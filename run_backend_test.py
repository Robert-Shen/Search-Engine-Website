import crawler
import sqlite3
import pprint

def testLab3CrawlerWithPageRank():
    print "===============================================================" 
    print '> Test page rank socres and presistent storage'
    print ''

    print '> Initialize the sqlite3 database connection'
    dbConnection = sqlite3.connect('myTable.db')
    dbConnection.text_factory = str
    print '> Start to initialize crawler'
    crawlerTest = crawler.crawler(dbConnection, "urls.txt")
    print '> Start crawling...'
    crawlerTest.crawl(depth=1)
    print '> Crawler is done'
    dbConnection.close()
    print '> DB connection is closed'

    print '> Start to read from presistent storage'
    print '> Initialize DB connection'
    dbConnection = sqlite3.connect('myTable.db')
    
    # we have 5 tables stored in the db:
    # lexicon: wordId (INTEGER PRIMARY KEY), word (TEXT)
    # documentId: docId (INTEGER PRIMARY KEY), url (TEXT)
    # invertedId: wordId (INTEGER), docId (INTEGER)
    # pageRankScores: docId (INTEGER), score (REAL)
    # docTitle: docId (INTEGER), title (TEXT)

    print "==============================================================="
    cur = dbConnection.cursor()
    cur.execute(
        '''
        SELECT * FROM pageRankScores;
        '''
    )
    pageRankScores = cur.fetchall()
    print '> Print the "docId" with their "score" below:'
    pprint.pprint(pageRankScores)
    print ''

    print "==============================================================="
    cur.execute(
        '''
        SELECT * FROM documentId;
        '''
    )
    documentIds = cur.fetchall()
    print '> Print the "docId" with their "url" below:'
    pprint.pprint(documentIds)
    print ''

    print "==============================================================="
    cur.execute(
        '''
        SELECT url, score FROM documentId NATURAL JOIN pageRankScores;
        '''
    )
    urlScores = cur.fetchall()
    print '> Print the "url" with their "score" below:'
    pprint.pprint(urlScores)
    print ''

    dbConnection.close()
    print '> Done, DB connection close'

if __name__ == "__main__":
    testLab3CrawlerWithPageRank()
    print ""
    print ""
    print ""
    print "Exit test!"