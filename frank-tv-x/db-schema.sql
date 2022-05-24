db schema:
    tweetNumber: integer
    nextTweetTimestamp: integer
    tweetToReplyId: integer
c.execute('''CREATE TABLE frankData(id int, tweetNumber int)''')
c.execute("""INSERT INTO frankData (id, tweetNumber) VALUES (1, 1)""")
        