/**
 * Stripe Checkout — subscriptions + one-time payments for Coerentis SKUs.
 *
 * Subscriptions: audit-monthly, audit-annual, simulation-monthly
 * One-time: simulation-onetime, enterprise-deposit (scoping / engagement deposit — SOW still governs)
 *
 * Env:
 *   STRIPE_SECRET_KEY (required)
 *   STRIPE_PRICE_AUDIT_MONTHLY, STRIPE_PRICE_AUDIT_ANNUAL
 *   STRIPE_PRICE_SIMULATION_MONTHLY, STRIPE_PRICE_SIMULATION_ONETIME
 *   STRIPE_PRICE_ENTERPRISE_DEPOSIT
 * Optional: STRIPE_ENABLE_AUTOMATIC_TAX=true (Stripe Tax)
 *
 * Netlify: URL / DEPLOY_PRIME_URL for redirect origins.
 */
const Stripe = require('stripe');

/** @type {Record<string, { mode: 'subscription' | 'payment', envKey: string }>} */
const PLAN_CONFIG = {
  'audit-monthly': { mode: 'subscription', envKey: 'STRIPE_PRICE_AUDIT_MONTHLY' },
  'audit-annual': { mode: 'subscription', envKey: 'STRIPE_PRICE_AUDIT_ANNUAL' },
  'simulation-monthly': { mode: 'subscription', envKey: 'STRIPE_PRICE_SIMULATION_MONTHLY' },
  'simulation-onetime': { mode: 'payment', envKey: 'STRIPE_PRICE_SIMULATION_ONETIME' },
  'enterprise-deposit': { mode: 'payment', envKey: 'STRIPE_PRICE_ENTERPRISE_DEPOSIT' },
};

function jsonHeaders() {
  return { 'Content-Type': 'application/json' };
}

function getPriceId(plan) {
  const cfg = PLAN_CONFIG[plan];
  if (!cfg) return null;
  return process.env[cfg.envKey];
}

exports.handler = async function createCheckoutSession(event) {
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 204,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
      },
      body: '',
    };
  }

  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, headers: jsonHeaders(), body: JSON.stringify({ error: 'Method not allowed' }) };
  }

  const secret = process.env.STRIPE_SECRET_KEY;
  if (!secret || (!secret.startsWith('sk_live_') && !secret.startsWith('sk_test_'))) {
    return {
      statusCode: 503,
      headers: jsonHeaders(),
      body: JSON.stringify({ error: 'Billing is not configured. Set STRIPE_SECRET_KEY in Netlify.' }),
    };
  }

  let body;
  try {
    body = JSON.parse(event.body || '{}');
  } catch (e) {
    return { statusCode: 400, headers: jsonHeaders(), body: JSON.stringify({ error: 'Invalid JSON' }) };
  }

  const plan = body.plan;
  const cfg = PLAN_CONFIG[plan];
  const priceId = getPriceId(plan);

  if (!cfg || !priceId || typeof priceId !== 'string' || !priceId.startsWith('price_')) {
    return {
      statusCode: 400,
      headers: jsonHeaders(),
      body: JSON.stringify({
        error:
          'Unknown plan or missing Stripe Price ID. Set env for this SKU (e.g. STRIPE_PRICE_SIMULATION_MONTHLY).',
      }),
    };
  }

  const origin = (process.env.URL || process.env.DEPLOY_PRIME_URL || 'https://coerentis.co').replace(/\/$/, '');
  const stripe = new Stripe(secret);

  try {
    /** @type {Record<string, unknown>} */
    const params = {
      mode: cfg.mode,
      line_items: [{ price: priceId, quantity: 1 }],
      success_url: `${origin}/thanks/stripe/?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${origin}/#pricing`,
      allow_promotion_codes: true,
      billing_address_collection: 'required',
      tax_id_collection: { enabled: true },
      metadata: { coerentis_plan: plan },
    };

    if (cfg.mode === 'subscription') {
      params.subscription_data = { metadata: { coerentis_plan: plan } };
    }

    if (process.env.STRIPE_ENABLE_AUTOMATIC_TAX === 'true') {
      params.automatic_tax = { enabled: true };
    }

    const session = await stripe.checkout.sessions.create(params);

    return {
      statusCode: 200,
      headers: jsonHeaders(),
      body: JSON.stringify({ url: session.url }),
    };
  } catch (err) {
    console.error('create-checkout-session', err.message || err);
    return {
      statusCode: 500,
      headers: jsonHeaders(),
      body: JSON.stringify({
        error: 'Could not start checkout. Try again or email info@boonmind.io.',
      }),
    };
  }
};
