CREATE TABLE IF NOT EXISTS token_info (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  token TEXT NOT NULL,
  platform TEXT NOT NULL,
  token_base_url TEXT NOT NULL,
  claimed_model TEXT NOT NULL,
  non_claimed_model TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_record (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  token_id INTEGER NOT NULL,
  audit_time TEXT NOT NULL,
  status TEXT NOT NULL,
  overall_conclusion TEXT,
  report_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(token_id) REFERENCES token_info(id)
);

CREATE TABLE IF NOT EXISTS audit_event (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  audit_id INTEGER NOT NULL,
  ts TEXT NOT NULL,
  event TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  FOREIGN KEY(audit_id) REFERENCES audit_record(id)
);
