-- init.sql
CREATE TABLE files (
  id                serial PRIMARY KEY,
  file_name         varchar(80),
  file_content      BYTEA NOT NULL,
  created_at        DATE NOT NULL
)
