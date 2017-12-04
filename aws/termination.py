import os
import time
import boto.ec2
import deployment
import sys

def TerminateAWS(aws_id, aws_key, instanceId, ip, dns):
    connection = deployment.EstablishConnectionToAWS(aws_id, aws_key)

    myPrint("Carefule! You are about to terminate the following instance:")
    myPrint('Instance ID: %s' % instanceId)
    myPrint('Public DNS: %s' % dns)
    myPrint('Public IP: %s' % ip)
    userComfirm = raw_input("> Is this the instance you want to terminate (y/n)? ")
    if userComfirm == 'y':
        connection.terminate_instances(instance_ids=[instanceId])

        if (deployment.CheckInstanceStatus(connection, [instanceId]) == 'none'):
            myPrint("Succues: Instance %s is terminated." % instanceId)
        else:
            myPrint("Fail: Instance %s cannot be terminated due to some errors." % instanceId)
    else:
        userInput = raw_input(
            "> Enter the instance_id of the AWS istance you wish to terminate: ")
        try:
            connection.terminate_instances(instance_ids=[userInput])

            if (deployment.CheckInstanceStatus(connection, [userInput]) == 'none'):
                myPrint("Succues: Instance %s is terminated" % instanceId)
            else:
                myPrint("Fail: Instance %s cannot be terminated due to some errors" % userInput)
        except:
            myPrint('Unexpected error, termination process aborted')

def myPrint(text):
    print '> %s' % text
    sys.stdout.flush()
