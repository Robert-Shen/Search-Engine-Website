# Copyright (C) 2011 by Peter Goodman
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import urllib2
import urlparse
from BeautifulSoup import *
from collections import defaultdict
import re
import sqlite3
import HTMLParser
import unicodedata
import pagerank
from os.path import abspath, dirname

def attr(elem, attr):
    """An html attribute from an html element. E.g. <a href="">, then
    attr(elem, "href") will get the href or an empty string."""
    try:
        return elem[attr]
    except:
        return ""

WORD_SEPARATORS = re.compile(r'\s|\n|\r|\t|[^a-zA-Z0-9\-_]')

class crawler(object):
    """Represents 'Googlebot'. Populates a database by crawling and indexing
    a subset of the Internet.

    This crawler keeps track of font sizes and makes it simpler to manage word
    ids and document ids."""

    def __init__(self, db_conn, url_file):
        """Initialize the crawler with a connection to the database to populate
        and with the file containing the list of seed URLs to begin indexing."""
        self._url_queue = [ ] # record all urls
        self._doc_id_cache = { } # key: url, value: docId
        self._word_id_cache = { } # key: word, value: wordId

        ########################################################################

        # used to look up a list of URLs given a keyword
        # key: word id, value: set of document ids
        self._inverted_index = { }
        # key: word string, value: set of URL strings
        self._resolved_inverted_index = { }
        # lab3: data structure that passed to pageRank algorithm
        # value: pair of (from_link_docId, to_link_docId)
        self._from_to_links = []
        # lab3: cache to store titles of docId
        # key: docId, value: set of titles
        self._doc_title_cache = { }
        # lab4: cache to store every word hits of docId
        # key: docId, value: list of (wordId, relativeFontSize, wordLocation)
        self._doc_wordHits_cache = {}
        # lab4: cache to store anchor hits of the links
        # Anchor hits are the text of the link, the text reveals more info about
        # the dest link and therefore weighted higher
        # Key: docId, value: list of (wordId, anchorFontSize=10)
        self._doc_anchorHits_cache = {}
        # lab4: cache to store a snippet of docId
        # key: docId, value: text of snippet
        self._doc_snippet_cache = {}

        # start db connection
        self.db_conn = db_conn
        self.cur = db_conn.cursor()

        # we have 8 tables stored in the db:
        # lexicon: wordId (INTEGER PRIMARY KEY), word (TEXT)
        # documentId: docId (INTEGER PRIMARY KEY), url (TEXT)
        # invertedId: wordId (INTEGER), docId (INTEGER)
        # pageRankScores: docId (INTEGER), score (REAL)
        # docTitle: docId (INTEGER), title (TEXT)
        # docWordHits: docId (INTEGER), wordId (INTEGER), fontSize (INTEGER), wordLocation (INTEGER)
        # docAnchorHits: docId (INTEGER), wordId (INTEGER), anchorFontSize (INTEGER)
        # docSnippet: docId (INTEGER), snippet (TEXT)

        # restart db every run the crawler
        self.cur.executescript(
            '''
            DROP TABLE IF EXISTS lexicon;
            DROP TABLE IF EXISTS documentId;
            DROP TABLE IF EXISTS invertedId;
            DROP TABLE IF EXISTS pageRankScores;
            DROP TABLE IF EXISTS docTitle;
            DROP TABLE IF EXISTS docWordHits;
            DROP TABLE IF EXISTS docAnchorHits;
            DROP TABLE IF EXISTS docSnippet;
            '''
        )

        ########################################################################

        # functions to call when entering and exiting specific tags
        self._enter = defaultdict(lambda *a, **ka: self._visit_ignore)
        self._exit = defaultdict(lambda *a, **ka: self._visit_ignore)

        # add a link to our graph, and indexing info to the related page
        self._enter['a'] = self._visit_a

        # record the currently indexed document's title and increase
        # the font size
        def visit_title(*args, **kargs):
            self._visit_title(*args, **kargs)
            self._increase_font_factor(7)(*args, **kargs)

        # increase the font size when we enter these tags
        self._enter['b'] = self._increase_font_factor(2)
        self._enter['strong'] = self._increase_font_factor(2)
        self._enter['i'] = self._increase_font_factor(1)
        self._enter['em'] = self._increase_font_factor(1)
        self._enter['h1'] = self._increase_font_factor(7)
        self._enter['h2'] = self._increase_font_factor(6)
        self._enter['h3'] = self._increase_font_factor(5)
        self._enter['h4'] = self._increase_font_factor(4)
        self._enter['h5'] = self._increase_font_factor(3)
        self._enter['title'] = visit_title

        # decrease the font size when we exit these tags
        self._exit['b'] = self._increase_font_factor(-2)
        self._exit['strong'] = self._increase_font_factor(-2)
        self._exit['i'] = self._increase_font_factor(-1)
        self._exit['em'] = self._increase_font_factor(-1)
        self._exit['h1'] = self._increase_font_factor(-7)
        self._exit['h2'] = self._increase_font_factor(-6)
        self._exit['h3'] = self._increase_font_factor(-5)
        self._exit['h4'] = self._increase_font_factor(-4)
        self._exit['h5'] = self._increase_font_factor(-3)
        self._exit['title'] = self._increase_font_factor(-7)

        # never go in and parse these tags
        self._ignored_tags = set([
            'meta', 'script', 'link', 'meta', 'embed', 'iframe', 'frame',
            'noscript', 'object', 'svg', 'canvas', 'applet', 'frameset',
            'textarea', 'style', 'area', 'map', 'base', 'basefont', 'param',
        ])

        # set of words to ignore
        curPath = abspath(__file__)
        dirPath = abspath(dirname(curPath))
        stopwordsFile = r'%s/stopwords.txt' % dirPath
        ignoredWordsFile = open(stopwordsFile, 'r')
        ignoredWords = [line.strip('\n') for line in ignoredWordsFile.readlines()]
        ignoredWordsFile.close()
        self._ignored_words = ignoredWords

        # TODO remove me in real version
        self._mock_next_doc_id = 1
        self._mock_next_word_id = 1

        # keep track of some info about the page we are currently parsing
        self._curr_depth = 0
        self._curr_url = ""
        self._curr_doc_id = 0
        self._font_size = 0
        self._curr_words = None

        # get all urls into the queue
        try:
            with open(url_file, 'r') as f:
                for line in f:
                    self._url_queue.append((self._fix_url(line.strip(), ""), 0))
        except IOError:
            pass

    # TODO remove me in real version
    def _mock_insert_document(self, url):
        """A function that pretends to insert a url into a document db table
        and then returns that newly inserted document's id."""
        ret_id = self._mock_next_doc_id
        self._mock_next_doc_id += 1
        return ret_id

    # TODO remove me in real version
    def _mock_insert_word(self, word):
        """A function that pretends to inster a word into the lexicon db table
        and then returns that newly inserted word's id."""
        ret_id = self._mock_next_word_id
        self._mock_next_word_id += 1
        return ret_id

    def word_id(self, word):
        """Get the word id of some specific word."""
        if word in self._word_id_cache:
            return self._word_id_cache[word]

        # TODO: 1) add the word to the lexicon, if that fails, then the
        #          word is in the lexicon
        #       2) query the lexicon for the id assigned to this word,
        #          store it in the word id cache, and return the id.

        word_id = self._mock_insert_word(word)
        self._word_id_cache[word] = word_id
        self._inverted_index[word_id]=set() #lab1--new word id: empty set of inverted indexs (of document ids)
        return word_id

    def document_id(self, url):
        """Get the document id for some url."""
        if url in self._doc_id_cache:
            return self._doc_id_cache[url]

        # TODO: just like word id cache, but for documents. if the document
        #       doesn't exist in the db then only insert the url and leave
        #       the rest to their defaults.

        doc_id = self._mock_insert_document(url)
        self._doc_id_cache[url] = doc_id
        return doc_id

    def _fix_url(self, curr_url, rel):
        """Given a url and either something relative to that url or another url,
        get a properly parsed url."""

        rel_l = rel.lower()
        if rel_l.startswith("http://") or rel_l.startswith("https://"):
            curr_url, rel = rel, ""

        # compute the new url based on import
        curr_url = urlparse.urldefrag(curr_url)[0]
        parsed_url = urlparse.urlparse(curr_url)
        return urlparse.urljoin(parsed_url.geturl(), rel)

    def add_link(self, elem, from_doc_id, to_doc_id):
        """Add a link into the database, or increase the number of links between
        two pages in the database."""
        # record from link and to link for pagerank
        self._from_to_links.append((from_doc_id, to_doc_id))

        # record anchor hits
        string = elem.string
        if string is None:
            return
        words = WORD_SEPARATORS.split(elem.string.lower())
        curr_anchors = []
        for word in words:
            word = word.strip()
            if word in self._ignored_words:
                continue
            # record (wordIds, anchorFontSize) of anchor
            curr_anchors.append((self.word_id(word), 10))

        if to_doc_id not in self._doc_anchorHits_cache.keys():
            self._doc_anchorHits_cache[to_doc_id] = curr_anchors
        else:
            self._doc_anchorHits_cache[to_doc_id] += curr_anchors

    def _visit_title(self, elem):
        """Called when visiting the <title> tag."""
        title_text = self._text_of(elem).strip()
        # print "document title="+ repr(title_text)

        # TODO update document title for document id self._curr_doc_id

        # parse title and save to cache
        if not self._doc_title_cache.has_key(self._curr_doc_id):
            title1 = unicode(BeautifulStoneSoup(title_text, convertEntities=BeautifulStoneSoup.ALL_ENTITIES))
            title2 = unicodedata.normalize('NFKD', title1)
            title3 = HTMLParser.HTMLParser().unescape(title2).replace("\u2013", "-")
            self._doc_title_cache[self._curr_doc_id] = str(title3)

    def _visit_a(self, elem):
        """Called when visiting <a> tags."""

        dest_url = self._fix_url(self._curr_url, attr(elem,"href"))

        #print "href="+repr(dest_url), \
        #      "title="+repr(attr(elem,"title")), \
        #      "alt="+repr(attr(elem,"alt")), \
        #      "text="+repr(self._text_of(elem))

        # add the just found URL to the url queue
        self._url_queue.append((dest_url, self._curr_depth))

        # add a link entry into the database from the current document to the
        # other document
        self.add_link(elem, self._curr_doc_id, self.document_id(dest_url))

        # TODO add title/alt/text to index for destination url

    def _add_words_to_document(self):
        # TODO: knowing self._curr_doc_id and the list of all words and their
        #       font sizes (in self._curr_words), add all the words into the
        #       database for this document
        # print "    num words="+ str(len(self._curr_words))
        self._doc_wordHits_cache[self._curr_doc_id] = self._curr_words

    def _add_first_p_to_document(self, soup):
        firstParagraph = soup.find('p')
        if firstParagraph is None:
            self._doc_snippet_cache[self._curr_doc_id] = 'Snippet not available'
        else:
            currSnippet = firstParagraph.text
            if currSnippet is None:
                self._doc_snippet_cache[self._curr_doc_id] = 'Snippet not available'
            else:
                if not self._doc_snippet_cache.has_key(self._curr_doc_id):
                    snippet1 = unicode(BeautifulStoneSoup(currSnippet, convertEntities=BeautifulStoneSoup.ALL_ENTITIES))
                    snippet2 = unicodedata.normalize('NFKD', snippet1)
                    snippet3 = HTMLParser.HTMLParser().unescape(snippet2).replace("\u2013", "-")
                    self._doc_snippet_cache[self._curr_doc_id] = str(snippet3)

    def _increase_font_factor(self, factor):
        """Increade/decrease the current font size."""
        def increase_it(elem):
            self._font_size += factor
        return increase_it

    def _visit_ignore(self, elem):
        """Ignore visiting this type of tag"""
        pass

    def _add_text(self, elem, doc_id):
        """Add some text to the document. This records word ids and word font sizes
        into the self._curr_words list for later processing."""
        words = WORD_SEPARATORS.split(elem.string.lower())
        for word in words:
            word = word.strip()
            wordLocation = self._curr_wordIndex
            if word in self._ignored_words:
                continue
            # record (wordId, relativeFontSize, wordLocation)
            self._curr_words.append((self.word_id(word), self._font_size, wordLocation))
            self._curr_wordIndex += 1

            #add doc_id to word if first acess to this word
            if doc_id not in self._inverted_index[self.word_id(word)]:
                self._inverted_index[self.word_id(word)].add(doc_id)

    def _text_of(self, elem):
        """Get the text inside some element without any tags."""
        if isinstance(elem, Tag):
            text = [ ]
            for sub_elem in elem:
                text.append(self._text_of(sub_elem))

            return " ".join(text)
        else:
            return elem.string

    def _index_document(self, soup, doc_id):
        """Traverse the document in depth-first order and call functions when entering
        and leaving tags. When we come accross some text, add it into the index. This
        handles ignoring tags that we have no business looking at."""
        class DummyTag(object):
            next = False
            name = ''

        class NextTag(object):
            def __init__(self, obj):
                self.next = obj

        tag = soup.html
        stack = [DummyTag(), soup.html]

        while tag and tag.next:
            tag = tag.next

            # html tags
            if isinstance(tag, Tag):

                if tag.parent != stack[-1]:
                    self._exit[stack[-1].name.lower()](stack[-1])
                    stack.pop()

                tag_name = tag.name.lower()

                # ignore this tag and everything in it
                if tag_name in self._ignored_tags:
                    if tag.nextSibling:
                        tag = NextTag(tag.nextSibling)
                    else:
                        self._exit[stack[-1].name.lower()](stack[-1])
                        stack.pop()
                        tag = NextTag(tag.parent.nextSibling)

                    continue

                # enter the tag
                self._enter[tag_name](tag)
                stack.append(tag)

            # text (text, cdata, comments, etc.)
            else:
                self._add_text(tag, doc_id)

    def crawl(self, depth=2, timeout=3):
        """Crawl the web!"""
        seen = set()

        while len(self._url_queue):

            url, depth_ = self._url_queue.pop()

            # skip this url; it's too deep
            if depth_ > depth:
                continue

            doc_id = self.document_id(url)

            # we've already seen this document
            if doc_id in seen:
                continue

            seen.add(doc_id) # mark this document as haven't been visited

            socket = None
            try:
                socket = urllib2.urlopen(url, timeout=timeout)
                soup = BeautifulSoup(socket.read())

                self._curr_depth = depth_ + 1
                self._curr_url = url
                self._curr_doc_id = doc_id
                self._font_size = 0
                self._curr_words = []
                # keep track of word location for current docId
                self._curr_wordIndex = 0
                self._index_document(soup, doc_id)
                self._add_words_to_document()
                self._add_first_p_to_document(soup)
                print "    url="+repr(self._curr_url)

            except Exception as e:
                print e
                pass
            finally:
                if socket:
                    socket.close()

        # After crawling, save all data to database

        # save lexicon data to presistent storage
        # lexicon: wordId (INTEGER PRIMARY KEY), word (TEXT)
        self.cur.execute(
            ''' CREATE TABLE IF NOT EXISTS lexicon
                (wordId INTEGER PRIMARY KEY, word TEXT);
            '''
        )
        lexiconData = [(int(wordId), word) for word, wordId in self._word_id_cache.items()]
        self.cur.executemany(
            ''' INSERT INTO lexicon VALUES (?,?)
            ''',
            lexiconData
        )
        self.db_conn.commit()

        # save documentId data to presistent storage
        # documentId: docId (INTEGER PRIMARY KEY), url (TEXT)
        self.cur.execute(
            ''' CREATE TABLE IF NOT EXISTS documentId
                (docId INTEGER PRIMARY KEY, url TEXT);
            '''
        )
        documentIdData = [(int(docId), str(url)) for url, docId in self._doc_id_cache.items()]
        self.cur.executemany(
            ''' INSERT INTO documentId VALUES (?,?)
            ''',
            documentIdData
        )
        self.db_conn.commit()

        # save invertedId data to presistent storage
        # invertedId: wordId (INTEGER), docId (INTEGER)
        self.cur.execute(
            ''' CREATE TABLE IF NOT EXISTS invertedId
                (wordId INTEGER, docId INTEGER);
            '''
        )
        invertedIdData = []
        for wordId in self._inverted_index.keys():
            for docId in self._inverted_index[wordId]:
                invertedIdData.append((int(wordId), int(docId)))
        self.cur.executemany(
            ''' INSERT INTO invertedId VALUES (?,?)
            ''',
            invertedIdData
        )
        self.db_conn.commit()

        # save pageRankScores data to presistent storage
        # pageRankScores: docId (INTEGER), score (REAL)
        pageRankScores = pagerank.page_rank(self._from_to_links)
        self.cur.execute(
            ''' CREATE TABLE IF NOT EXISTS pageRankScores
                (docId INTEGER, score REAL);
            '''
        )
        pageRankScoresData = [(int(docId), float(score)) for docId, score in pageRankScores.items()]
        unscoredLinks = [(int(docId), float(0.0)) for docId
                                                  in self._doc_id_cache.values()
                                                  if docId not in pageRankScores.keys()]
        self.cur.executemany(
            ''' INSERT INTO pageRankScores VALUES (?,?)
            ''',
            pageRankScoresData
        )
        self.cur.executemany(
            ''' INSERT INTO pageRankScores VALUES (?,?)
            ''',
            unscoredLinks
        )
        self.db_conn.commit()

        # save docTitle data to presistent storage
        # docTitle: docId (INTEGER), title (TEXT)
        self.cur.execute(
            ''' CREATE TABLE IF NOT EXISTS docTitle
                (docId INTEGER, title TEXT);
            '''
        )
        docTitles = [(int(docId), str(title)) for docId, title in self._doc_title_cache.items()]
        self.cur.executemany(
            ''' INSERT INTO docTitle VALUES (?,?)
            ''',
            docTitles
        )
        self.db_conn.commit()

        # save docWordHits data to presistent stroage
        # docWordHits: docId (INTEGER), wordId (INTEGER), fontSize (INTEGER), wordLocation (INTEGER)
        self.cur.execute(
            ''' CREATE TABLE IF NOT EXISTS docWordHits
                (docId INTEGER, wordId INTEGER, fontSize INTEGER, wordLocation INTEGER);
            '''
        )
        wordHits = []
        for docId in self._doc_wordHits_cache.keys():
            for hit in self._doc_wordHits_cache[docId]:
                wordHits.append((int(docId), int(hit[0]), int(hit[1]), int(hit[2])))
        self.cur.executemany(
            ''' INSERT INTO docWordHits VALUES (?,?,?,?)
            ''',
            wordHits
        )
        self.db_conn.commit()

        # save docAnchorHits data to presistent stroage
        # docAnchorHits: docId (INTEGER), wordId (INTEGER), anchorFontSize (INTEGER)
        self.cur.execute(
            ''' CREATE TABLE IF NOT EXISTS docAnchorHits
                (docId INTEGER, wordId INTEGER, anchorFontSize INTEGER);
            '''
        )
        anchorHits = []
        for docId in self._doc_anchorHits_cache.keys():
            for hit in self._doc_anchorHits_cache[docId]:
                anchorHits.append((int(docId), int(hit[0]), int(hit[1])))
        self.cur.executemany(
            ''' INSERT INTO docAnchorHits VALUES (?,?,?)
            ''',
            anchorHits
        )
        self.db_conn.commit()

        # save docSnippet data to presistent stroage
        # docSnippet: docId (INTEGER), snippet (TEXT)
        self.cur.execute(
            ''' CREATE TABLE IF NOT EXISTS docSnippet
                (docId INTEGER, snippet TEXT);
            '''
        )
        docSnippets = [(docId, snippet) for docId, snippet in self._doc_snippet_cache.items()]
        self.cur.executemany(
            ''' INSERT INTO docSnippet VALUES (?,?)
            ''',
            docSnippets
        )
        self.db_conn.commit()

    def get_inverted_index(self):
        return self._inverted_index

    def get_resolved_inverted_index(self):
        for x in self._inverted_index.keys():
            #resolve word of the current dict row
            k = [ i for i,j in self._word_id_cache.items() if j == x]
            #resolve url of the current dict row
            v = [ i for i,j in self._doc_id_cache.items() if j in self._inverted_index[x]]
            #insert resolved data to dict
            self._resolved_inverted_index[k[0]]= set(v)
        return self._resolved_inverted_index


if __name__ == "__main__":
    # get database path
    curPath = abspath(__file__)
    rootDir = abspath(dirname(dirname(curPath)))
    dbFile = r'%s/searcher/database.db' % rootDir

    # connect to database
    dbConnection = sqlite3.connect(dbFile)
    dbConnection.text_factory = str

    # start crawling
    bot = crawler(dbConnection, 'urlsList.txt')
    bot.crawl(depth=1)

    # close database
    dbConnection.close()
