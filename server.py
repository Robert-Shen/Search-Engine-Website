import config

# import files from other directory
from os.path import dirname, abspath
import sys
curPath = abspath(__file__)
rootDir = abspath(dirname(curPath))

frontend = r'%s/frontend' % rootDir
sys.path.insert(0, frontend)
from frontend import startServer

############################################################################################
# When on local machine, set this to True;
# When upload to AWS server, set this to False
isLocalServer = True
############################################################################################

startServer(isLocalServer, config.ROOT)
