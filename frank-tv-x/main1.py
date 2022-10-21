import logging
import requests
import sqlite3
import time
import tweepy
from decouple import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

class Tweet():
    def __init__(self, id, text, videoIdTW, videoIdYT, isTheFirstOne , isTheLastOne):
        self.id = id
        self.text = text
        self.videoIdTW = videoIdTW
        self.videoIdYT = videoIdYT
        self.isTheFirstOne = isTheFirstOne
        self.isTheLastOne = isTheLastOne

class DbData():
    def __init__(self, tweetNumber, lastTweetTimestamp, tweetToReplyId):
        self.tweetNumber = tweetNumber
        self.lastTweetTimestamp = lastTweetTimestamp
        self.tweetToReplyId = tweetToReplyId

class FrankTvBot(tweepy.StreamListener):
    def __init__(self, api):
        logger.info(f"\n--- Initializing app ---\n")
        self.api = api
        self.me = api.me()
        tweet = f"https://twitter.com/FrankSuarezTv/status/video/1"
        result = self.api.update_status(tweet)
        logger.info(f"--- Sent tweet {tweet} ---")
        logger.info(f"--- Result: {result} ---")
        logger.info(f"--- Result ID: {result.id} ---")

        time.sleep(10)
        try:
            result1 = self.api.update_status(status="Response 123", in_reply_to_status_id=result.id, auto_populate_reply_metadata=True)
            logger.info(f"--- Result1: {result1} ---")
            logger.info(f"--- Result1 ID: {result1.id} ---")
        except Exception as e:
            logger.info(e)

        time.sleep(10)
        try:
            result2 = self.api.update_status(status="Response 456", in_reply_to_status_id=1582786847402782720, auto_populate_reply_metadata=True)
            logger.info(f"--- Result2: {result2} ---")
            logger.info(f"--- Result2 ID: {result2.id} ---")
        except Exception as e:
            logger.info(e)

    def on_status(self, tweet):
        print(tweet)

    def on_limit(self, status):
        logger.error(f"--- Rate Limit Exceeded, Sleep for 2 Mins: {status}")
        time.sleep(2 * 60)
        return True

    def on_error(self, status):
        logger.error(f"\n--- ERROR: {status} ---\n")

def main():
    keywords = ['FrankSuarezTv']
    consumer_key = config('api_public')
    consumer_secret = config('api_secret')
    access_token = config('token_public')
    access_token_secret = config('token_secret')
    try:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        try:
            api.verify_credentials()
        except Exception as e:
            logger.error("--- Error creating API", exc_info=True)
            raise e
        logger.info("--- API created")
        tweets_listener = FrankTvBot(api)
        stream = tweepy.Stream(api.auth, tweets_listener, is_async=True)
        stream.filter(track=keywords, languages=['es', 'en'])
    except Exception as e:
        logger.error(f"\n--- App failed ---\n {e}")

if __name__ == "__main__":
    main()
