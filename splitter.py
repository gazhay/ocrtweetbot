import textwrap

testStr = ""

class Splitter:

    def forTweets( inText, splitLength=(280-8-15) ):
        lines = textwrap.wrap(inText, splitLength, break_long_words=False)

        for i,s in enumerate(lines):
            lines[i] = lines[i] + " [{}/{}]".format((i+1),(len(lines)))

        return lines


if __name__ == '__main__':
    print(Splitter.forTweets(testStr))
