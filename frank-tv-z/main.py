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
        logger.info(f"--- Initializing app at {self.get_current_time()} ---")
        self.api = api
        self.me = api.me()
        self.timeToNextSerie = 60 * 60 * 19 - 6   # 19hs
        self.timeToSameSerie = 100
        self.data = None
        self.dbData = DbData(1, 0, 0)
        self.currentTweet = Tweet(1, "", 1, 1, True, True)
        self.launch_or_sleep()

    def get_current_timestamp(self):
        return int(round(time.time(), 0))

    def get_current_time(self):
        return time.asctime(time.localtime(time.time()))

    def update_params(self):
        logger.info(f"--- Updating params {self.get_current_time()} ---")
        id, tweetNumber, lastTweetTimestamp, tweetToReplyId = self.get_db_data()
        self.dbData.lastTweetTimestamp = lastTweetTimestamp
        self.dbData.tweetNumber = tweetNumber
        self.dbData.tweetToReplyId = tweetToReplyId
        if self.dbData.lastTweetTimestamp is None:
            self.dbData.lastTweetTimestamp = self.get_current_timestamp()
        if self.dbData.tweetNumber is None or self.dbData.tweetNumber == 0:
            self.dbData.tweetNumber = 1
        logger.info(f"--- Updated data from db: tweetNumber {self.dbData.tweetNumber}, lastTweetTimestamp {self.dbData.lastTweetTimestamp}, tweetToReplyId {self.dbData.tweetToReplyId} ---")
        data = self.get_storage()
        if data is not None:
            self.data = data
        self.currentTweet.id = self.dbData.tweetNumber
        current = self.data['objects'][self.dbData.tweetNumber - 1]
        self.currentTweet.isTheFirstOne = current['isTheFirstOne']
        self.currentTweet.isTheLastOne = current['isTheLastOne']
        self.currentTweet.text = current['text']
        self.currentTweet.videoIdTW = current['videoIdTW']
        self.currentTweet.videoIdYT = current['videoIdYT']
        logger.info(f"--- Updated data from storage file: id {self.currentTweet.id}, isTheFirstOne {self.currentTweet.isTheFirstOne}, isTheLastOne {self.currentTweet.isTheLastOne}, text {self.currentTweet.text}, videoIdTW {self.currentTweet.videoIdTW}, videoIdYT {self.currentTweet.videoIdYT} ---")

    def get_db_data(self):
        conn = sqlite3.connect('frank.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM frankData''')
        result = cursor.fetchone()    # int, int, int, str, int
        cursor.close()
        return result

    def get_storage(self):
        try:
            url = config('storage_url')
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.exception(e)
            return None

    def launch_or_sleep(self):
        self.update_params()
        currentTimestamp = self.get_current_timestamp()
        if self.currentTweet.isTheFirstOne == True:
            remains = self.dbData.lastTweetTimestamp + self.timeToNextSerie - currentTimestamp
        else:
            remains = self.dbData.lastTweetTimestamp + self.timeToSameSerie - currentTimestamp
        if remains > 0:
            logger.info(f"--- It's NOT time, sleeping {remains} seconds to post {self.currentTweet.id} ({self.get_current_time()}) ---")
            time.sleep(remains)
            self.launch_or_sleep()
            return
        ################################################################
        if self.currentTweet.isTheFirstOne == False and (self.dbData.tweetToReplyId == 0 or self.dbData.tweetToReplyId == "0"):
            self.update_db(None)
            self.launch_or_sleep()
            return
        
        tweet = f"{self.currentTweet.text} https://twitter.com/FrankSuarezTv/status/{self.currentTweet.videoIdTW}/video/1"
        if self.currentTweet.isTheFirstOne == True:
            logger.info(f"--- Head tweet: sending tweet number {self.currentTweet.id}, {tweet} ({self.get_current_time()}) ---")
            result = self.api.update_status(tweet)
            self.update_db(None)
            if self.currentTweet.isTheLastOne == False:
                self.update_db(result.id)
            while self.currentTweet.isTheLastOne == False:
                time.sleep(self.timeToSameSerie)
                self.update_params()
                tweet = f"{self.currentTweet.text} https://twitter.com/FrankSuarezTv/status/{self.currentTweet.videoIdTW}/video/1"
                result = self.api.update_status(status=tweet, in_reply_to_status_id=result.id, auto_populate_reply_metadata=True)
                self.update_db(None)
                logger.info(f"--- Tweet reply: {self.currentTweet.id}, {tweet} ({self.get_current_time()}) ---")
                if self.currentTweet.isTheLastOne == False:
                    self.update_db(result.id)
        else:
            logger.info(f"--- Tweet reply: sending tweet number {self.currentTweet.id}, {tweet} ({self.get_current_time()}) ---")
            result = self.api.update_status(status=tweet, in_reply_to_status_id=self.dbData.tweetToReplyId, auto_populate_reply_metadata=True)
            self.update_db(None)
            if self.currentTweet.isTheLastOne == False:
                self.update_db(result.id)
            while self.currentTweet.isTheLastOne == False:
                time.sleep(self.timeToSameSerie)
                self.update_params()
                tweet = f"{self.currentTweet.text} https://twitter.com/FrankSuarezTv/status/{self.currentTweet.videoIdTW}/video/1"
                result = self.api.update_status(status=tweet, in_reply_to_status_id=result.id, auto_populate_reply_metadata=True)
                self.update_db(None)
                logger.info(f"--- Tweet reply: {self.currentTweet.id}, {tweet} ({self.get_current_time()}) ---")
                if self.currentTweet.isTheLastOne == False:
                    self.update_db(result.id)
        self.send_complete_video_tweet(result.id)
        self.update_db(0)
        logger.info("--- Done")
        self.launch_or_sleep()

    def update_db(self, tweetToReplyId):
        logger.info(f"--- Updating db ({self.get_current_time()}) ---")
        conn = sqlite3.connect('frank.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if tweetToReplyId is None:
            if self.dbData.tweetNumber != len(self.data['objects']):
                nextTweetNumber = self.dbData.tweetNumber + 1
            else:
                nextTweetNumber = 1
            lastTweetTimestamp = self.get_current_timestamp()
            logger.info(f"--- Saving next tweet number {nextTweetNumber} and last tweet timestamp {lastTweetTimestamp} in db ---")
            cursor.execute('''UPDATE frankData SET tweetNumber = ? WHERE id = ? ''', (nextTweetNumber, 1))
            cursor.execute('''UPDATE frankData SET lastTweetTimestamp = ? WHERE id = ? ''', (lastTweetTimestamp, 1))
        else:
            logger.info(f"--- Saving tweet to reply id {tweetToReplyId} in db ---")
            cursor.execute('''UPDATE frankData SET tweetToReplyId = ? WHERE id = ? ''', (tweetToReplyId, 1))
        conn.commit()
        cursor.close()

    def search_tweet(self, text):
        logger.info("--- Searching for:", text)
        if self.data == None or self.data['objects'] == None:
            logger.info("--- Exit")
            return
        for tweet in self.data['objects']:
            if tweet['text'] in text:
                logger.info(f"--- Tweet found: {tweet['text']}")
                return Tweet(tweet['id'], tweet['text'], tweet['videoIdTW'], tweet['videoIdYT'], tweet['isTheFirstOne'], tweet['isTheLastOne'])

    def send_complete_video_tweet(self, tweet_id):
        logger.info(f"--- Waiting {self.timeToSameSerie} seconds to send Complete Video URL...")
        time.sleep(self.timeToSameSerie)
        tweet = f"Video completo: https://youtu.be/{self.currentTweet.videoIdYT}"
        logger.info(f"--- Sending tweet {tweet} ({self.get_current_time()}) ---")
        self.api.update_status(status=tweet, in_reply_to_status_id=tweet_id, auto_populate_reply_metadata=True)
        logger.info("--- Done")

    def on_limit(self, status):
        logger.error(f"--- Rate Limit Exceeded, Sleep for 2 Mins: {status}")
        time.sleep(2 * 60)
        return True

    def on_error(self, status):
        logger.error(f"--- ERROR: {status} ---")

def main():
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
            logger.error("--- Error verifying credentials", exc_info=True)
            raise e
        logger.info("--- API created")
        tweets_listener = FrankTvBot(api)
        tweepy.Stream(api.auth, tweets_listener, is_async=True)
    except Exception as e:
        logger.error(f"--- App failed: {e} ---")

if __name__ == "__main__":
    main()
