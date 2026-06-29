-- 1. Enable the pgvector extension for vector similarity search
create extension if not exists vector;

-- 2. Create the memories table
create table if not exists memories (
    id          text primary key,
    user_id     text not null,
    text        text not null,
    embedding   vector(384),
    tags        jsonb default '[]',
    importance  float default 0.5,
    timestamp   float not null,
    decay_days  int default 0
);

-- 3. Create an index for fast vector search
create index if not exists memories_embedding_idx
on memories using ivfflat (embedding vector_cosine_ops)
with (lists = 100);

-- 4. Create an index for fast filtering by user
create index if not exists memories_user_idx
on memories (user_id);

-- 5. Create the function for semantic recall (called by RPC from Python)
create or replace function match_memories(
    query_embedding vector(384),
    match_user_id   text,
    match_count     int default 5
)
returns table (
    id          text,
    user_id     text,
    text        text,
    tags        jsonb,
    importance  float,
    timestamp   float,
    decay_days  int,
    similarity  float
)
language sql stable
as $$
    select
        id,
        user_id,
        text,
        tags,
        importance,
        timestamp,
        decay_days,
        1 - (embedding <=> query_embedding) as similarity
    from memories
    where user_id = match_user_id
    order by embedding <=> query_embedding
    limit match_count;
$$;

-- 6. Setup Row Level Security (RLS)
-- By default, Supabase blocks all writes from the anon key. 
-- This policy allows all operations so retainr can read/write data.
alter table memories enable row level security;

create policy "allow all operations"
on memories for all
to anon
using (true)
with check (true);
