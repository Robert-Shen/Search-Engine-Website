# import files from other directory
from os.path import dirname, abspath
import sys
curPath = abspath(__file__)
rootDir = abspath(dirname(curPath))

aws = r'%s/aws' % rootDir
sys.path.insert(0, aws)
from deployment import SetupAWS

CURRENT_DIRECTORY = os.getcwd()

def deploy():
    # setup AWS
    print '> Start to create the AWS instance'
    ipAddress, instanceId, KEY_PAIR_FILE = SetupAWS()
    print '> AWS is setup'

    # setup app in AWS
    print "> Start to setup app in AWS"
    os.system("scp -r -o StrictHostKeyChecking=no -i %s %s ubuntu@%s:~/" % (KEY_PAIR_FILE, CURRENT_DIRECTORY, ipAddress))
    os.system("ssh -i %s ubuntu@%s" % (KEY_PAIR_FILE, ipAddress))
    #os.system("cd bottle-0.12.7")
    #os.system("python setup.py install --user")
    print "> Webpage Launched"

deploy()
