from decouple import config
from selenium import webdriver
import json
import logging
import requests
import time
import tweepy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

class FavRetweetListener(tweepy.StreamListener):

    def __init__(self, api):
        starttime = time.time()
        while True:
            logger.info(f"tick, son las {time.asctime(time.localtime(time.time()))}")
            url = 'https://maslabook.herokuapp.com/api/bot'
            #url = 'http://localhost:8005/api/bot'
            payload = {'password': config('COUNTER_PW')}
            headers = {'content-type': 'application/json'}
            try:
                response = requests.post(url, data=json.dumps(payload), headers=headers)
                response_json = response.json()
                post_text = response_json["post_text"]
                logger.info(response_json)
                if "network" in response_json and response_json["network"] == 'fb':
                    print("FB")
                    image = self.get_image(response_json['url'])
                    if image is None:
                        print("No image") ###################3
                        api.update_status(post_text)
                    else:
                        api.update_with_media("image.jpg", status=post_text)
                else:
                    print("TW")
                    api.update_status(post_text)
            except Exception as e:
                print(e)

            #logger.info("My friends:", friends_names)
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

    def get_image(self, url):
        print("Getting image")
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        #driver = webdriver.Chrome(options=options)
        driver = webdriver.Remote("http://127.0.0.1:4444/wd/hub", options=options)
        try:
            driver.get(url)
            time.sleep(7)
            print(driver.find_element('id', '#loginform'))
            if driver.find_element('id', '#loginform'):
                username = driver.find_element('id', 'email')
                password = driver.find_element('id', 'pass')
                submit   = driver.find_element('id', 'loginbutton')
                username.send_keys(config("FB_USERNAME"))
                password.send_keys(config("FB_PASSWORD"))
                submit.click()
                #driver.get(url)
                time.sleep(4)
            driver.save_screenshot('image.png')
            return True
        except Exception as e:
            print(e)
            return False
        finally:
            driver.quit()
        # try:
        #     url_final = f"https://api.apiflash.com/v1/urltoimage?access_key={access_key}&url={response_json['url']}&format=jpeg&scroll_page=true&response_type=image&css=%23headerArea%7Bdisplay%3A%20none%3B%7D"
        #     r = requests.get(url_final, stream=True)
        #     with open('image.jpg', 'wb') as file:
        #         for chunk in r:
        #             file.write(chunk)
        #     api.update_with_media("image.jpg", status=post_text)
        #     #api.update_with_media(base64.b64decode(response_json["file"]), status=post_text)
        # except Exception as ex:
        #     print(ex)
        #     api.update_status(post_text)

    def on_error(self, status):
        logger.error(status)

def create_api():
    consumer_key = config("api_public")
    consumer_secret = config("api_secret")
    access_token = config("token_public")
    access_token_secret = config("token_secret")
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, 
        wait_on_rate_limit_notify=True)
    try:
        api.verify_credentials()
    except Exception as e:
        logger.error("Error creating API", exc_info=True)
        raise e
    logger.info("API created")
    return api

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
