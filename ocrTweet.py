# -*- coding: utf-8 -*-
import os
import sys
import tweepy
from splitter import Splitter
import ocrspace

from dotenv import load_dotenv,set_key
load_dotenv()

myname    = "@ocrbot1" # Twitter account screenname prefixed with @
magicw    = "ocrplz"   # Phrase that must be present to perform ocr
# Messgaes to sponsors & thanks
thankstxt = "Service is able to run with the kind help of pythonanywhere.com @pythonanywhere"

class ocrbot:
    def __init__(self):
        # Setup the API for Twitter, ocr.space and try to find a previous run env var
        self.api       = self.setup_api()
        self.ocr_api   = ocrspace.API(os.getenv('OCR_KEY'))
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
            media = subjectTweet.entities.get('media', [])
            for img in media:
                if img["type"]=="photo":
                    mediaFound.append(img["media_url"])
                else:
                    print("ignoring {} as not photo".format(img))

            # Tweeting will be in a chain,so we need to start the chain from original tweet
            chainTo = mention.id;
            for task in mediaFound:
                # send image for OCR and get back a list of tweets
                for i,tweety in enumerate(self.OCRImage(task)):
                    ##
                    # Try to send each tweet in the chain
                    try:
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
                    except Exception as e:
                        print("Failed {}".format(e))
                        # pass
                    # Add thanks tweet
                    self.api.update_status(status=thankstxt, in_reply_to_status_id = chainTo)


if __name__ == '__main__':
    OCR = ocrbot()

    OCR.find_new_tasks()
