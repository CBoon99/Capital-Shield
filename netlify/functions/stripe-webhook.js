/**
 * Stripe webhooks — verify signature and acknowledge events (extend for provisioning, CRM, etc.).
 * Env: STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET (from Stripe Dashboard → Developers → Webhooks)
 * Endpoint URL: https://YOUR_SITE/.netlify/functions/stripe-webhook
 */
const Stripe = require('stripe');

exports.handler = async function stripeWebhook(event) {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method not allowed' };
  }

  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;
  const secretKey = process.env.STRIPE_SECRET_KEY;

  if (!webhookSecret || !secretKey) {
    console.warn('stripe-webhook: STRIPE_WEBHOOK_SECRET or STRIPE_SECRET_KEY missing');
    return { statusCode: 503, body: 'Webhook not configured' };
  }

  const sig =
    event.headers['stripe-signature'] ||
    event.headers['Stripe-Signature'] ||
    event.headers['STRIPE-SIGNATURE'];

  if (!sig) {
    return { statusCode: 400, body: 'Missing stripe-signature' };
  }

  let rawBody = event.body || '';
  if (event.isBase64Encoded && typeof rawBody === 'string') {
    rawBody = Buffer.from(rawBody, 'base64').toString('utf8');
  }

  const stripe = new Stripe(secretKey);

  let stripeEvent;
  try {
    stripeEvent = stripe.webhooks.constructEvent(rawBody, sig, webhookSecret);
  } catch (err) {
    console.error('stripe-webhook verify', err.message);
    return { statusCode: 400, body: `Webhook Error: ${err.message}` };
  }

  console.log('stripe-webhook', stripeEvent.type, stripeEvent.id);

  return {
    statusCode: 200,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ received: true }),
  };
};
