-- Unlock keys for password-locked research PDFs.
-- Run in the Supabase SQL editor. Service role only (FastAPI).
-- Demo stores name/DOB and the plaintext unlock_key; production should minimize PII.

create table if not exists public.report_unlock_keys (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  catalog_key text not null,
  subject_name text not null,
  date_of_birth date not null,
  key_fingerprint text not null unique,
  unlock_key text not null,
  research_score numeric,
  disclaimer text not null
);

alter table public.report_unlock_keys enable row level security;

-- No policies for anon/authenticated: only the service role (bypasses RLS) can insert.

comment on table public.report_unlock_keys is
  'Generated PDF open-passwords for QureSense research score sheets. Not a clinical EHR.';
