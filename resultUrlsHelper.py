import sqlite3
import pprint
import sys
import textwrap

MAX_TITILE_LENGTH = 72

'''
Find the links that are related to the first keyword of input keywords string.
Return list [(url1, title1), (url2, title2), ...]
if title of the url not exist, then title = url
'''
def resultUrls(keywords):
    # parse keywords to extract the first keyword
    lowerCase = keywords.lower().split()
    keyword = lowerCase[0]

    # connect to db
    dbConnection = sqlite3.connect('myTable.db')
    dbConnection.text_factory = str
    cur = dbConnection.cursor()

    # we have 5 tables stored in the db:
    # lexicon: wordId (INTEGER PRIMARY KEY), word (TEXT)
    # documentId: docId (INTEGER PRIMARY KEY), url (TEXT)
    # invertedId: wordId (INTEGER), docId (INTEGER)
    # pageRankScores: docId (INTEGER), score (REAL)
    # docTitle: docId (INTEGER), title (TEXT)

    # get wordId from db
    cur.execute('SELECT wordId FROM lexicon WHERE word=?;', (keyword,))
    wordIdQuery = cur.fetchall()
    if len(wordIdQuery) == 0:
        return None
    wordId = wordIdQuery[0][0]

    # get set of docId by the particular wordId
    cur.execute(
        ''' SELECT docId, score, url
            FROM invertedId NATURAL JOIN pageRankScores
                            NATURAL JOIN documentId
            WHERE wordId=?;
        ''',
        (wordId,)
    )
    docIdQuery = cur.fetchall()

    if len(docIdQuery) == 0:
        print 'Nothing'
        return None
    docIds = list(set(docIdQuery))  # remove duplicated docId

    # sort docIds according to score
    # docIds is a list of tuples with format like [(docId, score, url),(docId2, score2, url2),...]
    docIds.sort(key=lambda tup: tup[1])
    docIds = docIds[::-1]  # change order from greatest to leastest

    # query titles
    cur.execute('SELECT * FROM docTitle;')
    docTitleQuery = cur.fetchall()
    docTitles = {}  # key: docID, value: title
    for item in docTitleQuery:
        docTitles[item[0]] = item[1]

    # append titles to urls
    result = []
    for docId in docIds:
        if docTitles.has_key(docId[0]):
            result.append((docId[2], ParsedTitle(docTitles[docId[0]])))
        else:
            result.append((docId[2], ParsedUrlTitle(docId[2])))

    # ========================  For testing purpose ======================
    # cur.execute('SELECT * FROM documentId')
    # a = cur.fetchall()
    # print len(a)
    # pprint.pprint(a)
    #
    # print '============================================================='
    # print '============================================================='
    #
    # cur.execute('SELECT * FROM docTitle')
    # b = cur.fetchall()
    # print len(b)
    # pprint.pprint(b)
    # ========================  For testing purpose ======================

    # terminate db connetion and return
    dbConnection.close()
    return result

'''
Trim the title of url to a limited number of chars (specified by MAX_TITILE_LENGTH)
'''
def ParsedTitle(title):
    if len(title) > MAX_TITILE_LENGTH:
        trimedTitle = textwrap.wrap(title, MAX_TITILE_LENGTH, break_long_words=False)
        title = trimedTitle[0] + ' ...'
    return title

'''
Trim the url to a limited number of chars (specified by MAX_TITILE_LENGTH)
'''
def ParsedUrlTitle(url):
    if len(url) > MAX_TITILE_LENGTH:
        trimedUrl = url[0:MAX_TITILE_LENGTH]
        url = trimedUrl + '...'
    return url

if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')

    result = resultUrls('engineering is awesome')
    pprint.pprint(result)
    # result = resultUrls('google is good')
    # pprint.pprint(result)
