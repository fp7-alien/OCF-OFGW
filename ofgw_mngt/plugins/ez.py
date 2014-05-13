from utils import cuisine
from utils.remote import remote
   
class ez_hw:
    def __init__(self, ip):
        self.ip = ip
        print "EZ obj created"
        print "IP: " + self.ip
        cuisine.connect(ip, user="krisd")
        result = cuisine.run("uname -a")
        print "Result:%s" %result

    @remote
    def reboot(self):
        CMD = "Xreboot now"
        return CMD

    @remote
    def reset(self):
        CMD = "Xrm /tmp/old & cp /tmp/new /tmp/old"
        return CMD

    @remote
    def showPorts(self):
        CMD = "ifconfig"
        return CMD

    def __call__(self):
        print "RUNNING!!!!"