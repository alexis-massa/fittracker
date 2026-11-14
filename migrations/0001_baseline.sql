-- Baseline: the schema the Python version (python-final, v0.4.0) created at startup, unchanged.
-- On the live database this is recorded with `fittracker baseline`, never run (pi-infra APP_CONTRACT.md).
-- `just schema-check` proves it equals the live schema.

CREATE TABLE users (
    id serial PRIMARY KEY,
    username text NOT NULL,
    password_hash text NOT NULL,
    preferences jsonb NOT NULL DEFAULT '{}',
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX users_username_key ON users (lower(username));

-- One JSON document per row (see src/model.rs for the fields), owned by a user.
CREATE TABLE exercises (
    id serial PRIMARY KEY,
    doc jsonb NOT NULL,
    user_id integer REFERENCES users (id) ON DELETE CASCADE
);
CREATE INDEX exercises_user_id_idx ON exercises (user_id);

CREATE TABLE sessions (
    id serial PRIMARY KEY,
    doc jsonb NOT NULL,
    user_id integer REFERENCES users (id) ON DELETE CASCADE
);
CREATE INDEX sessions_user_id_idx ON sessions (user_id);
