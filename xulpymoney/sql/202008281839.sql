ALTER TABLE public.creditcards ALTER COLUMN active SET NOT NULL;
ALTER TABLE public.creditcards ALTER COLUMN active SET DEFAULT TRUE;
ALTER TABLE public.creditcards ALTER COLUMN deferred SET NOT NULL;
ALTER TABLE public.creditcards ALTER COLUMN deferred SET DEFAULT FALSE;
ALTER TABLE public.creditcards ALTER COLUMN name SET NOT NULL;
ALTER TABLE public.creditcards ALTER COLUMN accounts_id SET NOT NULL;
