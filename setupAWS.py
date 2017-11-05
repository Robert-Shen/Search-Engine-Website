import os
import time
import boto.ec2
import boto.ec2.connection
import boto.ec2.instance
import credential

AWS_SCCESS_KEY_ID = credential.Access_Key_Id
AWS_SECRET_ACCESS_KEY = credential.Secret_Access_Key

KEY_PAIR_FILE_NAME = 'KeyPair'
KEY_PAIR_DIRECTORY = os.getcwd() # save to current working directory

SECURITY_GROUP_NAME = 'csc326-group52'
SECURITY_GROUP_DESCRIPTION = 'My csc326 web app'

# Establish connection to region
def EstablishConnectionToAWS():
    return boto.ec2.connect_to_region('us-east-1', aws_access_key_id=AWS_SCCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

def Setup():
    connection = EstablishConnectionToAWS()

    # check if a keyPair already exists
    keyPair = connection.get_key_pair(KEY_PAIR_FILE_NAME)
    if keyPair is None:
        # Create Key-Pair. The .pem key file is needed for SSH the new instances.
        keyPair = connection.create_key_pair(KEY_PAIR_FILE_NAME)
        keyPair.save(KEY_PAIR_DIRECTORY)

    # check if the securityGroup already exists
    #
    #if len(securityGroup) == 0:
    # Create a security group
    try:
        securityGroup = connection.get_all_security_groups(groupnames=[SECURITY_GROUP_NAME])[0]
    except connection.ResponseError, e:
        if e.code == 'InvalidGroup.NotFound':
            securityGroup = connection.create_security_group(name=SECURITY_GROUP_NAME,description=SECURITY_GROUP_DESCRIPTION)
            # Authorize following protocols and ports for the security group
            securityGroup.authorize(ip_protocol='icmp', from_port=-1, to_port=-1, cidr_ip='0.0.0.0/0')
            securityGroup.authorize(ip_protocol='tcp', from_port=22, to_port=22, cidr_ip='0.0.0.0/0')
            securityGroup.authorize(ip_protocol='tcp', from_port=80, to_port=80, cidr_ip='0.0.0.0/0')
            securityGroup.authorize(ip_protocol='tcp', from_port=8080, to_port=8080, cidr_ip='0.0.0.0/0') # for testing purpose

    # Start a new instance
    reservationObj = connection.run_instances('ami-8caa1ce4', key_name=KEY_PAIR_FILE_NAME, security_groups=[SECURITY_GROUP_NAME], instance_type='t1.micro')
    # States of the instance
    instance = reservationObj.instances[0]

    # Once the state of the instance is changed to "running"
    print('Wait for instance to initialize'),
    while CheckInstanceStatus(connection, instance.id) != 'ok':
        time.sleep(1)
        print('.'),
    print('instance is initialized successfully')

    # The public IP address of the instance 
    #publicIpAddress = instance.ip_address

    # Setup static IP address
    address = connection.allocate_address()
    address.associate(instance_id = instance.id)
    ipAddress = address.public_ip   

    print('------------------------------')
    print('ip address: ' + ipAddress)
    print('instance id: ' + instance.id)
    print('------------------------------')

    return (ipAddress, instance.id, KEY_PAIR_FILE_NAME+'.pem')

def CheckInstanceStatus(connection, instanceId):
    instances = connection.get_all_instance_status(instance_ids=instanceId)
    if not instances:
        return "none"
    else:
        return instances[0].system_status.status

# launch setup program
Setup()