import json
import logging
import sqlite3
import time
import tweepy
from config import create_api

# 1. Poner a escuchar tweets con "@fstv"
# 2. Lanzar primer tweet
# 3. Activar bandera de si es último video de la serie

# 4. Si es último de serie, suspender escucha, guardar vacío en db pero guardar hora del próximo tweet
# 5. A las 8 hs lanzar tweet y repetir 3

# 4. Procesar los escuchados buscando eso y que sea propio
# 5. El que cumpla, capturar id, calcular cuánto falta para 8 hs, anotar en db el id y a qué hora tiene que salir el tweet y dejar de escuchar
# 6. Dormir hasta la hora calculada
# 7. Lanzar tweet como respuesta al anterior
# 8. Volver a escuchar para repetir

# Si se reinicia, tiene que leer la db para ver a qué hora seguir y si tiene que replicar o empezar nueva serie

class FrankTvBot(tweepy.StreamListener):
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    
    def __init__(self, api):
        print(f"\n--- Starting at {time.asctime(time.localtime(time.time()))} ---\n")
        self.api = api
        self.me = api.me()
        self.nextTweetTimestamp
        self.lastVideoYTId
        self.nextVideoIsFirstOfSerie
        self.nextVideoIsLastOfSerie
        self.tweetToReplyId
        self.tweetNumber
        with open('storage.json', encoding='utf-8') as json_file:
            self.data = json.load(json_file)
        self.update_params()
        self.launch_or_sleep(self)

    def launch_or_sleep(self):
        currentTimestampInSeconds = round(time.time(), 0)
        remains = self.nextTweetTimestamp-currentTimestampInSeconds
        print(f"\n--- Comparing db timestamp {self.nextTweetTimestamp} with current {currentTimestampInSeconds} ({remains}) ---\n")
        if self.nextTweetTimestamp != 0 and remains > 0:
            print(f"\n--- It's NOT time, sleeping {remains} ---\n")
            time.sleep(remains)
            # verificar que no se haya respondido mientras se dormía
        print(f"\n--- Launching tweet... tweetNumber {self.tweetNumber} ---\n")
        self.send_tweet(self)
        while True:
            try:
                self.update_db(self, False)
            except Exception as e:
                print("\n--- Error updating params:", e, "---\n")
                self.logger.error("\n--- Error updating params:", e, "---\n")
                time.sleep(60)
    
    def on_status(self, tweet):
        try:
            self.update_params()
            me_id = self.me.id
            user_id = tweet.user.id
            tweetId = tweet.id
            status = tweet.get_status(id)
            text = status.text
            if self.nextVideoIsFirstOfSerie(self) == True:
                print(f"\n--- Ignoring because next video is head: {text} ---\n")
                return
            self.logger.info(f"\n--- Processing tweet {tweetId} {text} ---\n")
            if user_id != me_id:
                print("\n--- This tweet is not mine ---\n")
                return
            if 'https://twitter.com/FrankSuarezTv/status/' not in text or '/video/1' not in text:
                print("\n--- It's not a video serie ---\n")
                return
            print("\n--- Sending tweet... ---\n")
            videoYTId = text.split('https://twitter.com/FrankSuarezTv/status/')[1].split('/video/1')[0]
            print(f"\n--- Comparing {videoYTId} with {self.lastVideoYTId} ---\n")
            if self.lastVideoYTId != videoYTId:
                print("\n--- It's not the video to reply to ---\n")
                return
            self.tweetToReplyId = tweetId
            self.update_db(self, True)
            self.launch_or_sleep(self)
        except Exception as e:
            print("\n--- Error on status:", e, "---\n")
            self.logger.error("\n--- Error on status:", e, "---\n")

    def send_tweet(self):
        title = self.data['objects'][self.tweetNumber-1]['text']
        video = f"https://twitter.com/FrankSuarezTv/status/{self.data['objects'][self.tweetNumber-1]['videoIdTW']}/video/1"
        tuit = f"{title} {video}"
        if self.nextVideoIsFirstOfSerie == True:
            print("\n--- Head tweet ---\n")
            self.api.update_status(tuit)
        else:
            print("\n--- Tweet reply ---\n")
            self.api.update_status(status = tuit, in_reply_to_status_id = self.tweetToReplyId , auto_populate_reply_metadata = True)
            #self.api.update_status(f"{tuit}", self.tweetToReplyId)
        
    def update_params(self):
        print(f"\n--- Updating params ---\n")
        conn = sqlite3.connect('frank.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM nextTweet''')
        self.tweetNumber, self.nextTweetTimestamp, self.tweetToReplyId = cursor.fetchone()   # 3 integers
        if self.nextTweetTimestamp is None:
            self.nextTweetTimestamp = 0
        if self.tweetNumber is None or self.tweetNumber == 0:
            self.tweetNumber = 1
        self.nextVideoIsFirstOfSerie = self.data['objects'][self.tweetNumber-1]['isTheFirstOne']
        self.nextVideoIsLastOfSerie = self.data['objects'][self.tweetNumber-1]['isTheLastOne']
        if self.tweetNumber == 1:
            self.lastVideoYTId = self.data['objects'][self.data['objects'].length()-1]['videoIdYT']
        else:
            self.lastVideoYTId = self.data['objects'][self.tweetNumber-2]['videoIdYT']
        print("\n--- Updated data from db ---\n")
        conn.commit()
        cursor.close()
    
    def update_db(self, savingTweetToReplyId):
        print(f"\n--- Updating db ---\n")
        conn = sqlite3.connect('frank.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if savingTweetToReplyId == True:
            print(f"\n--- Saving tweet to reply id {self.tweetToReplyId} in db ---\n")
            cursor.execute(f"""UPDATE frankData SET tweetToReplyId = {self.tweetToReplyId} WHERE id = 1""")
        else:
            if self.tweetNumber == self.data['objects'].length():
                self.tweetNumber = 1
            else:
                self.tweetNumber = self.tweetNumber + 1
            self.nextTweetTimestamp = self.nextTweetTimestamp + 28800     # 8 hs   ver qué pasa en caida
            cursor.execute(f"""UPDATE frankData SET tweetNumber = {self.tweetNumber} WHERE id = 1""")
            cursor.execute(f"""UPDATE frankData SET nextTweetTimestamp = {self.nextTweetTimestamp} WHERE id = 1""")
        conn.commit()
        cursor.close()

    def on_error(self, status):
        self.logger.error(status)

def main():
    keywords = ["FrankSuarezTv"]
    try:
        api = create_api()
        tweets_listener = FrankTvBot(api)
        stream = tweepy.Stream(api.auth, tweets_listener)
        stream.filter(track=keywords, languages=["es", "en"])
    except Exception as e:
        print("App failed:", e)
        time.sleep(600)
        main()

if __name__ == "__main__":
    main()
