-- Login sessions (pi-common auth). The Python version kept them in NiceGUI's file storage, so users log in
-- once more after the cutover; passwords are unchanged.
-- Rollback: DROP TABLE auth_sessions;

CREATE TABLE auth_sessions (
    token_hash varchar(64) PRIMARY KEY,
    user_id integer NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    csrf_token varchar(64) NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    expires_at timestamptz NOT NULL
);
CREATE INDEX auth_sessions_user_id_idx ON auth_sessions (user_id);
