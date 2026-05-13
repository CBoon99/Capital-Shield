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

  if (stripeEvent.type === 'checkout.session.completed') {
    try {
      const session = stripeEvent.data.object;
      const email =
        (session.customer_details && session.customer_details.email) ||
        session.customer_email;
      const planKey =
        (session.metadata && session.metadata.coerentis_plan) || '';
      if (email && process.env.RESEND_API_KEY) {
        const { sendEmail, stripeWelcomeHtml, planLabelFromKey } = require('./lib/transactional-email');
        await sendEmail({
          to: email,
          subject: 'Coerentis — payment received, next steps',
          html: stripeWelcomeHtml(planLabelFromKey(planKey)),
        });
        console.log('stripe-webhook: welcome email queued for', email);
      }
    } catch (e) {
      console.error('stripe-webhook: welcome email failed', e.message || e);
    }
  }

  return {
    statusCode: 200,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ received: true }),
  };
};
