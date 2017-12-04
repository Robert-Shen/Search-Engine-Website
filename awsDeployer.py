import config
import paramiko
import os
import config
import sys

# import files from other directory
from os.path import dirname, abspath
import sys
curPath = abspath(__file__)
rootDir = abspath(dirname(curPath))

aws = r'%s/aws' % rootDir
sys.path.insert(0, aws)
from deployment import SetupAWS

def myPrint(text):
    print '> %s' % text
    sys.stdout.flush()

# setup AWS
myPrint('Start to create the AWS instance')
instanceId, publicDNS, piblicIP, KEY_PAIR_FILE = SetupAWS(config.AWS_Access_Key_Id,
                                                          config.AWS_Secret_Access_Key,
                                                          rootDir,
                                                          config.KEY_PAIR_FILE_NAME)
myPrint('AWS is setup')

# setup app in AWS
myPrint("Start to setup app in AWS")

# copy all files to remote server
os.system("scp -r -o StrictHostKeyChecking=no -i %s ./ ubuntu@%s:~/app" % (KEY_PAIR_FILE, str(piblicIP)) )

k = paramiko.RSAKey.from_private_key_file(KEY_PAIR_FILE) # must be in your current dir
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())

c.connect( hostname = piblicIP, username = 'ubuntu', pkey = k )

myPrint('Start to download and install necessary packages')
commands = [ "wget https://pypi.python.org/packages/source/b/bottle/bottle-0.12.7.tar.gz",
             "tar -zxvf bottle-0.12.7.tar.gz",
             "cd bottle-0.12.7; sudo python setup.py install --user",
             "sudo apt-get -y update",
             "sudo apt-get -y install python-beaker",
             "sudo apt-get -y install python-requests",
             "sudo apt-get -y install npm",
             "sudo npm install datamuse",
             "sudo npm install nohup",
             # below are for google api
             "sudo apt-get -y install python-pip python-dev build-essential",
             "sudo pip install --upgrade pip",
             "sudo pip install --upgrade virtualenv",
             "sudo pip install --upgrade oauth2client",
             "sudo pip install --upgrade google-api-python-client",
             "cd app; sudo nohup python server.py &"
             ]# these commands will exec in series

for command in commands:
    print "Executing {}".format( command )
    stdin , stdout, stderr = c.exec_command(command) # this command is executed on the *remote* server
    print stdout.read()
    print( "Errors")
    print stderr.read()

myPrint('All necessary packages are installed successfully')

c.close()

myPrint("Webpage is Launched")

# write all useful info to config.py
qAWS_Access_Key_Id = config.AWS_Access_Key_Id
qAWS_Secret_Access_Key = config.AWS_Secret_Access_Key
qINSTANCE_ID = instanceId
qPUBLIC_DNS = publicDNS
qPUBLIC_IP = piblicIP
qKEY_PAIR_FILE_NAME = config.KEY_PAIR_FILE_NAME

with open('config.py', 'w') as f:
    f.write('AWS_Access_Key_Id = "%s"\n' % qAWS_Access_Key_Id)
    f.write('AWS_Secret_Access_Key = "%s"\n' % qAWS_Secret_Access_Key)
    f.write('\n')
    f.write('INSTANCE_ID = "%s"\n' % qINSTANCE_ID)
    f.write('PUBLIC_DNS = "%s"\n' % qPUBLIC_DNS)
    f.write('PUBLIC_IP = "%s"\n' % qPUBLIC_IP)
    f.write('\n')
    f.write('KEY_PAIR_FILE_NAME = "%s"\n' % qKEY_PAIR_FILE_NAME)

# print summary
myPrint('Info about Instance_ID, Public_DNS, Public_IP are write to config.py')
myPrint('=================================')
myPrint('Instance_ID: %s' % qINSTANCE_ID)
myPrint('Public_DNS: %s' % qPUBLIC_DNS)
myPrint('Public_IP: %s' % qPUBLIC_IP)
myPrint('=================================')

myPrint('AWS instance deployment finished')
myPrint("Webpage is Launched")
myPrint("Deployment and launching are finished")
