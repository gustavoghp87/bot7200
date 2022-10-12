import requests
import sqlite3
import time
import tweepy
from config import create_api
from config import get_storage_url

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
        print(f"\n--- Initializing app at {self.get_current_time()} ---\n")
        self.api = api
        self.me = api.me()
        self.timeToNextSerie = 60 * 60 * 8 - 6   # 7hs
        self.timeToSameSerie = 60
        self.data = None
        self.dbData = DbData(1, 0, 0)
        self.currentTweet = Tweet(1, "", 1, 1, True, True)
        self.launch_or_sleep()

    def get_current_timestamp(self):
        return int(round(time.time(), 0))

    def get_current_time(self):
        return time.asctime(time.localtime(time.time()))

    def update_params(self):
        print(f"--- Updating params {self.get_current_time()} ---")
        id, tweetNumber, lastTweetTimestamp, tweetToReplyId = self.get_db_data()
        self.dbData.lastTweetTimestamp = lastTweetTimestamp
        self.dbData.tweetNumber = tweetNumber
        self.dbData.tweetToReplyId = tweetToReplyId
        if self.dbData.lastTweetTimestamp is None:
            self.dbData.lastTweetTimestamp = self.get_current_timestamp()
        if self.dbData.tweetNumber is None or self.dbData.tweetNumber == 0:
            self.dbData.tweetNumber = 1
        print(f"--- Updated data from db: tweetNumber {self.dbData.tweetNumber}, lastTweetTimestamp {self.dbData.lastTweetTimestamp}, tweetToReplyId {self.dbData.tweetToReplyId} ---")
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
        print(f"--- Updated data from storage file: id {self.currentTweet.id}, isTheFirstOne {self.currentTweet.isTheFirstOne}, isTheLastOne {self.currentTweet.isTheLastOne}, text {self.currentTweet.text}, videoIdTW {self.currentTweet.videoIdTW}, videoIdYT {self.currentTweet.videoIdYT} ---")

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
            url = get_storage_url()
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(e)
            return None

    def launch_or_sleep(self):
        self.update_params()
        currentTimestamp = self.get_current_timestamp()
        if self.currentTweet.isTheFirstOne == True:
            remains = self.dbData.lastTweetTimestamp + self.timeToNextSerie - currentTimestamp
        else:
            remains = self.dbData.lastTweetTimestamp + self.timeToSameSerie - currentTimestamp
        if remains > 0:
            print(f"--- It's NOT time, sleeping {remains} seconds to post {self.currentTweet.id} ({self.get_current_time()}) ---")
            time.sleep(remains)
            self.launch_or_sleep()
            return
        tweet = f"{self.currentTweet.text} https://twitter.com/FrankSuarezTv/status/{self.currentTweet.videoIdTW}/video/1"
        print(f"--- Sending tweet number {self.currentTweet.id}, {tweet} ({self.get_current_time()}) ---")
        if self.currentTweet.isTheFirstOne == True or self.dbData.tweetToReplyId == 0:
            print("--- Head tweet ---")
            self.api.update_status(tweet)
        else:
            print("--- Tweet reply ---")
            self.api.update_status(status=tweet, in_reply_to_status_id=self.dbData.tweetToReplyId, auto_populate_reply_metadata=True)
        print("--- Done")
        self.update_db(None)

    def update_db(self, tweetToReplyId):
        print(f"--- Updating db ({self.get_current_time()}) ---")
        conn = sqlite3.connect('frank.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if tweetToReplyId is None:
            if self.dbData.tweetNumber != len(self.data['objects']):
                nextTweetNumber = self.dbData.tweetNumber + 1
            else:
                nextTweetNumber = 1
            lastTweetTimestamp = self.get_current_timestamp()
            print(f"--- Saving next tweet number {nextTweetNumber} and last tweet timestamp {lastTweetTimestamp} in db ---")
            cursor.execute('''UPDATE frankData SET tweetNumber = ? WHERE id = ? ''', (nextTweetNumber, 1))
            cursor.execute('''UPDATE frankData SET lastTweetTimestamp = ? WHERE id = ? ''', (lastTweetTimestamp, 1))
        else:
            print(f"--- Saving tweet to reply id {tweetToReplyId} in db ---")
            cursor.execute('''UPDATE frankData SET tweetToReplyId = ? WHERE id = ? ''', (tweetToReplyId, 1))
        conn.commit()
        cursor.close()

    def on_status(self, tweet):
        try:
            tweet_id = tweet.id
            text = self.api.get_status(tweet_id).text
            print(f"Analyzing {text}")
            if tweet.user.id != self.me.id or 'RT @FrankSuarezTv:' in text:  #1384308750610227200
                return
            currentTweet = self.search_tweet(text)
            if currentTweet is None or self.currentTweet.text != currentTweet.text:
                return
            print(f"\n\n\n\n\n\n--- Sending tweet next to {text} ---")
            if currentTweet.isTheLastOne == True:
                self.send_complete_video_tweet(tweet_id)
                self.update_db(0)
                self.launch_or_sleep()
            else:
                self.update_db(tweet_id)
                self.launch_or_sleep()
        except Exception as e:
            print(f"\n--- On status error: {e} ---")

    def search_tweet(self, text):
        print("Searching for", text)
        if self.data == None or self.data['objects'] == None:
            print("--- Exit")
            return
        for tweet in self.data['objects']:
            if tweet['text'] in text:
                print(f"--- Tweet found: {tweet['text']}")
                return Tweet(tweet['id'], tweet['text'], tweet['videoIdTW'], tweet['videoIdYT'], tweet['isTheFirstOne'], tweet['isTheLastOne'])

    def send_complete_video_tweet(self, tweet_id):
        print(f"--- Waiting {self.timeToSameSerie} seconds to send Complete Video URL...")
        time.sleep(self.timeToSameSerie)
        tweet = f"Video completo: https://youtu.be/{self.currentTweet.videoIdYT}"
        print(f"--- Sending tweet {tweet} ({self.get_current_time()}) ---")
        self.api.update_status(status=tweet, in_reply_to_status_id=tweet_id, auto_populate_reply_metadata=True)
        print("--- Done")

    def on_limit(self, status):
        print(f"--- Rate Limit Exceeded, Sleep for 2 Mins: {status}")
        time.sleep(2 * 60)
        return True

    def on_error(self, status):
        print(f"\n--- ERROR: {status} ---\n")

def main():
    keywords = ['FrankSuarezTv']
    try:
        api = create_api()
        tweets_listener = FrankTvBot(api)
        stream = tweepy.Stream(api.auth, tweets_listener)
        stream.filter(track=keywords, languages=['es', 'en'])
    except Exception as e:
        print("App failed:", e)
        time.sleep(60)
        main()
        return

if __name__ == "__main__":
    main()
