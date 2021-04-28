from logging import log
import requests
import tweepy
import logging
from config import create_api
import time
import json
from decouple import config
import sqlite3
import os


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

class FavRetweetListener(tweepy.StreamListener):
    def __init__(self, api):
        self.api = api
        self.me = api.me()
        starttime = time.time()

        with open('storage.json', encoding='utf-8') as json_file:
            data = json.load(json_file)
            for p in data['objects']:
                print(f"Id: {p['id']}")
                print('Text: ' + p['text'])
                print('VideoIdTW: ' + p['videoIdTW'])
                print('VideoIdYT: ' + p['videoIdYT'])
                print('')
        
        print("###############################################################################################################\n\n")

        while True:
            print(f"tick, son las {time.asctime(time.localtime(time.time()))}")

            # if not os.path.exists('db'):
            #     os.makedirs('db')
            # if not os.path.exists('/db/frank.db'):
            #     open('db/frank.db', 'w')
            #     conn = sqlite3.connect('db/frank.db')
            #     c = conn.cursor()
            #     c.execute('''CREATE TABLE nextTweet(id int, tuitNumber int)''')
            #     c.execute("""INSERT INTO nextTweet (id, tuitNumber) VALUES (1, 1)""")
            #     conn.commit()
            #     c.close()

            conn = sqlite3.connect('db/frank.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''SELECT * FROM nextTweet''')
            id, tuitNumber = cursor.fetchone()
            print(id, tuitNumber)

            if tuitNumber < len(data['objects']):
                nextTuitNumber = tuitNumber + 1
            else:
                nextTuitNumber = 1

            print("Next:", nextTuitNumber)
            
            cursor.execute(f"""UPDATE nextTweet SET tuitNumber = {nextTuitNumber} WHERE id = 1""")
            conn.commit()
            cursor.close()


            tuit = f" {data['objects'][tuitNumber-1]['text']}         (https://www.youtube.com/watch?v={data['objects'][tuitNumber-1]['videoIdYT']}) https://twitter.com/FrankSuarezTv/status/{data['objects'][tuitNumber-1]['videoIdTW']}/video/1"
            
            try:
                print("Tuiteando:", tuit)
                self.api.update_status(tuit)

            except AssertionError as error:
                print("Error", error)

            

            print("\n\n\n")


            
            friends_names = []
            for friend in api.friends():
                friends_names.append(friend.screen_name)

            for follower in api.followers():
                if follower.screen_name not in friends_names:
                    try:
                        follower.follow()
                        api.create_mute(follower.screen_name)
                        print (f"Siguiendo a {follower.screen_name}, silenciado")
                    except:
                        print("\n")
            

            loop = 60*60*8
            time.sleep(loop - ((time.time() - starttime) % loop))

    def on_error(self, status):
        logger.error(status)


def main():
    api = create_api()
    tweets_listener = FavRetweetListener(api)
    tweepy.Stream(api.auth, tweets_listener)

if __name__ == "__main__":
    main()
