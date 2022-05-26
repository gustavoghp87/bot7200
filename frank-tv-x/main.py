import json
import logging
import requests
import sqlite3
import time
import tweepy
from config import create_api
from config import get_storage_url

class FrankTvBot(tweepy.StreamListener):
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    
    def __init__(self, api):
        print(f"\n--- Starting at {time.asctime(time.localtime(time.time()))} ---\n")
        self.api = api
        self.me = api.me()
        self.title = None
        self.lastTitle = None
        self.nextTweetTimestamp = None
        self.currentIsFirstOfSerie = None
        self.nextIsLastOfSerie = None
        self.tweetToReplyId = None
        self.tweetNumber = None
        self.data = None
        self.update_params()
        self.launch_or_sleep()

    def launch_or_sleep(self):
        currentTimestamp = int(round(time.time(), 0))
        remains = self.nextTweetTimestamp-currentTimestamp
        print(f"\n--- Comparing db timestamp {self.nextTweetTimestamp} with current {currentTimestamp} ({remains}) ---\n")
        if self.nextTweetTimestamp != 0 and remains > 0:
            print(f"\n--- It's NOT time, sleeping {remains} ---\n")
            time.sleep(remains)
            self.update_params()
            self.launch_or_sleep()
            return
        video_id = self.data['objects'][self.tweetNumber-1]['videoIdTW']
        video = f"https://twitter.com/FrankSuarezTv/status/{video_id}/video/1"
        tweet = f"{self.title} {video}"
        print(f"\n--- Sending tweet... tweet number {self.tweetNumber}, {tweet} ---\n")
        if self.currentIsFirstOfSerie == True or self.tweetToReplyId == 0:
            print("--- Head tweet ---\n")
            self.api.update_status(tweet)
        else:
            print("--- Tweet reply ---\n")
            self.api.update_status(status = tweet, in_reply_to_status_id = self.tweetToReplyId , auto_populate_reply_metadata = True)
        print("Done")
        self.update_db(False)
    
    def on_status(self, tweet):
        try:
            me_id = self.me.id   # 1384308750610227200
            user_id = tweet.user.id
            tweet_id = tweet.id
            status = self.api.get_status(tweet_id)
            text = status.text
            self.logger.info(f"\n\n\n\n\n\n\n\n\n #########################################################################\n\n--- PROCESSING TWEET ---\n")
            print(me_id, user_id, tweet_id)
            print(text)
            if user_id != me_id:
                print("\n--- This tweet is not mine ---\n")
                return
            # if 'RT @FrankSuarezTv:' in text:
            #     print("\n--- It's not the video to reply to ---\n")
            #     return
            if 'https://twitter.com/FrankSuarezTv/status/' not in text and 'https://t.co/' not in text:
                print("\n--- It's not a video serie ---\n")
                return
            self.update_params()
            print(self.lastTitle)
            if self.lastTitle not in text:
                print("\n--- It's not the video to reply ---\n")
                return
            print("\n--- Sending tweet... ---\n")
            if self.nextIsLastOfSerie == True:
                self.tweetToReplyId = 0
            else:
                self.tweetToReplyId = tweet_id
            self.update_db(True)
            self.launch_or_sleep()
        except Exception as e:
            print("\n--- On status error:", e, "---\n")

    def update_params(self):
        # with open(self.get_storage(), encoding='utf-8') as json_file:
        #     self.data = json.load(json_file)
        self.data = self.get_storage()
        print(f"\n--- Updating params ---\n")
        try:
            conn = sqlite3.connect('frank.db')     # execute('''CREATE TABLE frankData(id int, tweetNumber int)''')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''SELECT * FROM frankData''')
            id, tweetNumber, nextTweetTimestamp, tweetToReplyId = cursor.fetchone()   # int, int, int, str
            self.tweetNumber = tweetNumber
            self.nextTweetTimestamp = nextTweetTimestamp
            self.tweetToReplyId = tweetToReplyId
        except Exception as e:
            print("\n---", e, "---\n")
            try:
                cursor.execute(''' INSERT INTO frankData(tweetNumber, tweetToReplyId, nextTweetTimestamp) VALUES (?,?,?) ''', (1, 0, 0))
                conn.commit()
            except Exception as ex:
                print("\n---", ex, "---\n")
        finally:
            cursor.close()
        if self.nextTweetTimestamp is None:
            self.nextTweetTimestamp = int(round(time.time(), 0))
        if self.tweetNumber is None or self.tweetNumber == 0:
            self.tweetNumber = 1
        self.currentIsFirstOfSerie = self.data['objects'][self.tweetNumber-1]['isTheFirstOne']
        self.title = self.data['objects'][self.tweetNumber-1]['text']
        if self.tweetNumber == 1:
            self.nextIsLastOfSerie = True
            self.lastTitle = self.data['objects'][len(self.data['objects'])-1]['text']
        else:
            self.nextIsLastOfSerie = self.data['objects'][self.tweetNumber-2]['isTheLastOne']
            self.lastTitle = self.data['objects'][self.tweetNumber-2]['text']
        print("\n--- Updated data from db:", self.tweetNumber, self.nextTweetTimestamp, self.tweetToReplyId, self.currentIsFirstOfSerie, self.nextIsLastOfSerie, "---\n")
    
    def update_db(self, savingTweetToReplyId):
        try:
            print(f"\n--- Updating db ---\n")
            conn = sqlite3.connect('frank.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if savingTweetToReplyId == True:
                print(f"\n--- Saving tweet to reply id {self.tweetToReplyId} in db ---\n")
                cursor.execute('''UPDATE frankData SET tweetToReplyId = ? WHERE id = ? ''', (self.tweetToReplyId, 1))
            else:
                if self.tweetNumber == len(self.data['objects']):
                    self.tweetNumber = 1
                else:
                    self.tweetNumber = self.tweetNumber + 1
                self.nextTweetTimestamp = int(round(time.time(), 0)) + 300     # 8 hs = 28800 - 5
                cursor.execute('''UPDATE frankData SET tweetNumber = ? WHERE id = ? ''', (self.tweetNumber, 1))
                cursor.execute('''UPDATE frankData SET nextTweetTimestamp = ? WHERE id = ? ''', (self.nextTweetTimestamp, 1))
            conn.commit()
        except Exception as e:
            print("\n--- Error updating params in db:", e, " ---\n")
            time.sleep(60)
            self.update_db(savingTweetToReplyId)
        finally:
            cursor.close()

    def on_error(self, status):
        self.logger.error(status)
        
    def get_storage(self):
        try:
            url = get_storage_url()
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"\n--- Method get_storage failed: {e} ---\n")
            time.sleep(60)
            self.launch_or_sleep()
            return

def main():
    keywords = ["FrankSuarezTv"]
    try:
        api = create_api()
        tweets_listener = FrankTvBot(api)
        stream = tweepy.Stream(api.auth, tweets_listener)
        stream.filter(track=keywords, languages=["es", "en"])
    except Exception as e:
        print("App failed:", e)
        time.sleep(60)
        main()
        return

if __name__ == "__main__":
    main()
