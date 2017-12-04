import config


# import files from other directory
from os.path import dirname, abspath
import sys
curPath = abspath(__file__)
rootDir = abspath(dirname(curPath))

aws = r'%s/aws' % rootDir
sys.path.insert(0, aws)
from termination import TerminateAWS

# TerminateAWS(config.AWS_Access_Key_Id,
#              config.AWS_Secret_Access_Key,
#              config.INSTANCE_ID,
#              config.PUBLIC_IP,
#              config.PUBLIC_DNS)

TerminateAWS(config.AWS_Access_Key_Id,
             config.AWS_Secret_Access_Key,
             'i-020237bc015370864',
             '52.203.200.74',
             'ec2-52-203-200-74.compute-1.amazonaws.com')
