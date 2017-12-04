import os
import time
import boto.ec2
import setupAWS

connection = setupAWS.EstablishConnectionToAWS()

# get all instances
reservations = connection.get_all_instances()
instances = []
for reservation in reservations:
    for instance in reservation.instances:
        instances.append(instance)

# display information of all instances
for i in range(len(instances)):
    print("index: %s instanceId: %s state: %s ipAddress: %s" % (i, instances[i].id, instances[i].state, instances[i].ip_address))

# let user decide which instance to terminate
while True:
    userInput = input("Type in 'index#' to terminate instance. Type in any other string to exit: ")
    if userInput in range(len(instances)):
        terminateIndex = userInput
        terminateIndex(connection, instances[userInput])
    else:
        print('exit...')
        break

def terminateInstance(connection, instance):
    if instance.state != 'terminated':
        connection.terminate_instances([instance.id])

        print('Wait for instance to terminate'),
        while instance.state != 'terminated':
            time.sleep(1)
            print('.'),
            instance.update()
        print('instance %s is terminated successfully' % instance.id)

    else:
        print('instance %s has already been terminated' % instance.id)