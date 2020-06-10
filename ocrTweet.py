# -*- coding: utf-8 -*-
import os
import sys
import tweepy
from splitter import Splitter
import ocrspace

from dotenv import load_dotenv,set_key
load_dotenv()

myname = "@ipoopmostly"
magicw = "ocrplz"

class ocrbot:
    def __init__(self):
        self.api       = self.setup_api()
        self.ocr_api   = ocrspace.API(os.getenv('OCR_KEY'))
        self.myLastRun = int(os.getenv("LAST_RUN",default=0))

    def setup_api(self):
        auth = tweepy.OAuthHandler(os.getenv('CONSUMER_KEY'), os.getenv('CONSUMER_SECRET')    )
        auth.set_access_token(     os.getenv('ACCESS_TOKEN'), os.getenv('ACCESS_TOKEN_SECRET'))
        return tweepy.API(auth)

    def post_tweet(self,contents="OCRBot empty message"):
        # api = setup_api()
        tweet = contents
        status = self.api.update_status(status=tweet)
        return 1

    def OCRImage(self,imageUrl):
        ocrResult    = self.ocr_api.ocr_url(imageUrl)
        tweetsToSend = Splitter.forTweets(ocrResult) # tweet length limits (280-8-15) user name and brackets
        return tweetsToSend

    def find_new_tasks(self):
        if self.myLastRun!=0:
            myMentions = self.api.mentions_timeline(since_id=self.myLastRun) # Have to store last run to stop repeated interactions [since_id][, max_id][, count])
        else:
            myMentions = self.api.mentions_timeline()

        print("New Tasks {}".format(len(myMentions)))
        for mention in myMentions:
            ## Limit this to mentions with the keyword
            if mention.id > self.myLastRun:
                set_key(".env","LAST_RUN",str(mention.id))
                self.myLastRun=mention.id

            splittext = mention.text.split()
            if not(myname in splittext and magicw in splittext):
                print("Tweet failed on inclusion criteria") #### <<<< This fails with multiple people in the thread - must do it better
                print(mention.text.split()[1:3])
                continue

            # print("Requestor {}\n Original Tweet Author {}\n Original Tweet {}\n".format(mention.author,mention.in_reply_to_screen_name,mention.in_reply_to_status_id))
            requestor = mention.author
            subjectAuthor_str = mention.in_reply_to_screen_name
            subjectTweetId    = mention.in_reply_to_status_id
            # mention.author is object of Requestor
            # mention.in_reply_to_screen_name is screen name of original author
            # mention.in_reply_to_status_id is numerical tweet id of tweet we are interested in.
            mediaFound = []
            print("Seeking tweet {}".format(subjectTweetId))
            subjectTweet = self.api.get_status(subjectTweetId, include_entities=True, tweet_mode='extended')
            # print(">>>>>{}<<<<<".format(subjectTweet))
            media = subjectTweet.entities.get('media', [])
            for img in media:
                if img["type"]=="photo":
                    mediaFound.append(img["media_url"])
                else:
                    print("ignoring {} as not photo".format(img))

            chainTo = mention.id;
            for task in mediaFound:
                # print("OCR on {}".format(task))
                for i,tweety in enumerate(self.OCRImage(task)):
                    # print("Tweet to send >>>>>{}<<<<<".format("@{} ".format(requestor.screen_name)+tweety) )
                    try:
                        if i==0:
                            newTweet = self.api.update_status(status=("@{} ".format(requestor.screen_name)+tweety), in_reply_to_status_id = chainTo )
                        else:
                            newTweet = self.api.update_status(status=(tweety)                                     , in_reply_to_status_id = chainTo )
                        chainTo = newTweet.id
                    except Exception as e:
                        print("Failed {}".format(e))
                        # pass



if __name__ == '__main__':
    OCR = ocrbot()

    OCR.find_new_tasks()
