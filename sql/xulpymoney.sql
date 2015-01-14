DELETE FROM products WHERE id<=0;
UPDATE products SET active=true WHERE priorityhistorical[1]=3;
UPDATE products SET active=true WHERE priorityhistorical[1]=8;
ALTER SEQUENCE seq_conceptos START WITH 100 RESTART;
ALTER SEQUENCE seq_entidadesbancarias START WITH 4 RESTART;
ALTER SEQUENCE seq_cuentas START WITH 5 RESTART;
UPDATE globals set value=NULL where id_globals=6;
