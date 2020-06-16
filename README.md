# OcrTweetBot

A simple bot which attempts to OCR images and tweet the resulting text as a thread.

## Dependencies
tweepy
python-dotenv
~~ocrspace~~

ocrspace is no longer an external dependency as the latest version wasn't available on pypy.
It is duplicated inside this project with credit to https://github.com/ErikBoesen/ocrspace

## Requirements
Twitter account & developer account
ocrspace free (or pro) API key

Create a file called .env in the working directory of the script with the following variables filled out

````
CONSUMER_KEY='<TWITTER KEY>'
CONSUMER_SECRET='<TWITTER KEY>'
ACCESS_TOKEN='<TWITTER KEY>'
ACCESS_TOKEN_SECRET='<TWITTER KEY>'
OCR_KEY='<OCRSPACE KEY>'


TWITTER_SN="@<TWITTER SCREEN NAME>"
TWITTER_MW="<MAGIC PHRASE>"
````

MAGIC PHRASE is something like "ocrplz".

Then run the script at whatever intervals the APIs will allow you.

The bot looks through its mentions from the last seen mention, if it finds the magic keyword it will attempt to find images, ocr them and send replies to whoever requested the bot to work with the text it finds.

This is **alpha** quality work. It does *enough* to work in the narrow cases it has been tested with. (@theousherwood tweets and one from the poke).

It would be trivial to trip it up and it has little error handling or reporting.

I also **don't** have the resources to host and run this beyond the free tier of API access to both twitter and OCRSpace. These will get used up fairly quickly, that's why it is here on github.

It would be good if twitter would go beyond their current model of opt-in image descriptions. Making them mandatory would be great. Automatically OCRing images like this bot aims to do would also be great, both well within the resources of the company.

# Out in the wild

It is currently running on the account @ocrbot1 on twitter.
