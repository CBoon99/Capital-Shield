/**
 * Netlify Forms — invoked automatically when a form is submitted (name must be submission-created).
 * If DATABASE_URL (Neon Postgres) is set in Netlify env, inserts a JSON copy of the payload.
 * Netlify dashboard submissions are unchanged; this is optional long-term storage.
 */
const { neon } = require('@neondatabase/serverless');

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

  const url = process.env.DATABASE_URL;
  if (!url) {
    console.log('submission-created: DATABASE_URL not set; skipping Neon insert');
    return { statusCode: 200, body: JSON.stringify({ ok: true, neon: false }) };
  }

  try {
    const sql = neon(url);
    const raw = JSON.stringify(parsed);
    await sql`INSERT INTO form_submissions (raw) VALUES (${raw}::jsonb)`;
    console.log('submission-created: stored in Neon');
  } catch (err) {
    console.error('submission-created: Neon insert failed', err.message || err);
  }

  return { statusCode: 200, body: JSON.stringify({ ok: true, neon: true }) };
};
