from utils import cuisine
# from utils.remote import remote

def remote(f):
    def new_f(cmd):
        print "Entering", f.__name__
        cmd=f(cmd)
        result = cuisine.run(cmd)
        print "Result:%s" %result
        print "Exited", f.__name__
    return new_f

class hwConfig():
    def __init__(self, ip, config, id):
        self.ip = ip
        self.config = config
        self.id = id
        print "EZ obj created"
        print "IP: " + self.ip
        login = config.getDevicesParam(id=self.id, param='login')
        cuisine.connect(self.ip, user=login)
        # cuisine.mode_remote()
        # result = cuisine.run("uname -a")
        result = cuisine.run("ifconfig")
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
        CMD="ifconfig"
        return CMD


    # def __call__(self):
    #     print "Calling plugin function"


