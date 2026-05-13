/**
 * Double opt-in: GET /.netlify/functions/confirm-subscription?token=...
 * Requires DATABASE_URL + sql/neon-email-confirmation.sql + pending row from submission-created.
 */
const crypto = require('crypto');
const { neon } = require('@neondatabase/serverless');
const {
  sendEmail,
  contactUserHtml,
  contactAdminHtml,
  whitepaperUserHtml,
} = require('./lib/transactional-email');

function siteOrigin() {
  return (process.env.URL || process.env.DEPLOY_PRIME_URL || 'https://coerentis.co').replace(/\/$/, '');
}

function hashToken(token) {
  return crypto.createHash('sha256').update(String(token), 'utf8').digest('hex');
}

function redirect(loc) {
  return { statusCode: 302, headers: { Location: loc }, body: '' };
}

exports.handler = async function confirmSubscription(event) {
  if (event.httpMethod !== 'GET') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }

  const qs = event.queryStringParameters || {};
  const token = qs.token;
  if (!token || String(token).length < 64) {
    return redirect(`${siteOrigin()}/thanks/contact/?error=invalid`);
  }

  const dbUrl = process.env.DATABASE_URL;
  if (!dbUrl) {
    return { statusCode: 503, body: 'Confirmation is not configured.' };
  }

  const tokenHash = hashToken(token);
  const sql = neon(dbUrl);

  try {
    const updated = await sql`
      UPDATE pending_form_confirmations
      SET confirmed_at = now()
      WHERE token_hash = ${tokenHash}
        AND confirmed_at IS NULL
        AND expires_at > now()
      RETURNING id, form_name, email, payload
    `;

    if (!updated.length) {
      const existing = await sql`
        SELECT form_name, confirmed_at
        FROM pending_form_confirmations
        WHERE token_hash = ${tokenHash}
        LIMIT 1
      `;
      if (existing.length && existing[0].confirmed_at) {
        const dest =
          existing[0].form_name === 'whitepaper'
            ? '/thanks/whitepaper/?verified=1'
            : '/thanks/?verified=1';
        return redirect(`${siteOrigin()}${dest}`);
      }
      const expired = await sql`
        SELECT 1 FROM pending_form_confirmations
        WHERE token_hash = ${tokenHash} AND expires_at <= now()
        LIMIT 1
      `;
      if (expired.length) {
        return redirect(`${siteOrigin()}/thanks/contact/?error=expired`);
      }
      return redirect(`${siteOrigin()}/thanks/contact/?error=invalid`);
    }

    const row = updated[0];
    const raw = row.payload && row.payload.raw ? row.payload.raw : row.payload;
    const fields = (row.payload && row.payload.fields) || {};

    try {
      await sql`INSERT INTO form_submissions (raw) VALUES (${JSON.stringify(raw)}::jsonb)`;
    } catch (archiveErr) {
      console.error('confirm-subscription: form_submissions insert failed', archiveErr.message || archiveErr);
    }

    const adminTo = process.env.NOTIFY_ADMIN_EMAIL || 'info@boonmind.io';
    try {
      if (row.form_name === 'contact') {
        await sendEmail({
          to: row.email,
          subject: 'We received your Coerentis application',
          html: contactUserHtml(fields),
        });
        await sendEmail({
          to: adminTo,
          subject: `[Coerentis] New application from ${row.email}`,
          html: contactAdminHtml(fields),
        });
      } else if (row.form_name === 'whitepaper') {
        await sendEmail({
          to: row.email,
          subject: 'Coerentis — brief request confirmed',
          html: whitepaperUserHtml(fields),
        });
        await sendEmail({
          to: adminTo,
          subject: `[Coerentis] Whitepaper request confirmed — ${row.email}`,
          html: contactAdminHtml(fields),
        });
      }
    } catch (mailErr) {
      console.error('confirm-subscription: post-confirm email failed', mailErr.message || mailErr);
    }

    const dest =
      row.form_name === 'whitepaper' ? '/thanks/whitepaper/?verified=1' : '/thanks/?verified=1';
    return redirect(`${siteOrigin()}${dest}`);
  } catch (e) {
    console.error('confirm-subscription', e.message || e);
    return redirect(`${siteOrigin()}/thanks/contact/?error=server`);
  }
};
