import paramiko
import time
import re

BUFFER = 25000

class SSHConnection(object):
    '''
    Base class is based upon Cisco IOS behavior.

    Should subclass this class for different vendors.
    '''

    def __init__(self, net_device):
        self.net_device = net_device
        self.ip = net_device.ip_address

        if net_device.ssh_port:
            self.port = net_device.ssh_port
        else:
            self.port = 22

        self.username = net_device.credentials.username
        self.password = net_device.credentials.password

        self.prompt = ""
        self.enable_char = "#"

        self.model = ""
        self.os_version = ""
        self.serial = ""
        self.uptime_in_seconds = ""

    def establish_connection(self):
        print
        print "#" * 80

        # Create instance of SSHClient object
        self.remote_conn_pre = paramiko.SSHClient()

        # Automatically add untrusted hosts
        self.remote_conn_pre.set_missing_host_key_policy(
            paramiko.AutoAddPolicy())

        # initiate SSH connection
        print "SSH connection establisehd to {}:{}".format(self.ip, self.port)
        self.remote_conn_pre.connect(hostname=self.ip, port=self.port,
            username=self.username, password=self.password, look_for_keys=False,
            allow_agent=False)

        # Use invoke_shell to establish an 'interactive session'
        self.remote_conn = self.remote_conn_pre.invoke_shell()
        print "Interactive SSH session established"

        # Strip the initial router prompt
        time.sleep(3)
        output = self.remote_conn.recv(BUFFER)

        # See output
        print output

        print "#" * 80
        print

        self.prompt = self.find_prompt()

        if "#" not in self.prompt:
            self.enable()
            self.prompt = self.find_prompt()

        self.nopager()

        #print self.send_command("show interface")

    def find_prompt(self):

        self.remote_conn.send("\n")
        time.sleep(1)

        return self.remote_conn.recv(BUFFER).strip()

    def enable(self):

        self.remote_conn.send("enable\n")
        time.sleep(1)
        self.prompt = self.find_prompt()

        if self.enable_char not in self.prompt:
            print "Unable to enter enable mode."
            exit()

    def fix_crlf(self, text):

        if "\r" in text:
            text = text.replace('\r\n', '\n')
            return text.replace('\r', '\n')
        else:
            return text

    def nopager(self):

        self.remote_conn.send("term len 0\n")
        time.sleep(1)
        self.remote_conn.recv(BUFFER)

    def send_command(self, command):

        loop_count = 0
        loops_to_run = 3
        self.remote_conn.send(command + "\n")
        time.sleep(1)
        output = self.remote_conn.recv(BUFFER)
        if self.prompt not in output and loop_count < loops_to_run:
            #print "waiting for more"
            time.sleep(1)
            output += self.remote_conn.recv(BUFFER)
            loop_count += 1
        output = output.replace(command, "", 1)
        output = output.replace(self.prompt, "")
        output = output.strip()
        return self.fix_crlf(output)


    def gather_info(self):

        output = self.send_command("show version")

        self.model = self.get_model(output)
        self.os_version = self.get_os_version(output)
        self.serial = self.get_serial(output)
        self.uptime_in_seconds = self.get_uptime_in_seconds(output)

    def get_model(self, showver):

        result = ""
        try:
            result = re.findall(".*processor.*memory", showver)[0]
            result = result.split(" ")[1]
        except:
            pass
        return result

    def get_os_version(self, showver):

        result = ""
        try:
            result = re.findall("Cisco IOS Software.*", showver)[0]
            result = re.findall("Version (.*),", result)[0]
        except:
            pass
        return result

    def get_serial(self, showver):

        result = ""
        try:
            result = re.findall("Processor board ID (.*)", showver)[0]
        except:
            pass
        return result

    def get_uptime_in_seconds(self, showver):

        result = weeks = days = hours = mins = 0
        try:
            text = re.findall("uptime is (.*)", showver)[0]
            if "week" in text:
                weeks = re.findall("([0-9]{1,2}) week", text)[0]
            if "day" in text:
                days = re.findall("([0-9]{1,2}) day", text)[0]
            if "hour" in text:
                hours = re.findall("([0-9]{1,2}) hour", text)[0]
            if "minute" in text:
                mins = re.findall("([0-9]{1,2}) minute", text)[0]
            result = (int(mins) * 60) + (int(hours) * 3600) + (int(days) * 3600 * 24) + (int(weeks) * 3600 * 24 * 7)
        except:
            pass
        return result

class AristaSSHConnection(SSHConnection):

    def get_model(self, showver):

        result = ""
        try:
            result = re.findall("Arista (.*)", showver)[0]
        except:
            pass
        return result

    def get_os_version(self, showver):

        result = ""
        try:
            result = re.findall("Software image version: (.*)", showver)[0]
        except:
            pass
        return result

    def get_serial(self, showver):

        result = ""
        try:
            result = re.findall("Serial number: (.*)", showver)[0]
            result = result.strip()
        except:
            pass
        return result

    def get_uptime_in_seconds(self, showver):

        result = weeks = days = hours = mins = 0
        try:
            text = re.findall("Uptime: (.*)", showver)[0]
            if "week" in text:
                weeks = re.findall("([0-9]{1,2}) week", text)[0]
            if "day" in text:
                days = re.findall("([0-9]{1,2}) day", text)[0]
            if "hour" in text:
                hours = re.findall("([0-9]{1,2}) hour", text)[0]
            if "minute" in text:
                mins = re.findall("([0-9]{1,2}) minute", text)[0]
            result = (int(mins) * 60) + (int(hours) * 3600) + (int(days) * 3600 * 24) + (int(weeks) * 3600 * 24 * 7)
        except:
            pass
        return result
