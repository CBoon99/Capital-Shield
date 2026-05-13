-- Double opt-in for Netlify Forms (contact + whitepaper). Run in Neon if DATABASE_URL is set.
-- submission-created inserts a row here first; user confirms via confirm-subscription function.

CREATE TABLE IF NOT EXISTS pending_form_confirmations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  token_hash text NOT NULL UNIQUE,
  form_name text NOT NULL,
  email text NOT NULL,
  payload jsonb NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  expires_at timestamptz NOT NULL,
  confirmed_at timestamptz
);

CREATE INDEX IF NOT EXISTS idx_pending_form_email
  ON pending_form_confirmations (email);

CREATE INDEX IF NOT EXISTS idx_pending_form_expires
  ON pending_form_confirmations (expires_at)
  WHERE confirmed_at IS NULL;
