create table if not exists public.access_requests (
  id uuid primary key default gen_random_uuid(),
  machine_id text not null,
  user_ip text not null,
  hostname text,
  status text not null default 'pending' check (status in ('pending','approved','denied')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Index for fast polling by machine_id
create index if not exists access_requests_machine_id_idx on public.access_requests(machine_id);
create index if not exists access_requests_status_idx on public.access_requests(status);

-- Auto-update updated_at
create or replace function public.set_updated_at()
returns trigger language plpgsql as $$
begin new.updated_at = now(); return new; end;
$$;

drop trigger if exists set_access_requests_updated_at on public.access_requests;
create trigger set_access_requests_updated_at
  before update on public.access_requests
  for each row execute function public.set_updated_at();

-- Allow anonymous insert (eTool submits without auth) and read/update (APK uses anon key)
alter table public.access_requests enable row level security;

create policy "anon insert" on public.access_requests for insert to anon with check (true);
create policy "anon select" on public.access_requests for select to anon using (true);
create policy "anon update status" on public.access_requests for update to anon
  using (true) with check (status in ('approved','denied'));
