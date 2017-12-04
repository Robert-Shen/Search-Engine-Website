import time
import boto.ec2
import boto.ec2.connection
import boto.ec2.instance
import sys

SECURITY_GROUP_NAME = 'csc326-group52'
SECURITY_GROUP_DESCRIPTION = 'My csc326 web search engine'

# Establish connection to region
def EstablishConnectionToAWS(aws_id, aws_key):
    return boto.ec2.connect_to_region('us-east-1',
                                      aws_access_key_id = aws_id,
                                      aws_secret_access_key = aws_key)

# Setup a new instance of ec2
# Return public_DNS_address, instance_id, login.pem_filename
def SetupAWS(aws_access_key_id,
             aws_secret_access_key,
             rootDir,
             key_pair_name):
    # initialize global params
    AWS_ACCESS_KEY_ID = aws_access_key_id
    AWS_SECRET_ACCESS_KEY = aws_secret_access_key
    KEY_PAIR_FILE_NAME = key_pair_name
    KEY_PAIR_DIRECTORY = rootDir # save login.pem to root directory

    # connect to aws
    myPrint('Connecting to AWS')
    connection = EstablishConnectionToAWS(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    myPrint('Connected to AWS')

    # check if a keyPair already exists
    myPrint('Check if login.pem exists')
    keyPair = connection.get_key_pair(KEY_PAIR_FILE_NAME)
    if keyPair is None:
        myPrint('No login.pem found, creating new one')
        # Create Key-Pair. The .pem key file is needed for SSH the new instances.
        keyPair = connection.create_key_pair(KEY_PAIR_FILE_NAME)
        keyPair.save(KEY_PAIR_DIRECTORY)
    else:
        myPrint('Existing login.pem found, no need to create new one')

    # check if the securityGroup already exists

    # if len(securityGroup) == 0:
    # Create a security group
    try:
        myPrint('Check if the securityGroup already exists')
        securityGroup = connection.get_all_security_groups(groupnames=[SECURITY_GROUP_NAME])[0]
        myPrint('SecurityGroup already exists')
    except connection.ResponseError, e:
        if e.code == 'InvalidGroup.NotFound':
            myPrint('SecurityGroup not exists, creating a new one')
            securityGroup = connection.create_security_group(name=SECURITY_GROUP_NAME,description=SECURITY_GROUP_DESCRIPTION)
            # Authorize following protocols and ports for the security group
            securityGroup.authorize(ip_protocol='icmp', from_port=-1, to_port=-1, cidr_ip='0.0.0.0/0')
            securityGroup.authorize(ip_protocol='tcp', from_port=22, to_port=22, cidr_ip='0.0.0.0/0')
            securityGroup.authorize(ip_protocol='tcp', from_port=80, to_port=80, cidr_ip='0.0.0.0/0')
            securityGroup.authorize(ip_protocol='tcp', from_port=8080, to_port=8080, cidr_ip='0.0.0.0/0') # for testing purpose

    # Start a new instance
    myPrint('Start a new instance')
    reservationObj = connection.run_instances('ami-8caa1ce4',
                                              key_name=KEY_PAIR_FILE_NAME,
                                              security_groups=[SECURITY_GROUP_NAME],
                                              instance_type='t1.micro')
    # States of the instance
    instance = reservationObj.instances[0]

    # Once the state of the instance is changed to "running"
    myPrint('Wait for instance to initialize'),
    while CheckInstanceStatus(connection, instance.id) != 'ok':
        time.sleep(1)
        print('.'),
        sys.stdout.flush()
    myPrint('')
    myPrint('Instance is initialized successfully')

    # name the instance
    connection.create_tags([instance.id], {"Name": 'Deployment'})

    # The public IP address of the instance
    #publicIpAddress = instance.ip_address

    # Setup static IP address
    address = connection.allocate_address()
    address.associate(instance_id = instance.id)
    ipAddress = address.public_ip

    # Get public DNS of current instance
    curInstances = connection.get_only_instances(instance_ids=[instance.id])
    curInstance = curInstances[0]
    publicDNS = curInstance.public_dns_name

    myPrint('====================================================')
    myPrint('Instance id: %s' % instance.id)
    myPrint('Public DNS address: %s' % publicDNS)
    myPrint('Public ip: %s' % ipAddress)
    myPrint('====================================================')

    return (instance.id, publicDNS, ipAddress, KEY_PAIR_FILE_NAME+'.pem')

def CheckInstanceStatus(connection, instanceId):
    instances = connection.get_all_instance_status(instance_ids=instanceId)
    if not instances:
        return "none"
    else:
        return instances[0].system_status.status

def myPrint(text):
    print '> %s' % text
    sys.stdout.flush()
