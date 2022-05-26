BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "frankData" (
	"id"	INTEGER NOT NULL UNIQUE,
	"tweetNumber"	NUMERIC,
	"nextTweetTimestamp"	NUMERIC,
	"tweetToReplyId"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
COMMIT;