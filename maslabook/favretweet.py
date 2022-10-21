from config import create_api
from decouple import config
from logging import log
import json
import logging
import requests
import time
import tweepy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

class FavRetweetListener(tweepy.StreamListener):

    def __init__(self, api):
        self.api = api
        self.me = api.me()
        starttime = time.time()

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
                        if follower.screen_name != carlosmaslaton:
                            follower.follow()
                            api.create_mute(follower.screen_name)
                            print (f"Siguiendo a {follower.screen_name}, silenciado")
                    except:
                        print("\n")
            
            loop = 7200*3
            time.sleep(loop - ((time.time() - starttime) % loop))

    def on_error(self, status):
        logger.error(status)


def main():
    try:
        api = create_api()
        tweets_listener = FavRetweetListener(api)
        tweepy.Stream(api.auth, tweets_listener)
    except Exception as e:
        print("Error API:", e, "\n\n\n\n")
        time.sleep(60*30)
        main()

if __name__ == "__main__":
    main()