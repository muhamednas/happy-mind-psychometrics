-- ---------------------------------------------------------------------------
-- Portable RLS isolation assertions (run with psql -v ON_ERROR_STOP=1).
-- Any failed assertion raises an exception, which fails the run.
-- Prereqs: _local_shim.sql + all non-storage migrations applied to a fresh DB.
-- ---------------------------------------------------------------------------

-- Seed two tenants (as the privileged bootstrap role).
insert into public.corporates (id, name, slug) values
  ('22222222-2222-2222-2222-222222222222', 'Acme', 'acme'),
  ('33333333-3333-3333-3333-333333333333', 'Beta', 'beta');
insert into public.packages (id, corporate_id, title, access_code) values
  ('aaaaaaaa-0000-0000-0000-000000000001', '22222222-2222-2222-2222-222222222222', 'Acme Pkg', 'HM-AAAAAA-1'),
  ('bbbbbbbb-0000-0000-0000-000000000002', '33333333-3333-3333-3333-333333333333', 'Beta Pkg', 'HM-BBBBBB-2');

-- Act as an authenticated HR user of tenant A.
set role authenticated;
select set_config(
  'request.jwt.claims',
  '{"sub":"11111111-1111-1111-1111-111111111111","app_metadata":{"corporate_id":"22222222-2222-2222-2222-222222222222"}}',
  false
);

-- 1) SELECT isolation: tenant A sees only its own package.
do $$
begin
  if (select count(*) from public.packages) <> 1 then
    raise exception 'RLS SELECT: expected 1 visible package, got %', (select count(*) from public.packages);
  end if;
  if not exists (select 1 from public.packages where corporate_id = '22222222-2222-2222-2222-222222222222') then
    raise exception 'RLS SELECT: tenant A cannot see its own package';
  end if;
end $$;

-- 2) INSERT WITH CHECK: creating a row for another tenant is blocked.
do $$
begin
  begin
    insert into public.packages (corporate_id, title, access_code)
    values ('33333333-3333-3333-3333-333333333333', 'Cross', 'HM-CCCCCC-3');
    raise exception 'RLS INSERT: cross-tenant insert unexpectedly succeeded';
  exception
    when insufficient_privilege then null;  -- expected: WITH CHECK violation
  end;
end $$;

-- 3) UPDATE isolation: updating another tenant's row affects 0 rows.
do $$
declare n int;
begin
  update public.packages set title = 'HACKED'
   where id = 'bbbbbbbb-0000-0000-0000-000000000002';
  get diagnostics n = row_count;
  if n <> 0 then
    raise exception 'RLS UPDATE: cross-tenant update affected % rows (expected 0)', n;
  end if;
end $$;

reset role;

-- 4) service_role bypasses RLS: sees both tenants' packages.
set role service_role;
do $$
begin
  if (select count(*) from public.packages) < 2 then
    raise exception 'service_role should see all packages, got %', (select count(*) from public.packages);
  end if;
end $$;
reset role;

select 'RLS assertions passed' as result;
