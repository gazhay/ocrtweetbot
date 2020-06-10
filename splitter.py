import textwrap

testStr = """Keir Starmer: "It shouldn't have been done in that way. It's completely wrong to pull a
statue down like that but stepping back, that statue should have been taken down a long,
long time ago.
can't in 21st Century Britain have a slaver on a statue — a statue is there to honour
people.
can't have that in 21st Century Britain. That statue should have been brought down
properly with consent and put, I would say, in a museum.
"This was a man who was responsible for 100,000 people being moved from Africa to the
Caribbean as slaves, including women and children, who were branded on their chests
with the name of the company that he ran.
"Of the 100,000, 20,000 died en route and they were chucked in the sea. He should not be
on a statue in Bristol or anywhere else.
"He should be in a museum because we need to understand thk but it should have been
taken down a long time ago."
"""

class Splitter:

    def forTweets( inText, splitLength=(280-8-15) ):
        lines = textwrap.wrap(inText, splitLength, break_long_words=False)

        for i,s in enumerate(lines):
            lines[i] = lines[i] + " [{}/{}]".format((i+1),(len(lines)))

        return lines


if __name__ == '__main__':
    print(Splitter.forTweets(testStr))
