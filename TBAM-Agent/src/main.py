
import os
import subprocess
from subprocess import call
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from SecureXMLRPCServerOriginal import SecureXMLRPCServerOriginal
from time import sleep
import urllib
import json


SERVER_KEY_PATH = "../certs/ch-key.pem"
SERVER_CERT_PATH = "../certs/ch-cert.pem"
TRUSTED_CERT_PATH = "../certs/trusted_roots/ch-cert.pem"

SERVER_ADDRESS = "127.0.0.1"
SERVER_PORT = 8234

ACCESS_CONF_FILE = '/etc/security/access.conf'

CONN_WITH_MGMT = True

class RPCServer(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)
    
class Links():
    dpidSrc = ""
    dpidDst = ""
    portSrc = 0
    portDst = 0
    def __init__(self, dpidSrc, portSrc, dpidDst, portDst):
        self.dpidSrc = dpidSrc
        self.portSrc = portSrc
        self.dpidDst = dpidDst
        self.portDst = portDst
        
def main():
    
    class xmlrpc_registers:
        def __init__(self):
            import string
            self.python_string = string
            
        def getSws(self):
            sws = []
            if(not CONN_WITH_MGMT):
                sws.append({"dipd" : "00:00:00:00:00:00:00:00"})
                sws.append({"dipd" : "00:00:00:00:00:00:00:01"})
                sws.append({"dipd" : "00:00:00:00:00:00:00:02"})
            else:
                req = urllib.urlopen('http://localhost:5000/neighbours')
                data = json.load(req)
                for each in data:
                    sws.append({"dipd" : data[each]['dpid'].replace("-", ":")})
            return sws
        
        def getLinks(self):
            linksString = []
            
            if(not CONN_WITH_MGMT):
                linksString.append(Links(dpidSrc="00:00:00:00:00:00:00:00", portSrc="5", dpidDst="00:00:00:00:00:00:00:01", portDst="1"))
                linksString.append(Links(dpidSrc="00:00:00:00:00:00:00:01", portSrc="10", dpidDst="00:00:00:00:00:00:00:02", portDst="4"))
            else:
                links = {}
                req = urllib.urlopen('http://localhost:5000/neighbours')
                data = json.load(req)
                for each in data:
                    for elementPort, destDpid in data[each]["ports"].iteritems():
                        elementDpid = (data[each]["dpid"]).replace("-", ":")
                        destDpid = destDpid.replace("-", ":")
                        if(not links.has_key(destDpid)):
                            if(not links.has_key(elementDpid)):
                                links[elementDpid] = {}
                                links[elementDpid] [destDpid] = {elementPort : None}
                            else:
                                if (not links[elementDpid].has_key(destDpid)):
                                    links[elementDpid] [destDpid] = {elementPort : None}
                                else:
                                    dict = links[elementDpid][destDpid] 
                                    for key in dict.iterkeys():
                                        links[elementDpid][destDpid] = {key : elementPort}
                            # dstDpid exists
                        else:
                            dict = links[destDpid] [elementDpid]
                            for key in dict.iterkeys():
                                links[destDpid] [elementDpid] = {key : elementPort}
            
                for dpid in links.iteritems():
                    for link in dpid[1].iteritems():
                        print link
                        for srcPort, dstPort in link[1].iteritems():
                            linksString.append(Links(dpidSrc=str(dpid[0]), portSrc=srcPort, dpidDst=str(link[0]), portDst=dstPort))
            return linksString
        
        def setTCPProxy(self, controller):
            # show iptables: iptables -t nat -L -n -v
            os.system("iptables -t nat -A POSTROUTING -j MASQUERADE")
            os.system("iptables -t nat -A PREROUTING -p tcp --dport 6633 -j DNAT --to-destination %s" % (controller))
            
            return True
        
        def remTCPProxy(self, controller):

            present = True;
            while(present):
                # p = subprocess.Popen("ls", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                p = subprocess.Popen('iptables -t nat --check PREROUTING -p tcp --dport 6633 -j DNAT --to-destination %s' % (controller), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, error = p.communicate()
                if(not error):
                    os.system("iptables -t nat -D PREROUTING -p tcp --dport 6633 -j DNAT --to-destination %s" % (controller))
                else:
                    present = False
            present = True
            while(present):
                p = subprocess.Popen('iptables -t nat --check POSTROUTING -j MASQUERADE', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, error = p.communicate()
                if(not error):
                    os.system("iptables -t nat -D POSTROUTING -j MASQUERADE")
                else:
                    present = False

            os.system("conntrack -D -p tcp --dport 6633 --dst-nat %s" % (controller.split(":")[0]))
            return True
        
        def setOvS(self, VLANs):
            # Drop rule    
            os.system('ovs-ofctl add-flow switch "priority=0, actions=drop"')
            # Dict VLANs OFELIA -> ALIEN
            # VLANs = {"10" : "0xffff", "30" : "20"}
            for key, value in VLANs.iteritems():
                # If vlan value is not defined, the VLAN mapping is not configured!
                if(key and value and key != "-1"):
                    # The in_port = 2 is connected to ALIEN island, the in_port = 3 is connected to OFELIA island
                    if(value == "0xffff"):
                        # From OFELIA to ALIEN
                        os.system('ovs-ofctl add-flow switch "in_port=3, dl_vlan=%s, actions= strip_vlan, output:2"' % (str(key)))
                    else:
                        os.system('ovs-ofctl add-flow switch "in_port=3, dl_vlan=%s, actions= mod_vlan_vid:%s, output:2"' % (str(key), (str(value))))
                    # From ALIEN to OFELIA
                    os.system('ovs-ofctl add-flow switch "in_port=2, dl_vlan=%s, actions= mod_vlan_vid:%s, output:3"' % (str(value), (str(key))))
            return True
        
        def remOvS(self, VLANs):
            # Dict VLANs: OFELIA -> ALIEN
            # VLANs = {"10" : "0xffff", "30" : "20"}
            
            for key, value in VLANs.iteritems():
                if(key and value and key != "-1"):
                    os.system("ovs-ofctl del-flows switch dl_vlan=%s" % (str(key)))
                    os.system("ovs-ofctl del-flows switch dl_vlan=%s" % (str(value)))
            # Drop rule always present   
            os.system('ovs-ofctl add-flow switch "priority=0, actions=drop"')     
            return True
        
        def setUserAuth(self, projectInfo):
            first_rule = '+ : ALL : LOCAL\n'
            second_rule = '+ : @proj_' + projectInfo + ' : ALL\n'
            last_rule = '- : ALL EXCEPT root login:ALL EXCEPT LOCAL\n'
            
            f = open(ACCESS_CONF_FILE, 'r')
            lines = f.readlines()
            f.close()
            
            for line in lines:
                if line == last_rule:
                    open(ACCESS_CONF_FILE, 'w').writelines(lines[:-3])
            
            f = open(ACCESS_CONF_FILE, 'a')
            f.write(first_rule)
            f.write(second_rule)
            f.write(last_rule)
            
            f.close()
            return True
        
        def remUserAuth(self, projectInfo):
            first_rule = '+ : ALL : LOCAL\n'
            second_rule = '\n'
            last_rule = '- : ALL EXCEPT root login:ALL EXCEPT LOCAL\n'
            
            f = open(ACCESS_CONF_FILE, 'r')
            lines = f.readlines()
            f.close()
            
            for line in lines:
                if line == last_rule:
                    open(ACCESS_CONF_FILE, 'w').writelines(lines[:-3])
            
            f = open(ACCESS_CONF_FILE, 'a')
            f.write(first_rule)
            f.write(second_rule)
            f.write(last_rule)
            
            f.close()
            return True
    
    
        
    server_address = (SERVER_ADDRESS, SERVER_PORT)
    server = SecureXMLRPCServerOriginal(server_address, logRequests=False, keyfile=SERVER_KEY_PATH,
                                        certfile=SERVER_CERT_PATH,
                                        ca_certs=TRUSTED_CERT_PATH)
    server.register_instance(xmlrpc_registers())

    print "Serving HTTPS on %s, port %d" % (SERVER_ADDRESS, SERVER_PORT)
    server.serve_forever()


if __name__ == '__main__':
    main()
    
