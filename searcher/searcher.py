import sqlite3
import pprint
import sys
import textwrap
from math import *
from os.path import *

MAX_TITILE_LENGTH = 72

'''
Find the links that are related to the first keyword of input keywords string.
Return list [(url1, title1), (url2, title2), ...]
if title of the url not exist, then title = url
'''
def GetResults(seachString):
    # parse keywords to extract the first keyword
    lowerCase = seachString.lower().split()

    # ignore stopwords
    curPath = abspath(__file__)
    rootDir = abspath(dirname(dirname(curPath)))
    stopwordsFile = r'%s/crawlerAndPagerank/stopwords.txt' % rootDir
    ignoredWordsFile = open(stopwordsFile, 'r')
    ignoredWords = [line.strip('\n') for line in ignoredWordsFile.readlines()]
    ignoredWordsFile.close()

    # store valid keywords, not allow duplicated keywords
    keywords = set()
    for word in lowerCase:
        if word not in ignoredWords:
            keywords.add(word)

    # connect to db
    dbConnection = sqlite3.connect('database.db')
    dbConnection.text_factory = str
    cur = dbConnection.cursor()

    # we have 7 tables stored in the db:
    # lexicon: wordId (INTEGER PRIMARY KEY), word (TEXT)
    # documentId: docId (INTEGER PRIMARY KEY), url (TEXT)
    # invertedId: wordId (INTEGER), docId (INTEGER)
    # pageRankScores: docId (INTEGER), score (REAL)
    # docTitle: docId (INTEGER), title (TEXT)
    # docWordHits: docId (INTEGER), wordId (INTEGER), fontSize (INTEGER), wordLocation (INTEGER)
    # docAnchorHits: docId (INTEGER), wordId (INTEGER), anchorFontSize (INTEGER)

    rawDocIds = []
    rawWordHits = []
    rawCacheHits = []
    for word in keywords:
        curDocIds = GetDocInfoByWord(cur, word)
        if curDocIds is not None:
            rawDocIds.append(curDocIds)

        curWordHits = GetWordHitsByWord(cur, word)
        if curWordHits is not None:
            rawWordHits.append(curWordHits)

        curCacheHits = GetCacheHitsByWord(cur, word)
        if curCacheHits is not None:
            rawCacheHits.append(curCacheHits)

    # determine specific docIds that contain entire wordIds or one less of entire wordIds
    countDocIds = {}
    docIdToUrl = {} # map docId to its url
    baseScores = {} # map docId to its raw pagerank score
    for docIdsForWord in rawDocIds:
        for docTuple in docIdsForWord:
            if docTuple[0] not in countDocIds.keys():
                countDocIds[docTuple[0]] = 1
            else:
                countDocIds[docTuple[0]] += 1

            if docTuple[0] not in docIdToUrl.keys():
                docIdToUrl[docTuple[0]] = docTuple[1]
            if docTuple[0] not in baseScores.keys():
                baseScores[docTuple[0]] = docTuple[2]

    # narrow down to valid docIds who contains expected keywords
    validDocIds = []
    NUM_KEYWORDS = len(rawDocIds)
    MIN_EXPECTED_APPEAR_OF_KEYWORDS = NUM_KEYWORDS-1 if NUM_KEYWORDS > 2 else 1
    for rawDocId,numAppear in countDocIds.items():
        if numAppear >= MIN_EXPECTED_APPEAR_OF_KEYWORDS:
            validDocIds.append(rawDocId)
    print '>>>>>>>>>>>>>>>>>'
    print validDocIds

    docWithWordHits = {} # key: docId, value: [(wordIndex, fontSize, wordLocation), (wordIndex, fontSize, wordLocation), ...]
    wordIndex = 0
    for wordHitsForWord in rawWordHits:
        curWordIndex = wordIndex
        for wordHitTuple in wordHitsForWord:
            # (docId, fontSize, wordLocation)
            curDocId = wordHitTuple[0]
            if curDocId in validDocIds:
                curFontSize = wordHitTuple[1]
                curWordLocation = wordHitTuple[2]
                if curDocId not in docWithWordHits.keys():
                    docWithWordHits[curDocId] = [(curWordIndex, curFontSize, curWordLocation)]
                else:
                    docWithWordHits[curDocId].append((curWordIndex, curFontSize, curWordLocation))
        wordIndex += 1

    # calcuate the proximity score for each doc
    # we expect the proximity of keywords within 8 wording distance from each other
    PROXIMITY_WITHIN = 8
    proximityScores = {} # key: docId, value: proximity score
    docSnippet = {} # key: docId, value: proximity location
    for docId,doc in docWithWordHits.items():
        doc.sort(key=lambda tup: tup[2]) # sorted by wordLocation

        t = 0 # currentPtr
        while t <= (len(doc)-NUM_KEYWORDS):
            check = []
            for i in range(NUM_KEYWORDS):
                check.append(doc[t+i])

            # check1: number of different wordIndex must >= MIN_EXPECTED_APPEAR_OF_KEYWORDS
            check1 = set()
            for i in check:
                check1.add(i[0])
            if len(check1) < MIN_EXPECTED_APPEAR_OF_KEYWORDS:
                t += 1
                continue

            if MIN_EXPECTED_APPEAR_OF_KEYWORDS > 2: # expect proximity
                # check2: different keywords must appear within 8 words distance
                PROXIMITY_GOAL = MIN_EXPECTED_APPEAR_OF_KEYWORDS-2
                isPass = False
                m = 0
                n = 1
                numProximity = 0
                while n < len(check):
                    mm = check[m]
                    nn = check[n]
                    if mm[0] == nn[0]: # same words
                        m += 1
                        n += 1
                        continue
                    else: # different words
                        distance_m_n = nn[2] - mm[2]
                        if distance_m_n <= 8:
                            numProximity += 1
                        m += 1
                        n += 1
                if numProximity >= PROXIMITY_GOAL:
                    averageFontSize = reduce(lambda x,y: x[1]+y[1], check)
                    proximityScore = numProximity * averageFontSize
                    if docId not in proximityScores.keys():
                        proximityScores[docId] = proximityScore
                    else:
                        proximityScores[docId] += proximityScore
                    t += NUM_KEYWORDS
                else:
                    t += 1
            else: # does not expect proximity, using single word is good enough
                averageFontSize = check[0][1]
                if len(check) > 1:
                    averageFontSize = reduce(lambda x,y: x[1]+y[1], check)
                proximityScore = len(check) * averageFontSize
                if docId not in proximityScores.keys():
                    proximityScores[docId] = proximityScore
                else:
                    proximityScores[docId] += proximityScore
                t += NUM_KEYWORDS


    # get cache hits of doc
    # note that not all doc has cache hits
    cacheScores = {}
    for cacheHits in rawCacheHits:
        for cacheHit in cacheHits:
            docId = cacheHit[0]
            hit = cacheHit[0]
            if docId not in cacheScores.keys():
                cacheScores[docId] = hit
            else:
                cacheScores[docId] += hit

    # calculate final pagerank for validDocIds
    # validDocIds: baseScores proximityScores cacheScores
    finalPagerank = []
    for docId in validDocIds:
        baseScore = baseScores[docId] if docId in baseScores.keys() else 0
        proximityScore = proximityScores[docId] if docId in proximityScores.keys() else 0
        cacheScore = cacheScores[docId] if docId in cacheScores.keys() else 0
        finalPagerank.append((docId, baseScore, proximityScore, cacheScore))
    # normalize proximityScore
    totalProximityScore = reduce(lambda x,y: (0,0,x[2]+y[2]), finalPagerank)[2]
    finalPagerank = map(lambda x: (x[0], x[1], float(float(x[2])/float(totalProximityScore)/float(10)), x[3]), finalPagerank)
    # normalize cacheScore
    totalCacheScore = reduce(lambda x,y: (0,0,0,x[3]+y[3]), finalPagerank)[3]
    finalPagerank = map(lambda x: (x[0], x[1], x[2], float(float(x[3])/float(totalCacheScore)/float(10))), finalPagerank)
    # compute final score
    finalPagerank = map(lambda x: (x[0], float(sqrt(pow(x[1], 2) + pow(x[2], 2) + pow(x[3], 2)))), finalPagerank)
    finalPagerank.sort(key=lambda tup: tup[1])
    finalPagerank = finalPagerank[::-1]  # change order from greatest to leastest

    pprint.pprint(finalPagerank)

    # add titles
    docTitles = GetAllTitles(cur) # key: docID, value: title

    # append titles to urls
    result = []
    for page in finalPagerank:
        docId = page[0]
        docUrl = docIdToUrl[docId]
        if docTitles.has_key(docId):
            result.append((docUrl, ParsedTitle(docTitles[docId])))
        else:
            result.append((docUrl, ParsedUrlTitle(docUrl)))

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

