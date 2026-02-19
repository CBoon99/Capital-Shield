"""
Stripe Billing Integration

Handles Stripe webhooks for subscription lifecycle management and API key provisioning.
"""
import os
import secrets
import stripe
from fastapi import APIRouter, Request, HTTPException, Header, status
from typing import Optional
from app.core.config import (
    STRIPE_SECRET_KEY, 
    STRIPE_WEBHOOK_SECRET,
    TIER_LIMITS,
    API_KEYS
)
from app.db.usage import init_database
from app.core.logging import setup_logging

router = APIRouter()
logger = setup_logging()

# Initialize Stripe if key is provided
if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY
else:
    logger.warning("STRIPE_SECRET_KEY not configured. Billing features will be disabled.")


def generate_api_key() -> str:
    """Generate a secure API key"""
    return f"cs_{secrets.token_urlsafe(32)}"


def create_api_key_for_subscription(stripe_customer_id: str, tier: str) -> str:
    """
    Create an API key for a Stripe subscription
    
    Args:
        stripe_customer_id: Stripe customer ID
        tier: Tier name (starter, professional, enterprise)
    
    Returns:
        Generated API key
    """
    api_key = generate_api_key()
    
    # In production, this would be stored in a database
    # For now, we'll add it to the in-memory API_KEYS dict
    API_KEYS[api_key] = {
        "tier": tier,
        "name": f"{tier.title()} Subscription",
        "stripe_customer_id": stripe_customer_id,
        "rate_limit": TIER_LIMITS.get(tier, {}).get("daily_calls", 10000)
    }
    
    logger.info(f"Created API key for customer {stripe_customer_id}, tier {tier}")
    return api_key


@router.post("/billing/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None, alias="stripe-signature")
):
    """
    Handle Stripe webhook events
    
    Processes:
    - customer.subscription.created
    - customer.subscription.updated
    - customer.subscription.deleted
    - invoice.payment_succeeded
    - invoice.payment_failed
    """
    if not STRIPE_SECRET_KEY or not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe webhooks not configured"
        )
    
    payload = await request.body()
    
    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload"
        )
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature"
        )
    
    event_type = event['type']
    event_data = event['data']['object']
    
    logger.info(f"Received Stripe webhook: {event_type}")
    
    # Handle different event types
    if event_type == 'customer.subscription.created':
        handle_subscription_created(event_data)
    elif event_type == 'customer.subscription.updated':
        handle_subscription_updated(event_data)
    elif event_type == 'customer.subscription.deleted':
        handle_subscription_deleted(event_data)
    elif event_type == 'invoice.payment_succeeded':
        handle_payment_succeeded(event_data)
    elif event_type == 'invoice.payment_failed':
        handle_payment_failed(event_data)
    else:
        logger.info(f"Unhandled event type: {event_type}")
    
    return {"status": "success"}


def handle_subscription_created(subscription_data: dict):
    """Handle new subscription creation"""
    customer_id = subscription_data.get('customer')
    subscription_id = subscription_data.get('id')
    price_id = subscription_data.get('items', {}).get('data', [{}])[0].get('price', {}).get('id')
    
    # Map Stripe price IDs to tiers (would be configured in Stripe dashboard)
    # For now, use metadata or price lookup
    tier = subscription_data.get('metadata', {}).get('tier', 'starter')
    
    # Create API key for this subscription
    api_key = create_api_key_for_subscription(customer_id, tier)
    
    # Store subscription info (in production, use database)
    logger.info(f"Subscription created: {subscription_id}, tier: {tier}, API key: {api_key[:20]}...")


def handle_subscription_updated(subscription_data: dict):
    """Handle subscription updates (tier changes, etc.)"""
    customer_id = subscription_data.get('customer')
    subscription_id = subscription_data.get('id')
    status = subscription_data.get('status')
    
    # Update tier if subscription changed
    tier = subscription_data.get('metadata', {}).get('tier', 'starter')
    
    # Find and update API key tier
    for api_key, key_info in API_KEYS.items():
        if key_info.get('stripe_customer_id') == customer_id:
            key_info['tier'] = tier
            key_info['rate_limit'] = TIER_LIMITS.get(tier, {}).get('daily_calls', 10000)
            logger.info(f"Updated subscription {subscription_id} to tier {tier}")
            break


def handle_subscription_deleted(subscription_data: dict):
    """Handle subscription cancellation"""
    customer_id = subscription_data.get('customer')
    subscription_id = subscription_data.get('id')
    
    # Disable API keys for this customer
    # In production, mark as inactive rather than deleting
    keys_to_remove = []
    for api_key, key_info in API_KEYS.items():
        if key_info.get('stripe_customer_id') == customer_id:
            keys_to_remove.append(api_key)
    
    for api_key in keys_to_remove:
        # Mark as inactive rather than deleting
        API_KEYS[api_key]['tier'] = 'inactive'
        logger.info(f"Deactivated API key for cancelled subscription {subscription_id}")


def handle_payment_succeeded(invoice_data: dict):
    """Handle successful payment"""
    customer_id = invoice_data.get('customer')
    subscription_id = invoice_data.get('subscription')
    
    logger.info(f"Payment succeeded for customer {customer_id}, subscription {subscription_id}")
    
    # Ensure subscription is active
    if subscription_id:
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            if subscription.status == 'active':
                # Reactivate API keys if they were suspended
                for api_key, key_info in API_KEYS.items():
                    if key_info.get('stripe_customer_id') == customer_id:
                        if key_info.get('tier') == 'inactive':
                            # Restore tier from subscription metadata
                            tier = subscription.metadata.get('tier', 'starter')
                            key_info['tier'] = tier
                            key_info['rate_limit'] = TIER_LIMITS.get(tier, {}).get('daily_calls', 10000)
                            logger.info(f"Reactivated API key after payment")
        except Exception as e:
            logger.error(f"Error retrieving subscription: {e}")


def handle_payment_failed(invoice_data: dict):
    """Handle failed payment"""
    customer_id = invoice_data.get('customer')
    subscription_id = invoice_data.get('subscription')
    
    logger.warning(f"Payment failed for customer {customer_id}, subscription {subscription_id}")
    
    # Optionally suspend API access after multiple failures
    # For now, just log the failure


@router.get("/billing/usage/{api_key}")
async def get_usage_stats(api_key: str):
    """
    Get usage statistics for an API key
    
    Returns usage stats for dashboard display
    """
    from app.db.usage import get_usage_stats
    
    if api_key not in API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    key_info = API_KEYS[api_key]
    tier = key_info.get('tier', 'starter')
    tier_config = TIER_LIMITS.get(tier, {})
    
    usage_stats = get_usage_stats(api_key)
    
    return {
        "api_key": api_key[:20] + "...",  # Partial key for display
        "tier": tier,
        "daily_limit": tier_config.get('daily_calls'),
        "usage": usage_stats,
        "overage_rate": tier_config.get('overage_rate_gbp', 0.0)
    }


# Initialize database on import
init_database()
