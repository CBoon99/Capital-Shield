/**
 * Netlify Forms — name must be submission-created (automatic trigger).
 * Optional Neon: DATABASE_URL + sql/neon-form-submissions.sql + sql/neon-email-confirmation.sql
 * Optional email: RESEND_API_KEY, RESEND_FROM_EMAIL, NOTIFY_ADMIN_EMAIL
 *
 * Double opt-in (contact + whitepaper): when DATABASE_URL is set, stores only a pending row
 * and emails a confirm link. `form_submissions` is inserted in confirm-subscription after
 * the user verifies. If the pending insert or email fails, falls back to immediate emails
 * and archives the raw payload once.
 */
const crypto = require('crypto');
const { neon } = require('@neondatabase/serverless');
const {
  sendEmail,
  flattenFormFields,
  findEmail,
  pleaseConfirmHtml,
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

async function tryDoubleOptIn(sql, { formName, userEmail, fields, parsed }) {
  const token = crypto.randomBytes(32).toString('hex');
  const tokenHash = hashToken(token);
  const expiresAt = new Date(Date.now() + 72 * 60 * 60 * 1000).toISOString();
  const payload = { fields, raw: parsed };
  await sql`
    INSERT INTO pending_form_confirmations (token_hash, form_name, email, payload, expires_at)
    VALUES (${tokenHash}, ${formName}, ${userEmail}, ${JSON.stringify(payload)}::jsonb, ${expiresAt})
  `;
  try {
    const confirmUrl = `${siteOrigin()}/.netlify/functions/confirm-subscription?token=${encodeURIComponent(token)}`;
    const name = fields.name || fields.Name || 'there';
    const purpose = formName === 'whitepaper' ? 'whitepaper' : 'contact';
    const subject =
      formName === 'whitepaper'
        ? 'Confirm your email — Coerentis methodology brief'
        : 'Confirm your email — Coerentis application';
    await sendEmail({
      to: userEmail,
      subject,
      html: pleaseConfirmHtml({ name, confirmUrl, purpose }),
    });
  } catch (mailErr) {
    await sql`DELETE FROM pending_form_confirmations WHERE token_hash = ${tokenHash}`;
    throw mailErr;
  }
}

async function archiveRawSubmission(sql, parsed) {
  const raw = JSON.stringify(parsed);
  await sql`INSERT INTO form_submissions (raw) VALUES (${raw}::jsonb)`;
}

async function sendImmediate(formName, userEmail, fields, adminTo) {
  if (formName === 'contact') {
    await sendEmail({
      to: userEmail,
      subject: 'We received your Coerentis application',
      html: contactUserHtml(fields),
    });
    await sendEmail({
      to: adminTo,
      subject: `[Coerentis] New application from ${userEmail}`,
      html: contactAdminHtml(fields),
    });
  } else if (formName === 'whitepaper') {
    await sendEmail({
      to: userEmail,
      subject: 'Coerentis — brief request received',
      html: whitepaperUserHtml(fields),
    });
    await sendEmail({
      to: adminTo,
      subject: `[Coerentis] Whitepaper request from ${userEmail}`,
      html: contactAdminHtml(fields),
    });
  }
}

exports.handler = async function submissionCreatedHandler(event) {
  if (!event.body) {
    return { statusCode: 400, body: 'empty body' };
  }

  let parsed;
  try {
    parsed = JSON.parse(event.body);
  } catch (e) {
    console.error('submission-created: invalid JSON', e.message);
    return { statusCode: 400, body: 'invalid json' };
  }

  const fields = flattenFormFields(parsed);
  const formName = String(
    (parsed.payload && parsed.payload.form_name) ||
      parsed.form_name ||
      fields['form-name'] ||
      ''
  ).toLowerCase();

  const dbUrl = process.env.DATABASE_URL;
  const sql = dbUrl ? neon(dbUrl) : null;

  const adminTo = process.env.NOTIFY_ADMIN_EMAIL || 'info@boonmind.io';
  const userEmail = findEmail(fields);

  const shouldTryDoubleOptIn =
    sql &&
    userEmail &&
    (formName === 'contact' || formName === 'whitepaper') &&
    process.env.RESEND_API_KEY;

  if (sql && !shouldTryDoubleOptIn) {
    try {
      await archiveRawSubmission(sql, parsed);
      console.log('submission-created: stored raw submission in Neon');
    } catch (err) {
      console.error('submission-created: Neon form_submissions insert failed', err.message || err);
    }
  }

  try {
    if (shouldTryDoubleOptIn) {
      try {
        await tryDoubleOptIn(sql, { formName, userEmail, fields, parsed });
        console.log('submission-created: double opt-in pending for', formName, userEmail);
        return { statusCode: 200, body: JSON.stringify({ ok: true, pending_confirmation: true }) };
      } catch (pendingErr) {
        console.error(
          'submission-created: double opt-in failed, falling back to immediate mail',
          pendingErr.message || pendingErr
        );
        try {
          await archiveRawSubmission(sql, parsed);
        } catch (archiveErr) {
          console.error('submission-created: fallback archive failed', archiveErr.message || archiveErr);
        }
      }
    }

    if (!process.env.RESEND_API_KEY) {
      console.log('submission-created: RESEND_API_KEY not set; skip email');
      return { statusCode: 200, body: JSON.stringify({ ok: true }) };
    }

    if (formName === 'contact' && userEmail) {
      await sendImmediate('contact', userEmail, fields, adminTo);
      console.log('submission-created: contact emails sent (single-step)');
    } else if (formName === 'whitepaper' && userEmail) {
      await sendImmediate('whitepaper', userEmail, fields, adminTo);
      console.log('submission-created: whitepaper emails sent (single-step)');
    }
  } catch (mailErr) {
    console.error('submission-created: email failed', mailErr.message || mailErr);
  }

  return { statusCode: 200, body: JSON.stringify({ ok: true }) };
};