def GetDocInfoByWord(cur, word):
    # lexicon: wordId (INTEGER PRIMARY KEY), word (TEXT)
    # invertedId: wordId (INTEGER), docId (INTEGER)
    # documentId: docId (INTEGER PRIMARY KEY), url (TEXT)
    # pageRankScores: docId (INTEGER), score (REAL)
    cur.execute(
        ''' SELECT docId, url, score
            FROM lexicon NATURAL JOIN invertedId
                         NATURAL JOIN documentId
                         NATURAL JOIN pageRankScores
            WHERE word=?;
        ''', (word,))
    query = cur.fetchall()
    if len(query) > 0:
        return [(q[0], q[1], q[2]) for q in query]
    else:
        return None

def GetWordHitsByWord(cur, word):
    # lexicon: wordId (INTEGER PRIMARY KEY), word (TEXT)
    # invertedId: wordId (INTEGER), docId (INTEGER)
    # docWordHits: docId (INTEGER), wordId (INTEGER), fontSize (INTEGER), wordLocation (INTEGER)
    cur.execute(
        ''' SELECT docId, fontSize, wordLocation
            FROM lexicon NATURAL JOIN invertedId
                         NATURAL JOIN docWordHits
            WHERE word=?;
        ''', (word,))
    query = cur.fetchall()
    if len(query) > 0:
        return [(q[0], q[1], q[2]) for q in query]
    else:
        return None

def GetCacheHitsByWord(cur, word):
    # lexicon: wordId (INTEGER PRIMARY KEY), word (TEXT)
    # invertedId: wordId (INTEGER), docId (INTEGER)
    # docAnchorHits: docId (INTEGER), wordId (INTEGER), anchorFontSize (INTEGER)
    cur.execute(
        ''' SELECT docId, anchorFontSize
            FROM lexicon NATURAL JOIN invertedId
                         NATURAL JOIN docAnchorHits
            WHERE word=?;
        ''', (word,))
    query = cur.fetchall()
    if len(query) > 0:
        return [(q[0], q[1]) for q in query]
    else:
        return None

def GetAllTitles(cur):
    # docTitle: docId (INTEGER), title (TEXT)
    cur.execute('SELECT * FROM docTitle;')
    cur.execute(
        ''' SELECT *
            FROM docTitle;
        ''')
    query = cur.fetchall()
    docTitles = {}  # key: docID, value: title
    for q in query:
        docTitles[q[0]] = q[1]
    return docTitles

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

    result = GetResults('computer engineering')
    pprint.pprint(result)
    # result = GetResults('google is good')
    # pprint.pprint(result)
