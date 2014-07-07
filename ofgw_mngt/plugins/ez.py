from utils import cuisine
from utils.remote import remote
   
class hwConfig:
    def __init__(self, ip, config):
        self.ip = ip
        self.config = config
        print config
        print "EZ obj created"
        print "IP: " + self.ip
        cuisine.connect(ip, user="root")
        result = cuisine.run("uname -a")
        print "Result:%s" %result

    @remote
    def reboot(self):
        CMD = "Xreboot now"
        

    @remote
    def reset(self):
        CMD = "Xrm /tmp/old & cp /tmp/new /tmp/old"
        return CMD

    @remote
    def showPorts(self):
        CMD = "ifconfig"
        return CMD

    def __call__(self):
        print "Calling plugin function"