# -*- coding: utf-8 -*-
import os
import sys
import tweepy
from splitter import Splitter
from ocrspace import API
import time
from random import random

from dotenv import load_dotenv,set_key
load_dotenv()

myname    = os.getenv('TWITTER_SN') # # Twitter account screenname prefixed with @
magicw    = os.getenv('TWITTER_MW') # # Phrase that must be present to perform ocr
# Messgaes to sponsors & thanks

DEBUG     = False
DontPost  = False

useThanks = (DEBUG)?False:True
thankstxt = "Service is able to run with the kind help of pythonanywhere.com @pythonanywhere"

class ocrbot:
    def __init__(self):
        # Setup the API for Twitter, ocr.space and try to find a previous run env var
        self.api       = self.setup_api()
        ocrParams      = {
            'detectOrientation':"true",
            'scale'            :"true"
        }
        self.ocr_api   = API(api_key=os.getenv('OCR_KEY'), language='eng', **ocrParams)
        self.myLastRun = int(os.getenv("LAST_RUN",default=0))

    def setup_api(self):
        # Create OAuth link to twitter
        auth = tweepy.OAuthHandler(os.getenv('CONSUMER_KEY'), os.getenv('CONSUMER_SECRET')    )
        auth.set_access_token(     os.getenv('ACCESS_TOKEN'), os.getenv('ACCESS_TOKEN_SECRET'))
        return tweepy.API(auth)

    def OCRImage(self,imageUrl):
        # Call ocr.space API, wait and return list of tweets
        ocrResult    = self.ocr_api.ocr_url(imageUrl)
        tweetsToSend = Splitter.forTweets(ocrResult) # tweet length limits (280-8-15) user name and brackets
        print(" Tweet chain length {}".format(len(tweetsToSend)))
        return tweetsToSend

    def find_new_tasks(self):
        # If we have run before, only look for tweets since last run
        if self.myLastRun!=0:
            myMentions = self.api.mentions_timeline(since_id=self.myLastRun)
        else:
            myMentions = self.api.mentions_timeline()

        # Log the results
        print("New Tasks {}".format(len(myMentions)))

        for mention in myMentions:
            ## Keep updateing the last run variables with each new message to prevent duplication
            if mention.id > self.myLastRun:
                set_key(".env","LAST_RUN",str(mention.id))
                self.myLastRun=mention.id
            # Check for account name and magic phrase in this request
            splittext = mention.text.split()
            if not(myname in splittext and magicw in splittext):
                print("Tweet failed on inclusion criteria {}".format(mention.id))
                # We didn't find a correct request so move along
                continue

            # print("Requestor {}\n Original Tweet Author {}\n Original Tweet {}\n".format(mention.author,mention.in_reply_to_screen_name,mention.in_reply_to_status_id))
            requestor         = mention.author                      # User obj of requestor
            subjectAuthor_str = mention.in_reply_to_screen_name     # Screen name of target tweet author
            subjectTweetId    = mention.in_reply_to_status_id       # Target tweet id

            # Generate empty list to hold all found images
            mediaFound = []
            print("Seeking tweet {}".format(subjectTweetId))
            # Get the EXTENDED version of the tweet
            subjectTweet = self.api.get_status(subjectTweetId, include_entities=True, tweet_mode='extended')
            # Drill into any media
            # if DEBUG: print(subjectTweet)
            media = subjectTweet.extended_entities.get('media', []) ## Fixes #5, entities did not include all images
            for img in media:
                if img["type"]=="photo":
                    mediaFound.append(img["media_url"])
                else:
                    print("ignoring {} as not photo".format(img))

            if DEBUG: print("  {} Found {} images".format(subjectTweetId, len(mediaFound)))
            # Tweeting will be in a chain,so we need to start the chain from original tweet
            chainTo = mention.id;
            for task in mediaFound:
                # send image for OCR and get back a list of tweets
                if DEBUG: print(" {} OCR image {}".format(subjectTweetId, task))
                try:
                    for i,tweety in enumerate(self.OCRImage(task)):
                    ##
                    # Try to send each tweet in the chain
                        # FIX : #5
                        # Chain to will be last tweet in a chain for a given image, but first tweet of new image is probably "@" wrong person.
                        if DEBUG: print("  {}.".format(i), end="")
                        if DontPost:
                            continue
                        if i==0:
                            # First tweet must tag the requestor
                            newTweet = self.api.update_status(status=("@{} ".format(requestor.screen_name)+tweety), in_reply_to_status_id = chainTo )
                        elif i%24==0:
                            # create new quote tweet
                            newTweet = self.api.update_status(status="https://twitter.com/{}/status/{}".format(myname, chainTo))
                            chainTo  = newTweet.id
                            # Continue as thread to that
                            newTweet = self.api.update_status(status=(tweety)                                     , in_reply_to_status_id = chainTo )
                        else:
                            newTweet = self.api.update_status(status=(tweety)                                     , in_reply_to_status_id = chainTo )
                        chainTo = newTweet.id
                    time.sleep(random()) # random sleep so we appear a *tiny* bit less bot-y

                except Exception as e:
                    print("Failed OCR : {}".format(e))
                        # pass
            # Add thanks tweet
            # FIXES : #4
            if useThanks:
                self.api.update_status(status=thankstxt, in_reply_to_status_id = chainTo)

if __name__ == '__main__':
    OCR = ocrbot()

    OCR.find_new_tasks()
