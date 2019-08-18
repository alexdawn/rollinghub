INSERT INTO "user" (email, nickname, password)
VALUES
  ('test@test.com', 'testman', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f'),
  ('other@test.com', 'oboe', 'pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79');

INSERT INTO model (
  title, description, author_id, created, model_type,
  thumbnail_name, thumbnail)
VALUES
  ('test title',
   'test body',
   1,
   '1900-01-01 00:00:00',
   'locomotive'::model_type,
   'foo.jpg',
   'fakeimage'::bytea);
