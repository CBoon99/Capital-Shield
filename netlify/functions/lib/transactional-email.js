/**
 * Transactional email via Resend (HTTPS TLS to api.resend.com).
 * Env: RESEND_API_KEY, RESEND_FROM_EMAIL (e.g. "Coerentis <updates@yourdomain>").
 * Optional: NOTIFY_ADMIN_EMAIL — receives a copy of contact applications.
 */

const RESEND_API = 'https://api.resend.com/emails';

function layout(mainHtml) {
  return `<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width"></head>
<body style="margin:0;font-family:Inter,Segoe UI,Helvetica,Arial,sans-serif;background:#071225;color:#EAF2FF;">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#071225;padding:24px 12px;">
<tr><td align="center">
  <table role="presentation" width="560" cellspacing="0" cellpadding="0" style="max-width:560px;background:#0B1B33;border:1px solid rgba(46,168,255,0.25);border-radius:12px;overflow:hidden;">
    <tr><td style="padding:20px 24px;background:linear-gradient(90deg,rgba(46,168,255,0.15),rgba(124,92,255,0.12));border-bottom:1px solid rgba(46,168,255,0.2);">
      <span style="font-size:18px;font-weight:700;color:#2EA8FF;">Coerentis</span>
      <span style="color:rgba(234,242,255,0.6);font-size:13px;display:block;margin-top:4px;">BoonMind suite · Risk-first infrastructure</span>
    </td></tr>
    <tr><td style="padding:24px;font-size:15px;line-height:1.6;color:rgba(234,242,255,0.88);">
      ${mainHtml}
    </td></tr>
    <tr><td style="padding:16px 24px 20px;font-size:11px;line-height:1.5;color:rgba(234,242,255,0.45);border-top:1px solid rgba(120,170,255,0.15);">
      Coerentis™ · Patent pending. Not investment or legal advice.
      <br/>Questions: <a href="mailto:info@boonmind.io" style="color:#2EA8FF;">info@boonmind.io</a>
    </td></tr>
  </table>
</td></tr></table></body></html>`;
}

async function sendEmail({ to, subject, html, bcc }) {
  const key = process.env.RESEND_API_KEY;
  if (!key) {
    console.log('transactional-email: RESEND_API_KEY not set; skip send');
    return { skipped: true };
  }
  if (!to || !subject || !html) {
    throw new Error('sendEmail: missing to, subject, or html');
  }

  const from = process.env.RESEND_FROM_EMAIL || 'Coerentis <onboarding@resend.dev>';

  const body = { from, to: Array.isArray(to) ? to : [to], subject, html };
  if (bcc && bcc.length) body.bcc = bcc;

  const res = await fetch(RESEND_API, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${key}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });

  const text = await res.text();
  if (!res.ok) {
    console.error('Resend error', res.status, text);
    throw new Error(`Resend ${res.status}: ${text.slice(0, 400)}`);
  }
  return { ok: true };
}

function flattenFormFields(raw) {
  const out = {};
  function merge(obj) {
    if (!obj || typeof obj !== 'object') return;
    for (const [k, v] of Object.entries(obj)) {
      if (v != null && typeof v !== 'object') out[k] = String(v);
    }
  }
  merge(raw);
  if (raw.payload) {
    merge(raw.payload);
    merge(raw.payload.data);
    merge(raw.payload.human_fields);
    if (Array.isArray(raw.payload.ordered_human_fields)) {
      for (const row of raw.payload.ordered_human_fields) {
        if (row && row.name != null && row.value != null) out[row.name] = String(row.value);
      }
    }
  }
  merge(raw.data);
  merge(raw.human_fields);
  return out;
}

function findEmail(fields) {
  for (const [k, v] of Object.entries(fields)) {
    if (typeof v !== 'string') continue;
    const l = k.toLowerCase();
    if (l === 'email' || l.includes('email')) return v.trim();
  }
  return null;
}

function pleaseConfirmHtml({ name, confirmUrl, purpose }) {
  const purposeText =
    purpose === 'whitepaper'
      ? 'complete your methodology brief request and optional updates'
      : 'submit your Coerentis application to our team';
  const main = `
    <p style="margin:0 0 16px;">Hi ${escapeHtml(name)},</p>
    <p style="margin:0 0 16px;">Thanks for getting in touch. To protect your inbox and reduce spam, please <strong>confirm this email address</strong> so we can ${purposeText}.</p>
    <p style="margin:0 0 24px;text-align:center;">
      <a href="${escapeAttr(confirmUrl)}" style="display:inline-block;padding:14px 26px;background:#2EA8FF;color:#071225;font-weight:700;border-radius:10px;text-decoration:none;font-size:15px;">Confirm email address</a>
    </p>
    <p style="margin:0 0 12px;font-size:13px;color:rgba(234,242,255,0.55);">Or paste this link into your browser:</p>
    <p style="margin:0 0 20px;font-size:12px;word-break:break-all;color:rgba(124,207,255,0.85);">${escapeHtml(confirmUrl)}</p>
    <p style="margin:0;font-size:13px;color:rgba(234,242,255,0.55);">This link expires in <strong>72 hours</strong>. If you did not use the Coerentis site, you can ignore this message.</p>
  `;
  return layout(main);
}

