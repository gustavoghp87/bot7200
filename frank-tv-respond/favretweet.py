from logging import log
import tweepy
import logging
from config import create_api
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

class FavRetweetListener(tweepy.StreamListener):

    def __init__(self, api):
        self.api = api
        self.me = api.me()

    def on_status(self, tweet):

        logger.info(f"Processing tweet id {tweet.id}")

        if tweet.in_reply_to_status_id is not None or \
            tweet.user.id == self.me.id:
            print("This tweet is a reply or I'm its author so, ignore it")
            return

        if not tweet.favorited:
            try:
                tweet.favorite()
                user = str(tweet).split("screen_name': '")[1].split("'")[0]
                id = str(tweet).split("id': ")[1].split(',')[0]
                print(f"\n\nFaveado tuit {id} de @{user}")
            except Exception as e:
                print("Error faveando:", e)
        else:
            print("Ya faveado")

            # try:
            #     text = str(tweet).split("text': '")[1].split("'")[0]
            #     print(text)
            #     user = str(tweet).split("screen_name': '")[1].split("'")[0]
            #     id = str(tweet).split("id': ")[1].split(',')[0]

            #     if 'maslazoom' in text.lower() and 'listado de todos los maslazooms' not in text.lower():
            #         print(f"\n\nEnviando mensaje a @{user}, id {id}, por el tuit {text}")
            #         self.api.update_status(f"@{user} El listado de todos los maslazooms está en maslabook.com/maslazoom, saludos", id)

                # if 'toalla' in text.lower() or 'toallin' in text.lower() or 'toallín' in text.lower():
                #     print(f"\n\nEnviando mensaje a @{user}, id {id}, por el tuit {text}")
                #     filename = 'temp.jpg'
                #     request = requests.get("https://i.pinimg.com/originals/40/a1/91/40a191c06187848f0a2070ad68555564.jpg", stream=True)
                #     if request.status_code == 200:
                #         with open(filename, 'wb') as image:
                #             for chunk in request:
                #                 image.write(chunk)
                #         self.api.update_with_media(filename, status=f"@{user} no olvides llevar una toalla")
                #         os.remove(filename)

            # except Exception as e:
            #     logger.error("Error enviando mensaje", e)

    def on_error(self, status):
        logger.error(status)


def main():
    keywords = ["franksuarez", "metabolismotv", "metabolismo", "metabolism", "Metabolism", "diabetes"]
    try:
        api = create_api()
        tweets_listener = FavRetweetListener(api)
        stream = tweepy.Stream(api.auth, tweets_listener)
        stream.filter(track=keywords, languages=["es"])
    except Exception as e:
        print("Falló app:", e)
        time.sleep(36000)
        main()

if __name__ == "__main__":
    main()
