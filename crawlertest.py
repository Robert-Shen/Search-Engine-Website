from crawler import crawler


def test_inverted_index():
    #initialzing all test scenario
    #1.test -- testing crawler @ http://www.eecg.toronto.edu/~jzhu/csc326/csc326.html
    #2.testempty -- testing crawler @ empty urls.txt
    #3.test -- testing crawler @ http://www.eecg.toronto.edu/~jzhu/csc326/csc326.html
    #                          @ http://www.eecg.toronto.edu/~jzhu/csc467/csc467.html
   
    print "-----------------------------------------------------------------"    
    #first testcase starts here
    print "Test Inverted Index"
    print "@http://www.eecg.toronto.edu/~jzhu/csc326/csc326.html:"
    print ""
    test = crawler(None, 'urls.txt')
    test.crawl()    
    inverted_index = test.get_inverted_index()
    resolved_inverted_index = test.get_resolved_inverted_index()
    testcase1 = {1: set([1]), 2: set([1]), 3: set([1])}
    testcase2 = {u'languages': set(['http://www.eecg.toronto.edu/~jzhu/csc326/csc326.html']), u'csc326': set(['http://www.eecg.toronto.edu/~jzhu/csc326/csc326.html']), u'programming': set(['http://www.eecg.toronto.edu/~jzhu/csc326/csc326.html'])}
    print ""
    if inverted_index == testcase1:
        print "invert index succeed"
    else:
        print "invert index failed"
    if resolved_inverted_index == testcase2:
        print "resolve index succeed"
    else:
        print "resolve index failed"
    #first testcase ends here
    
    print "-----------------------------------------------------------------"
    #second testcase starts here
    print "Test Inverted Index with empty urls.txt:"
    print ""
    test = crawler(None, 'empty.txt')
    test.crawl()
    inverted_index = test.get_inverted_index()
    resolved_inverted_index = test.get_resolved_inverted_index()
    testcase1 = { }
    testcase2 = { }
    if inverted_index == testcase1:
        print "invert index succeed, empty dictionary created"
    else:
        print "invert index failed, empty dictionary not created"
    if resolved_inverted_index == testcase2:
        print "resolve index succeed, empty dictionary created"
    else:
        print "resolve index failed, empty dictionary not created"    
    #second testcase ends here
    
    print "-----------------------------------------------------------------"
    #third testcase starts here
    print "Test Inverted Index"
    print "@http://www.eecg.toronto.edu/~jzhu/csc326/csc326.html"    
    print "@http://www.eecg.toronto.edu/~jzhu/csc467/csc467.html:"
    print ""
    test = crawler(None, 'urls1.txt')
    test.crawl()    
    inverted_index = test.get_inverted_index()
    resolved_inverted_index = test.get_resolved_inverted_index()
    testcase1 = {1: set([1]), 2: set([1]), 3: set([1]), 4: set([2]), 5: set([2]), 6: set([2])}
    print ""    
    if inverted_index == testcase1:
        print "invert index succeed"
    else:
        print "resolve index failed"
    print "this is the resolved index, unordered due to dictionary characteristic, check manually:"
    print resolved_inverted_index
    #third testcase ends here
    
    
if __name__ == "__main__":
    test_inverted_index()
    print ""
    print ""
    print ""
    print "Exit test!"