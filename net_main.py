from net_system.models import NetworkDevice, Credentials, SnmpCredentials
from remote_connection.ssh_connection import SSHConnection, AristaSSHConnection
import django
import time

def gather_inventory():
    '''
    Dispatcher for calling SSH, onePK, or eAPI based onthe
    NetworkDevice.device_class
    '''

    DEBUG = True

    net_devices = NetworkDevice.objects.all()

    for a_device in net_devices:

        if 'ssh' in a_device.device_class:
            if 'cisco' in a_device.device_class:
                if DEBUG: print "Cisco SSH inventory call: {} {}".format(a_device.device_name, a_device.device_class)
                ssh_connect = SSHConnection(a_device)
                a_device.vendor = "cisco"
            elif 'arista' in a_device.device_class:
                if DEBUG: print "Arista SSH inventory call: {} {}".format(a_device.device_name, a_device.device_class)
                ssh_connect = AristaSSHConnection(a_device)
                a_device.vendor = "arista"
            ssh_connect.establish_connection()
            ssh_connect.gather_info()
            a_device.model = ssh_connect.model
            a_device.os_version = ssh_connect.os_version
            a_device.serial_number = ssh_connect.serial
            a_device.uptime_seconds = ssh_connect.uptime_in_seconds
            a_device.save()
#            a_device.uptime_seconds = ssh_connect.uptime_in_seconds
#            print "Model: " + ssh_connect.model
#            print "Version: " + ssh_connect.os_version
#            print "Serial: " + ssh_connect.serial
#            print "Uptime: " + str(ssh_connect.uptime_in_seconds)
        elif 'onepk' in a_device.device_class:
            if DEBUG: print "onePK inventory call: {} {}".format(a_device.device_name, a_device.device_class)
            pass
        elif 'eapi' in a_device.device_class:
            if DEBUG: print "eAPI inventory call: {} {}".format(a_device.device_name, a_device.device_class)
            pass
        else:
            # invalid condition / exception
            pass

if __name__ == '__main__':

    django.setup()

    LOOP_DELAY = 300
    VERBOSE = True

    time.sleep(5)
    print

    while True:
        if VERBOSE: print "Gather inventory from devices"
        gather_inventory()

        if VERBOSE: print "Sleeping for {} seconds".format(LOOP_DELAY)
        time.sleep(LOOP_DELAY)

