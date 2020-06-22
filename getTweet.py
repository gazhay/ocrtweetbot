#!/usr/bin/python3
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

class ocrHelper:
    def __init__(self):
        # Setup the API for Twitter, ocr.space and try to find a previous run env var
        self.api       = self.setup_api()

    def setup_api(self):
        # Create OAuth link to twitter
        auth = tweepy.OAuthHandler(os.getenv('CONSUMER_KEY'), os.getenv('CONSUMER_SECRET')    )
        auth.set_access_token(     os.getenv('ACCESS_TOKEN'), os.getenv('ACCESS_TOKEN_SECRET'))
        return tweepy.API(auth)

    def getTweet(self, id):
        print(self.api.get_status(id))

if __name__ == '__main__':
    OCR = ocrHelper()

    OCR.getTweet(sys.argv[1])
