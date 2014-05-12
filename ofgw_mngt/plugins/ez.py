from utils import cuisine

def remote(f):
    def new_f(cmd):
        print "Entering", f.__name__
        cmd=f(cmd)
        result = cuisine.run(cmd)
        print "Result:%s" %result
        print "Exited", f.__name__
    return new_f
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