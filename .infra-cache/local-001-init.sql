create extension if not exists "uuid-ossp";

create table if not exists users (
  id uuid primary key default uuid_generate_v4(),
  email text unique not null,
  full_name text not null,
  role text not null default 'analyst',
  hashed_password text not null,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists companies (
  id uuid primary key default uuid_generate_v4(),
  name text not null,
  slug text unique not null,
  domain text,
  website text,
  industry text,
  subindustry text,
  city text,
  region text,
  country text,
  employee_range text,
  revenue_range text,
  rating numeric(3,2),
  reviews_count integer default 0,
  description text,
  ai_summary text,
  health_score numeric(5,2) default 0,
  growth_score numeric(5,2) default 0,
  opportunity_score numeric(5,2) default 0,
  enrichment jsonb not null default '{}'::jsonb,
  metadata jsonb not null default '{}'::jsonb,
  embedding vector(1536),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_companies_country on companies(country);
create index if not exists idx_companies_industry on companies(industry);
create index if not exists idx_companies_enrichment on companies using gin(enrichment);
create index if not exists idx_companies_metadata on companies using gin(metadata);

create table if not exists signals (
  id uuid primary key default uuid_generate_v4(),
  company_id uuid not null references companies(id) on delete cascade,
  type text not null,
  severity text not null,
  title text not null,
  description text not null,
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists idx_signals_company_id on signals(company_id);
create index if not exists idx_signals_type on signals(type);

create table if not exists opportunities (
  id uuid primary key default uuid_generate_v4(),
  company_id uuid not null references companies(id) on delete cascade,
  category text not null,
  title text not null,
  description text not null,
  confidence numeric(5,2) not null default 0,
  estimated_value numeric(12,2) default 0,
  status text not null default 'open',
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists idx_opportunities_company_id on opportunities(company_id);
create index if not exists idx_opportunities_category on opportunities(category);

create table if not exists relationships (
  id uuid primary key default uuid_generate_v4(),
  source_company_id uuid references companies(id) on delete cascade,
  target_company_id uuid references companies(id) on delete cascade,
  relationship_type text not null,
  weight numeric(5,2) default 0,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists crawl_jobs (
  id uuid primary key default uuid_generate_v4(),
  job_type text not null,
  status text not null default 'queued',
  seed jsonb not null default '{}'::jsonb,
  target_url text,
  attempts integer not null default 0,
  max_attempts integer not null default 5,
  priority integer not null default 100,
  last_error text,
  scheduled_at timestamptz not null default now(),
  started_at timestamptz,
  finished_at timestamptz,
  created_at timestamptz not null default now()
);

create index if not exists idx_crawl_jobs_status on crawl_jobs(status);
create index if not exists idx_crawl_jobs_scheduled_at on crawl_jobs(scheduled_at);

create table if not exists exports (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid references users(id) on delete set null,
  export_type text not null,
  filters jsonb not null default '{}'::jsonb,
  file_url text,
  status text not null default 'pending',
  created_at timestamptz not null default now()
);

create table if not exists logs (
  id uuid primary key default uuid_generate_v4(),
  level text not null,
  source text not null,
  message text not null,
  context jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists saved_leads (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid not null references users(id) on delete cascade,
  company_id uuid not null references companies(id) on delete cascade,
  notes text,
  created_at timestamptz not null default now(),
  unique (user_id, company_id)
);

create table if not exists insight_snapshots (
  id uuid primary key default uuid_generate_v4(),
  insight_type text not null,
  title text not null,
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);