function escapeAttr(s) {
  return escapeHtml(s).replace(/'/g, '&#39;');
}

function contactUserHtml(fields) {
  const name = fields.name || fields.Name || 'there';
  const tier = fields.tier || fields['Which tier are you interested in?'] || '';
  const main = `
    <p style="margin:0 0 16px;">Hi ${escapeHtml(name)},</p>
    <p style="margin:0 0 16px;">Thanks for applying to <strong>Coerentis</strong>. We’ve received your request${tier ? ` (${escapeHtml(tier)})` : ''}.</p>
    <p style="margin:0 0 16px;">We typically respond within <strong>48 hours</strong> at this email address. If your note is urgent, reply and mention “priority” in the subject line.</p>
    <p style="margin:0 0 8px;">Useful links while you wait:</p>
    <ul style="margin:8px 0;padding-left:20px;color:rgba(234,242,255,0.8);">
      <li><a href="https://coerentis.co/integration.html" style="color:#2EA8FF;">Integration guide</a></li>
      <li><a href="https://coerentis.co/dashboard" style="color:#2EA8FF;">Operator dashboard</a> (connect your API origin and key)</li>
    </ul>
    <p style="margin:16px 0 0;font-size:13px;color:rgba(234,242,255,0.55);">This message confirms receipt only — not an acceptance or contract. Coerentis™ · patent pending.</p>
  `;
  return layout(main);
}

function contactAdminHtml(fields) {
  const rows = Object.entries(fields)
    .filter(([k]) => k !== 'bot-field' && !k.toLowerCase().includes('password'))
    .map(([k, v]) => `<tr><td style="padding:6px 8px;border-bottom:1px solid rgba(120,170,255,0.12);color:#7ccfff;">${escapeHtml(k)}</td><td style="padding:6px 8px;border-bottom:1px solid rgba(120,170,255,0.12);">${escapeHtml(v)}</td></tr>`)
    .join('');
  const main = `
    <p style="margin:0 0 12px;"><strong>New Coerentis contact / application</strong></p>
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="font-size:14px;">${rows || '<tr><td>No fields</td></tr>'}</table>
  `;
  return layout(main);
}

function whitepaperUserHtml(fields) {
  const name = fields.name || fields.Name || 'there';
  const main = `
    <p style="margin:0 0 16px;">Hi ${escapeHtml(name)},</p>
    <p style="margin:0 0 16px;">Your email is <strong>confirmed</strong>. Thanks for requesting the Coerentis methodology brief and related updates.</p>
    <p style="margin:0 0 16px;">We’ll follow up by email. You can also download the sample report from the brief page anytime.</p>
    <p style="margin:16px 0 0;font-size:13px;color:rgba(234,242,255,0.55);">Informational only — not investment advice.</p>
  `;
  return layout(main);
}

function stripeWelcomeHtml(planLabel) {
  const main = `
    <p style="margin:0 0 16px;">Thank you for your Coerentis checkout.</p>
    <p style="margin:0 0 16px;">Your purchase: <strong>${escapeHtml(planLabel || 'Coerentis')}</strong>. You’ll receive a receipt from <strong>Stripe</strong>.</p>
    <p style="margin:0 0 12px;">Next steps:</p>
    <ul style="margin:8px 0;padding-left:20px;">
      <li><a href="https://coerentis.co/integration.html" style="color:#2EA8FF;">Integration guide</a></li>
      <li><a href="https://coerentis.co/dashboard" style="color:#2EA8FF;">Dashboard</a> — connect your controlled beta API base URL and API key</li>
      <li>Questions: <a href="mailto:info@boonmind.io" style="color:#2EA8FF;">info@boonmind.io</a></li>
    </ul>
    <p style="margin:16px 0 0;font-size:13px;color:rgba(234,242,255,0.55);">Rights and deliverables follow your order or SOW + Stripe’s terms. Coerentis™ · patent pending.</p>
  `;
  return layout(main);
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function planLabelFromKey(key) {
  const map = {
    'audit-monthly': 'Licensed — Audit (monthly)',
    'audit-annual': 'Licensed — Audit (annual)',
    'simulation-monthly': 'Simulation add-on (monthly)',
    'simulation-onetime': 'Simulation add-on (one-time)',
    'enterprise-deposit': 'Enterprise — scoping deposit',
  };
  return map[key] || key || 'Coerentis';
}

module.exports = {
  sendEmail,
  flattenFormFields,
  findEmail,
  pleaseConfirmHtml,
  contactUserHtml,
  contactAdminHtml,
  whitepaperUserHtml,
  stripeWelcomeHtml,
  planLabelFromKey,
};
