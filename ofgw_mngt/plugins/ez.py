from utils import cuisine
from utils.remote import remote
   
class hwConfig:
    def __init__(self, ip, config, id):
        self.ip = ip
        self.config = config
        self.id = id
        print "EZ obj created"
        print "IP: " + self.ip
        login = config.getDevicesParam(id=self.id, param='login')
        cuisine.connect(ip, user=login)
        # result = cuisine.run("uname -a")
        # print "Result:%s" %result

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