-- SEQUENCES
CREATE SEQUENCE book_id_seq AS INT MINVALUE 1 MAXVALUE 999 START 1 NO CYCLE;

CREATE SEQUENCE author_id_seq AS INT MINVALUE 1 MAXVALUE 999 START 1 NO CYCLE;

CREATE SEQUENCE genre_id_seq AS INT MINVALUE 1 MAXVALUE 999 START 1 NO CYCLE;

CREATE SEQUENCE user_id_seq AS INT MINVALUE 1 MAXVALUE 999 START 1 NO CYCLE;
-- -- setval of the currentval = 1
-- SELECT setval('user_id_seq', 1)
-- -- setval of the nextval = 1
-- SELECT setval('user_id_seq', 1, false)
-- SELECT setval('genre_id_seq', 1, false)

CREATE SEQUENCE borrow_id_seq AS INT MINVALUE 1 MAXVALUE 999 START 1 NO CYCLE;

-- TABLES
SELECT * FROM public.user
SELECT * FROM public.genre
SELECT * FROM public.author


-- DELETE FROM public.genre
-- WHERE id = 'bk003'