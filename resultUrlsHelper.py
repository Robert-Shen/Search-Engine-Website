import sqlite3
import pprint
import sys

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
    docIds = list(set(docIdQuery)) # remove duplicated docId
    
    # sort docIds according to score
    # docIds is a list of tuples with format like [(docId, score, url),(docId2, score2, url2),...]
    docIds.sort(key=lambda tup: tup[1])
    docIds = docIds[::-1] # change order from greatest to leastest

    # query titles
    cur.execute('SELECT * FROM docTitle;')
    docTitleQuery = cur.fetchall()
    docTitles = {} # key: docID, value: title
    for item in docTitleQuery:
        docTitles[item[0]] = item[1]

    # append titles to urls
    result = []
    for docId in docIds:
        if docTitles.has_key(docId[0]):
            result.append((docId[2], docTitles[docId[0]]))
        else:
            result.append((docId[2], docId[2]))

    # ========================  For testing purpose ======================
    # cur.execute('SELECT * FROM documentId')
    # a = cur.fetchall()
    # print len(a)
    # pprint.pprint(a)

    # print '============================================================='
    # print '============================================================='

    # cur.execute('SELECT * FROM docTitle')
    # b = cur.fetchall()
    # print len(b)
    # pprint.pprint(b)
    # ========================  For testing purpose ======================

    # terminate db connetion and return
    dbConnection.close()
    return result

if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')

    result = resultUrls('engineering is awesome')
    pprint.pprint(result)
    # result = resultUrls('google is good')
    # pprint.pprint(result)