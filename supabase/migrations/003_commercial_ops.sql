create table if not exists payment_methods (
  id uuid primary key default uuid_generate_v4(),
  organization_id uuid not null references organizations(id) on delete cascade,
  provider text not null default 'stripe',
  provider_customer_id text,
  provider_payment_method_id text,
  brand text,
  last4 text,
  exp_month integer,
  exp_year integer,
  is_default boolean not null default false,
  created_at timestamptz not null default now()
);

create table if not exists invoices (
  id uuid primary key default uuid_generate_v4(),
  organization_id uuid not null references organizations(id) on delete cascade,
  provider text not null default 'stripe',
  external_invoice_id text,
  status text not null default 'draft',
  amount numeric(12,2) not null default 0,
  currency text not null default 'usd',
  seats integer not null default 0,
  line_items jsonb not null default '[]'::jsonb,
  hosted_invoice_url text,
  due_at timestamptz,
  paid_at timestamptz,
  created_at timestamptz not null default now()
);

create index if not exists idx_invoices_org_created on invoices(organization_id, created_at desc);

create table if not exists seat_invites (
  id uuid primary key default uuid_generate_v4(),
  organization_id uuid not null references organizations(id) on delete cascade,
  email text not null,
  role text not null default 'member',
  status text not null default 'pending',
  invite_token text not null unique,
  invited_by_user_id uuid references users(id) on delete set null,
  expires_at timestamptz,
  created_at timestamptz not null default now()
);

create index if not exists idx_seat_invites_org_created on seat_invites(organization_id, created_at desc);

create table if not exists company_sources (
  id uuid primary key default uuid_generate_v4(),
  company_id uuid not null references companies(id) on delete cascade,
  source_type text not null,
  source_key text not null,
  source_url text,
  confidence numeric(5,2) not null default 0,
  metadata jsonb not null default '{}'::jsonb,
  discovered_at timestamptz not null default now(),
  unique (company_id, source_type, source_key)
);

create index if not exists idx_company_sources_company_id on company_sources(company_id);
