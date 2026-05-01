-- Run once in Neon (or any Postgres) if you set DATABASE_URL for Netlify form archiving.
-- Netlify still stores submissions in the dashboard; this table is an optional replica.

CREATE TABLE IF NOT EXISTS form_submissions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at timestamptz NOT NULL DEFAULT now(),
  raw jsonb NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_form_submissions_created
  ON form_submissions (created_at DESC);
