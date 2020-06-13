import textwrap

testStr = ""

## A word on the magic length
#
# Maximum tweet size is 280
# We want to add pagination " [00/00]" = 8 characters
# We need to start the chain with an @ to someone, maximum screen_name = 15
# So theoretical maximum is 280-8-15

# Although thinking about it, we also have "@" and " " around screen_name, so 17 is probably safer.
# Alsoif tweet exceeds 99 in a chain, it will break the pagination bit, but the maximum number of tweets in a chain is
# but Twitter limits threads to 25 anyway
MAGIC_VALUE=(280-8-17)

class Splitter:

    def forTweets( inText, splitLength=MAGIC_VALUE ):
        lines = textwrap.wrap(inText, splitLength, break_long_words=False)

        for i,s in enumerate(lines):
            lines[i] = lines[i] + " [{}/{}]".format((i+1),(len(lines)))

        return lines


if __name__ == '__main__':
    print(Splitter.forTweets(testStr))
