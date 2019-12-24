-- Adding paydate to dps table and copy data from date column
ALTER TABLE dps ADD COLUMN paydate date NOT NULL DEFAULT now();
ALTER TABLE dps RENAME COLUMN id TO products_id;
ALTER TABLE dps RENAME COLUMN id_dps TO id;
UPDATE dps SET paydate = "date";
