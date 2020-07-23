# -*- coding: utf-8 -*-
import os,sys,time,re
import tweepy

from splitter import Splitter
from ocrspace import API
from random   import random

from dotenv   import load_dotenv,set_key
load_dotenv()

MYNAME    = os.getenv('TWITTER_SN') # # Twitter account screenname prefixed with @
MAGICW    = os.getenv('TWITTER_MW') # # Phrase that must be present to perform ocr

PENALTY_TIME = 60
PENALTY_INCR = 60

# Messgaes to sponsors & thanks
DEBUG     = True
DONTPOST  = False

if DEBUG:
    USETHANKS = False
else:
    USETHANKS = True
THANKSTXT = "Service is able to run with the kind help of pythonanywhere.com @pythonanywhere"

class ocrbot_stream(tweepy.StreamListener):

    def local_init(     self ):
        ocrParams      = {
            'detectOrientation': "true",
            'scale'            : "true",
            'OCREngine'        : 2
        }
        self.ocr_api        = API(api_key=os.getenv('OCR_KEY'), language='eng', **ocrParams)
        self.myLastRun      = int(os.getenv("LAST_RUN",default = 0))
        self.unameregex     = re.compile(r'@([A-Za-z0-9_]+)')
        self.auth           = tweepy.OAuthHandler(os.getenv('CONSUMER_KEY'), os.getenv('CONSUMER_SECRET')    )
        self.auth.set_access_token(               os.getenv('ACCESS_TOKEN'), os.getenv('ACCESS_TOKEN_SECRET'))
        self.api            = tweepy.API(self.auth)
    def OCRImage(       self, imageUrl, splitLength=None): # ////////////////////////////////////////
        # Call ocr.space API, wait and return list of tweets
        ocrResult    = self.ocr_api.ocr_url(imageUrl)
        if splitLength!=None:
            tweetsToSend = Splitter.forTweets(ocrResult, splitLength=splitLength) # tweet length limits (280-8-15) user name and brackets
        else:
            tweetsToSend = Splitter.forTweets(ocrResult)
        if DEBUG:
            print(" Tweet chain length {}".format(len(tweetsToSend)))
        return tweetsToSend
    def find_images(    self, collection): # ////////////////////////////////////////////////////////
        mediaFound = []
        for img in collection:
            if img["type"]=="photo":
                mediaFound.append(img["media_url"])
            else:
                if DEBUG:
                    print("ignoring {} as not photo".format(img))

        if DEBUG: print(" >> Found {} images".format(len(mediaFound)))
        return mediaFound
    def ocr2tweets(     self, task, people, chainStart): # //////////////////////////////////////////
        chainTo = chainStart
        try:
            for i,tweety in enumerate(self.OCRImage(task)):
                if DEBUG: print("  {}.".format(i), end="")
                if DONTPOST:
                    continue

                try:
                    if i%24==0 and i>0:
                        newTweet = self.api.update_status(status="{} https://twitter.com/{}/status/{}".format(people, MYNAME, chainTo))
                        chainTo  = newTweet.id
                        # Continue as thread to that
                    newTweet = self.api.update_status(status=("{} {}".format(people, tweety)) , in_reply_to_status_id = chainTo, auto_populate_reply_metadata=True )
                    chainTo = newTweet.id
                except Exception as e:
                    print("Failed posting : {}".format(e))
                time.sleep(random()) # random sleep so we appear a *tiny* bit less bot-y
                if USETHANKS:
                    self.api.update_status(status=THANKSTXT, in_reply_to_status_id = chainTo, auto_populate_reply_metadata=True)
            return "Success"
        except Exception as e:
            print("Failed OCR : {}".format(e))
            try:
                self.api.update_status(status=("{} Sorry, the optical character recognition failed on this tweet.".format(people)) , in_reply_to_status_id = chainTo, auto_populate_reply_metadata=True )
            except Exception as e:
                print("Failed explaining OCR failure : {}".format(e))
            return "Failed"
    def on_status(      self, mention):
        if mention.id > self.myLastRun:
            set_key(".env","LAST_RUN",str(mention.id))
            self.myLastRun=mention.id

        requestor          = mention.author                      # User obj of requestor
        subjectAuthor_str  = mention.in_reply_to_screen_name     # Screen name of target tweet author
        subjectTweetId     = mention.in_reply_to_status_id       # Target tweet id

        print("tweet {}".format(subjectTweetId))
        subjectTweet       = self.api.get_status(subjectTweetId, include_entities =True, tweet_mode ='extended', trim_user =True)
        conversationalists = "@{}".format(requestor.screen_name)
        if DEBUG: print(conversationalists)

        allMedia   = subjectTweet.extended_entities.get('media', [])
        mediaFound = self.find_images( allMedia ) ## Fixes #5, entities did not include all images
        chainTo    = mention.id;
        for task in mediaFound:
            if DEBUG: print(" {} OCR image {}".format(subjectTweetId, task))
            result = self.ocr2tweets( task, conversationalists, chainTo )
            if DEBUG: print(" {} ".format(result))
    def on_error(       self, status_code):
        if status_code == 420:
            # This is a rate warning and we will have been limited
            # The limit doubles with each subsequent Call
            # So we need to sleep for a while here
            print( "Going into the penalty box for {} secs {}".format(PENALTY_TIME,time.strftime("%H:%M:%S", time.localtime())) )
            time.sleep(PENALTY_TIME)
            PENALTY_TIME = PENALTY_TIME + PENALTY_INCR
            #returning False in on_error disconnects the stream
            # return False
            pass

if __name__ == '__main__':
    try:
        print(" // Establishing Bot Listener")
        BOT = ocrbot_stream()
        print(" // Initialising")
        session = BOT.local_init()
        print(" // Establishing Authorised Stream")
        botloop = tweepy.Stream(auth=BOT.auth, listener=BOT)
        print(" // Filter Stream")
        botloop.filter(track=[MYNAME,MAGICW],is_async=True)
        print(" // Done")
    except Exception as e:
        print(e)
