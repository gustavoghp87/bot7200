from config import create_api
from decouple import config
import base64
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
            logger.info(f"tick, son las {time.asctime(time.localtime(time.time()))}")
            
            url = 'https://maslabook.herokuapp.com/api/bot'
            payload = {'password': config('COUNTER_PW')}
            headers = {'content-type': 'application/json'}
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            
            response_json = response.json()
            post_text = response_json["post_text"]
            file = response_json["file"]
            logger.info(response_json)

            if file is None:
                self.api.update_status(post_text)
            else:
                try:
                    self.api.update_with_media(base64.b64decode(file), status=post_text)
                except Exception as e:
                    logger.info(e)
            
            #logger.info("Yo sigo:", friends_names)
            friends_names = []
            for friend in api.friends():
                friends_names.append(friend.screen_name)
            for follower in api.followers():
                if follower.screen_name not in friends_names:
                    try:
                        if follower.screen_name != 'carlosmaslaton':
                            follower.follow()
                            api.create_mute(follower.screen_name)
                            print (f"Siguiendo a {follower.screen_name}, silenciado")
                    except:
                        logger.info("\n")
            
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
        logger.info("Error API:", e, "\n\n\n\n")
        time.sleep(60*30)
        main()

if __name__ == "__main__":
    main()