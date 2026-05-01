create extension if not exists "pgcrypto";

create table if not exists public.inference_runs (
  id uuid primary key default gen_random_uuid(),
  run_name text not null,
  model_path text not null,
  source_path text not null,
  output_dir text not null,
  confidence numeric not null default 0.25,
  status text not null default 'completed',
  images_processed integer not null default 0,
  completed_at timestamptz,
  created_at timestamptz not null default now()
);

create table if not exists public.inference_images (
  id uuid primary key default gen_random_uuid(),
  run_id uuid not null references public.inference_runs(id) on delete cascade,
  original_path text not null,
  annotated_path text not null,
  annotated_object_path text not null,
  annotated_url text not null,
  box_count integer not null default 0,
  max_confidence numeric,
  width integer,
  height integer,
  created_at timestamptz not null default now()
);

create index if not exists inference_runs_created_at_idx on public.inference_runs (created_at desc);
create index if not exists inference_images_run_id_idx on public.inference_images (run_id);
create index if not exists inference_images_created_at_idx on public.inference_images (created_at desc);

insert into storage.buckets (id, name, public)
values ('annotated-outputs', 'annotated-outputs', true)
on conflict (id) do nothing;

