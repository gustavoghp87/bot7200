from logging import log
import requests
import tweepy
import logging
from config import create_api
import time
import json
from decouple import config
# import pymongo


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

class FavRetweetListener(tweepy.StreamListener):
    def __init__(self, api):
        self.api = api
        self.me = api.me()
        starttime = time.time()

        #connect = config('ATLAS_DB')
        #myclient = pymongo.MongoClient(connect)
        #mydb = myclient["bots"]
        #mycol = mydb["bot7200"]

        while True:
            print(f"tick, son las {time.asctime(time.localtime(time.time()))}")
            
            url = 'https://maslabook.herokuapp.com/api/bot'
            payload = {'password': config('COUNTER_PW')}
            headers = {'content-type': 'application/json'}
            tuit = requests.post(url, data=json.dumps(payload), headers=headers)

            print(tuit.json())
            self.api.update_status(tuit.json())
            
            friends_names = []
            for friend in api.friends():
                friends_names.append(friend.screen_name)

            #print("Yo sigo:", friends_names)

            for follower in api.followers():
                if follower.screen_name not in friends_names:
                    try:
                        follower.follow()
                        api.create_mute(follower.screen_name)
                        print (f"Siguiendo a {follower.screen_name}, silenciado")
                    except:
                        print("\n")
            
            loop = 7200
            time.sleep(loop - ((time.time() - starttime) % loop))

    def on_error(self, status):
        logger.error(status)


def main():
    api = create_api()
    tweets_listener = FavRetweetListener(api)
    tweepy.Stream(api.auth, tweets_listener)

if __name__ == "__main__":
    main()
