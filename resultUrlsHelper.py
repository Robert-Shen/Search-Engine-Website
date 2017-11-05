import sqlite3
import pprint
import sys

'''
Instruction to use:
Input: The keywords strings that the user input
Output: A list of tuples with following format: [('url', 'title'), ('url2', 'title2'), ...]
        Note if a url does not have a title, then it is stored as ''

Example:
>>> results = resultUrls('engineering')
>>> pprint.pprint(results)
[('http://www.eecg.toronto.edu/Welcome.html',
  u'Computer Engineering Research Group'),
 ('http://www.ece.utoronto.ca',
  u'Home - Electrical & Computer Engineering | Electrical & Computer Engineering'),
 ('https://play.google.com/?hl=en&tab=w8', u'Google Play'),
 ('http://www.eecg.toronto.edu/~exec/student_guide/Main/index.shtml',
  u'EECG Student Guide'),
 ('http://www.eecg.toronto.edu/grads.html',
  u'Computer Engineering Group Graduate Students'),
 ('http://www.eecg.toronto.edu/faculty.html',
  u'Computer Engineering Group Faculty'),
 ('http://www.eecg.toronto.edu/tech_reports/index.html',
  u'Computer Engineering Research Group'),
 ('http://www.eecg.toronto.edu/facilities.html',
  u'Computer Engineering Group Research Facilities'),
 ('http://www.eecg.toronto.edu/projects.html',
  u'Computer Engineering Group Major Research Areas and Projects'),
 ('http://www.eecg.toronto.edu/', u'Computer Engineering Research Group')]
>>> results = resultUrls('google is good')
>>> pprint.pprint(results)
[('http://www.mapquest.com/maps/map.adp?countryid=41&addtohistory=&country=CA&address=10+King%27s+College+Road&city=Toronto&state=ON&zipcode=M5S+3G4&submit=Get+Map',
  u"10 King's College Rd - Toronto ON - MapQuest"),
 ('http://www.mapquest.com/maps?address=10+King%27s+College+Road&city=Toronto&state=ON&zipcode=M5S+3G4&country=CA',
  u"10 King's College Rd - Toronto ON - MapQuest"),
 ('http://www.ece.utoronto.ca',
  u'Home - Electrical & Computer Engineering | Electrical & Computer Engineering'),
 ('https://www.google.ca/intl/en/options/', u'Our products | Google'),
 ('http://www.google.ca/history/optout?hl=en',
  u'Google - Search Customization'),
 ('https://www.google.ca/preferences?hl=en', u'Preferences'),
 ('https://www.google.ca/intl/en/about.html', u'Our latest | Google'),
 ('https://mail.google.com/mail/?tab=wm', u'Gmail'),
 ('https://play.google.com/?hl=en&tab=w8', u'Google Play'),
 ('https://www.google.ca/imghp?hl=en&tab=wi', u'Google Images'),
 ('http://www.utoronto.ca', u'University of Toronto'),
 ('https://accounts.google.com/ServiceLogin?hl=en&passive=true&continue=https://www.google.ca/',
  u'Sign in - Google Accounts'),
 ('https://www.google.ca/setprefdomain?prefdom=US&sig=__rDMUHg-fiW8TV6VO4aVbE0OzIXs%3D',
  u'Google'),
 ('https://www.google.ca/', u'Google')]


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
            result.append((docId[2], unicode(docTitles[docId[0]])   ))
        else:
            result.append((docId[2], ''))

    # terminate db connetion and return
    dbConnection.close()
    return result

if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')

    result = resultUrls('engineering')
    pprint.pprint(result)
    result = resultUrls('google is good')
    pprint.pprint(result)