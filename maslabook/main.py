from decouple import config
#from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
import json
import logging
import requests
import time
import tweepy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
image = 'image.png'

class FavRetweetListener(tweepy.StreamListener):

    def __init__(self, api):
        starttime = time.time()
        self.standalone = 1
        while True:
            logger.info(f"tick, it's {time.asctime(time.localtime(time.time()))}")
            url = 'https://maslabook.herokuapp.com/api/bot'
            #url = 'http://localhost:8005/api/bot'
            payload = {'password': config('COUNTER_PW')}
            headers = {'content-type': 'application/json'}
            try:
                response = requests.post(url, data=json.dumps(payload), headers=headers)
                response_json = response.json()
                post_text = response_json["post_text"]
                if post_text is None or post_text.lower() == "nan":
                    post_text = ""
                logger.info(response_json)
                if "network" in response_json and response_json["network"] == 'fb':
                    logger.info("FB")
                    hasImage = self.get_image(response_json['url'])
                    if hasImage is True:
                        api.update_with_media(image, status=post_text)
                    else:
                        logger.info("FB: No image")
                        api.update_status(post_text)
                else:
                    logger.info("TW")
                    if 'facebook.com' in post_text:
                        words = post_text.split()
                        for word in words:
                            if 'facebook.com' not in word:
                                continue
                            hasImage = self.get_image(word)
                            if hasImage is True:
                                api.update_with_media(image, status=post_text)
                            else:
                                logger.info("TW: Url but no image")
                                api.update_status(post_text)
                    else:
                        logger.info("TW no image")
                        api.update_status(post_text)
            except Exception as e:
                logger.info(e)
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
                            logger.info(f"Siguiendo a {follower.screen_name}, silenciado")
                    except:
                        logger.info("\n")
            loop = 7200*3
            time.sleep(loop - ((time.time() - starttime) % loop))

    def increase_standalone(self):
        self.standalone += 1
        logger.info(f"Increased standalone to {str(self.standalone)}")

    def get_image(self, url):
        logger.info("Getting image")
        #driver = webdriver.Chrome(options=options)
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        firefox_url = 'http://172.17.0.' + str(self.standalone) + ':4444/wd/hub'
        driver = None
        try:
            driver = webdriver.Remote(firefox_url, options=options)
            driver.get(url)
            time.sleep(7)
            # divs by role: image "main", text "complementary", all "feed"
            try:
                logger.info(driver.find_element('css selector', '#loginform'))
                username = driver.find_element('css selector', '#email')
                password = driver.find_element('css selector', '#pass')
                submit   = driver.find_element('css selector', '#loginbutton')
                username.send_keys(config("FB_USERNAME"))
                password.send_keys(config("FB_PASSWORD"))
                submit.click()
                time.sleep(4)
            except:
                logger.info("No login page")
            try:
                driver.execute_script('document.getElementById("headerArea").style.display="none";')
            except:
                logger.info("No headerArea found")
            try:
                driver.execute_script('document.getElementById("pagelet_bluebar").style.display="none";')
            except:
                logger.info("No pagelet_bluebar found")
            try:
                # driver.find_element('xpath', "//*[contains(text(), 'See more')]").click()
                # elements = driver.find_elements(By.CSS_SELECTOR, 'span')
                # for element in elements:
                #     if element.text == "See more of Carlos Maslatón on Facebook":
                #         origin = element.find_element('xpath', "..").find_element('xpath', "..").find_element('xpath', "..").find_element('xpath', "..").find_element('xpath', "..").find_element('xpath', "..")
                script = "Array.from(document.querySelectorAll('span')).forEach(x => { if(x.textContent == 'See more of Carlos Maslatón on Facebook') x.parentElement.parentElement.parentElement.parentElement.remove() });"
                driver.execute_script(script)
            except:
                logger.info("No See more button found")
            driver.save_screenshot(image)
            # try:
            #     feed = driver.find_element('css selector', 'div[role="feed"]')
            #     x = feed.location['x']
            #     y = feed.location['y']
            #     width = x + feed.size['width']
            #     height = y + feed.size['height']
            #     im = Image.open(image)
            #     im = im.crop((int(x), int(y), int(width), int(height)))
            #     im.save(image)
            #     logger.info("Cropped image")
            # except Exception as exc:
            #     logger.info(exc)
            return True
        except Exception as e:
            logger.info(e)
            self.increase_standalone()
            if self.standalone < 11:
                return self.get_image(url)
            else:
                return False
        finally:
            if driver is not None:
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
        #     logger.info(ex)
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

# def set_display_none(driver, type, selector, error):
#     try:
#         if type == "css":
#             driver.execute_script(f'document.querySelector({selector}).style.display = "none";')
#         elif type == "xpath":
#             driver.execute_script(f'document.evaluate({selector}, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.style.display = "none";')
#     except:
#         logger.info(error)
    # ID = "id"
    # NAME = "name"
    # XPATH = "xpath"
    # LINK_TEXT = "link text"
    # PARTIAL_LINK_TEXT = "partial link text"
    # TAG_NAME = "tag name"
    # CLASS_NAME = "class name"
    # CSS_SELECTOR = "css selector"

def main():
    try:
        api = create_api()
        FavRetweetListener(api)
    except Exception as e:
        logger.info("Error API:", e, "\n\n\n\n")
        time.sleep(60*30)
        main()

if __name__ == "__main__":
    main()
