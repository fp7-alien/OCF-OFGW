from utils import cuisine

def remote(f):
    def new_f(cmd):
        print "Entering", f.__name__
        cmd=f(cmd)
        result = cuisine.run(cmd)
        print "Result:%s" %result
        print "Exited", f.__name__
    return new_f