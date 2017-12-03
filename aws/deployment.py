import os
import setupAWS

CURRENT_DIRECTORY = os.getcwd()

def deploy():
    # setup AWS
    print 'Start to create the AWS instance'
    ipAddress, instanceId, KEY_PAIR_FILE = setupAWS.Setup()
    print 'AWS is setup'

    # setup app in AWS
    print "Start to setup app in AWS"
    os.system("scp -r -o StrictHostKeyChecking=no -i %s %s ubuntu@%s:~/" % (KEY_PAIR_FILE, CURRENT_DIRECTORY, ipAddress))
    os.system("ssh -i %s ubuntu@%s" % (KEY_PAIR_FILE, ipAddress))
    #os.system("cd bottle-0.12.7")
    #os.system("python setup.py install --user")
    print "App Launched"





deploy()