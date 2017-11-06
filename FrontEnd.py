import operator
from bottle import get, post, request, run, template, route, redirect, get,response,static_file,error
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import httplib2
from beaker.middleware import SessionMiddleware
import bottle
from resultUrlsHelper import resultUrls
############################################################################################
# If currently is testing on local machine, set this to True;
# before upload to AWS server, set this to False
isLocalServer = False
############################################################################################

globalKeywords = {}
CLIENT_ID="233110759621-pf3h9kl3ibncdvvdhkjcepvluedbuj2i.apps.googleusercontent.com"
CLIENT_SECRET="9x8veppsNgk0ZrGzxWy5RR-_"
SCOPE=['profile','email']
ROOT="http://ec2-52-5-119-86.compute-1.amazonaws.com"
REDIRECT_URI="http://ec2-52-5-119-86.compute-1.amazonaws.com/redirect"
cache=[]
if isLocalServer:
    ROOT="http://localhost:8080"
    REDIRECT_URI="http://localhost:8080/redirect"

session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 300,
    'session.data_dir': './data',
    'session.auto': True
}
app = SessionMiddleware(bottle.app(), session_opts)


@route('/<filename:path>')
def send_static(filename):
    return static_file(filename,root="css/")
@error(404)
def error404(error):
    return template("error")
# Initialize home page
@route('/result')
def redir():
    redirect(str('/'))
@route('/')
def login():
    global cache
    cache=request.url
    s = request.environ.get('beaker.session')
    if 'user' in s:
        email=s['user']
	loggin=1
    	if email not in globalKeywords:
            globalKeywords[email]={}
    else:
        loggin=0
    
    keywords = request.query.get('keywords')
    page_no = request.query.get('page_no')
    localKeywords = []
    localCount = []
    # If we dont receive any input keywords, return to home page

    if not keywords:
    	popularKeywords = None
    	if loggin:
	        if globalKeywords[email]:
	    	# Sort the dict into a list of tuples from small to large (according to value, not key)
	    	    sortedGlobalKywds = sorted(globalKeywords[email].items(),
	                                                       key=operator.itemgetter(1))
	    	# Reverse the list to start from large to small (according to value, not key)
	    	    popularKeywords = sortedGlobalKywds[::-1]

    	return template('home',
                        popularKeywords=popularKeywords,
                        loggin=loggin, 
                        userInfo=s, 
                        root=ROOT)
    else:
        lowerCase = keywords.lower().split()
        # Loop through every keyword in keywords string (lower cased )
        for word in lowerCase:
            if word not in localKeywords:
                # First store the appreance of each words in input string
                wordCount = lowerCase.count(word)
                localKeywords.append(word)
                localCount.append(wordCount)
            # Then update the wordCount for every keyword to determine the most popular 20 ones
            if loggin:
                if word in globalKeywords:
                    globalKeywords[email][word] = globalKeywords[email][word] + wordCount
                else:
                    globalKeywords[email][word] = wordCount
        response.set_header('Cache-Control', 'no-cache, no-store, max-age=0, must-revalidate')
        urls=resultUrls(keywords)
        if urls is not None:
            search = urls[(int(page_no) * 5 - 5):(int(page_no) * 5)]
            total = len(urls)/5

            if len(urls)%5 is not 0:
                total = total+1
            pagination=[None]*total
            for n in range(total):
                if (n+1) is int(page_no):
                    pagination[n]=('active',n+1)
                else:
                    pagination[n]=('None',n+1)
            return template('search',loggin=loggin,userInfo=s,pgn=pagination,srch=search,
                                keywords=keywords,currentpage=int(page_no),maxpage=total)
        else:
                return template('search',loggin=loggin,userInfo=s,pgn=[],srch=[],
                                keywords=keywords,currentpage=1,maxpage=1)
        '''
        return template('result', searchedKeywords=keywords,
                                  localKeywords=localKeywords, 
                                  localCount=localCount,
                                  loggin=loggin, 
                                  userInfo=s, 
                                  root=ROOT)
        '''
@route('/login')
def home():
    flow = flow_from_clientsecrets("client_secret_local.json",
                                  scope='https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email',
                                  redirect_uri=REDIRECT_URI)
    uri = flow.step1_get_authorize_url()
    redirect(str(uri))    
@route('/redirect')
def redirect_page():
    code = request.query.get('code','')
    flow = OAuth2WebServerFlow( client_id=CLIENT_ID,
 				client_secret=CLIENT_SECRET,
				scope=SCOPE,
				redirect_uri=REDIRECT_URI) 
    credentials = flow.step2_exchange(code)
    token = credentials.id_token['sub']
    http = httplib2.Http()
    http = credentials.authorize(http)
    # Get user email
    users_service = build('oauth2', 'v2', http=http)
    user_document = users_service.userinfo().get().execute()
    user_email = user_document['email']
    user_name = user_document['name']
    user_picture = user_document['picture']
    s = request.environ.get('beaker.session')
    s['user'] = user_email  
    s['name'] = user_name
    s['picture'] = user_picture
    s.save()
    redirect(str(cache))
@route('/logout')
def logout():
    s = request.environ.get('beaker.session')
    s.delete()
    redirect(str(cache))
# Start server
if isLocalServer:
    run(app=app,host='localhost', port=8080, debug=True)
else:
    run(app=app,host='0.0.0.0', port=80)
