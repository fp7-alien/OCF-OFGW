
import os
import subprocess
from subprocess import call
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from SecureXMLRPCServerOriginal import SecureXMLRPCServerOriginal
from time import sleep


SERVER_KEY_PATH = "/root/AlienAM/.gcf/ch-key.pem"
SERVER_CERT_PATH =  "/root/AlienAM/.gcf/ch-cert.pem"
TRUSTED_CERT_PATH = "/root/AlienAM/.gcf/trusted_roots/ch-cert.pem"

SERVER_ADDRESS = "127.0.0.1"
SERVER_PORT = 8234

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
    
        #cmd = ['/root/%s.sh' %(split[2]), '%/s' %(delay)]   
        #Avviare un bash file:
        #cmd = ['/root/AlienAM/prova.sh']
        #subprocess.Popen(cmd, shell=True)
        #oppure
        #os.system('/root/AlienAM/prova.sh')
        #oppure per lanciare un comando...
        #os.system("ls")
    
    class xmlrpc_registers:
        def __init__(self):
            import string
            self.python_string = string
            
        def getSws(self):
            #TODO: this call needs to retrieve information through the MGNT (not yet implemented) 
            sws = []
            sws.append({"dipd" : "00:00:00:00:00:00:00"})
            sws.append({"dipd" : "00:00:00:00:00:00:01"})
            return sws
        
        def getLinks(self):
            #TODO: this call needs to retrieve information through the MGN (not yet implemented)
            array = []
            array.append(Links(dpidSrc = "00:00:00:00:00:00:00", portSrc="5", dpidDst="00:00:00:00:00:00:01", portDst="1"))
            array.append(Links(dpidSrc = "00:00:00:00:00:00:01", portSrc="10", dpidDst="00:00:00:00:00:00:02", portDst="4"))
            #array = ["00:00:00:00:00:00:00-5/00:00:00:00:00:00:01-10", "00:00:00:00:00:00:10-1/AB:10:00:00:00:00:00-5"];
            return array
        
        def setTCPProxy(self, controller):
            # show iptables: iptables -t nat -L -n -v
            os.system("iptables -t nat -A POSTROUTING -j MASQUERADE")
            os.system("iptables -t nat -A PREROUTING -p tcp --dport 6633 -j DNAT --to-destination %s" %(controller))
            
            return True
        
        def remTCPProxy(self, controller):
            
            present = True;
            while(present):
                #p = subprocess.Popen("ls", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                p = subprocess.Popen('iptables -t nat --check PREROUTING -p tcp --dport 6633 -j DNAT --to-destination %s' %(controller), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, error = p.communicate()
                if(not error):
                    os.system("iptables -t nat -D PREROUTING -p tcp --dport 6633 -j DNAT --to-destination %s" %(controller))
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
            
            os.system("conntrack -D -p tcp --dport 6633 --dst-nat %s" %(controller))
            return True
        
        def setOvS(self, VLANs):
            #Drop rule    
            os.system('ovs-ofctl add-flow switch "priority=0, actions=drop"')
            #Dict VLANs OFELIA -> ALIEN
            #VLANs = {"10" : "0xffff", "30" : "20"}
            for key,value in VLANs.iteritems():
                #If vlan value is not defined, the VLAN mapping is not configured!
                if(key or value):
                    if(value == "0xffff"):
                        #From OFELIA to ALIEN
                        os.system('ovs-ofctl add-flow switch "in_port=3, dl_vlan=%s, actions= strip_vlan, output:2"' %(str(key)))
                    else:
                        os.system('ovs-ofctl add-flow switch "in_port=3, dl_vlan=%s, actions= mod_vlan_vid:%s, output:2"' %(str(key), (str(value))))
                    #From ALIEN to OFELIA
                    os.system('ovs-ofctl add-flow switch "in_port=2, dl_vlan=%s, actions= mod_vlan_vid:%s, output:3"' %(str(value), (str(key))))
            return True
        
        def remOvS(self, VLANs):
            #Dict VLANs: OFELIA -> ALIEN
            #VLANs = {"10" : "0xffff", "30" : "20"}
            
            for key,value in VLANs.iteritems():
                if(key or value):
                    os.system("ovs-ofctl del-flows switch dl_vlan=%s"%(str(key)))
                    os.system("ovs-ofctl del-flows switch dl_vlan=%s"%(str(value)))
            #Drop rule always present   
            os.system('ovs-ofctl add-flow switch "priority=0, actions=drop"')     
            return True
        
        def setUserAuth(self, ssh_pub_client_cert):
            #TODO: Actually we do not know the format of the certificate or certificates.

            
            return True
        
        def remUserAuth(self, ssh_pub_client_cert):
            #TODO: Actually we do not know the format of the certificate or certificates.

            return True
    
    
        
    server_address = (SERVER_ADDRESS, SERVER_PORT)
    #TODO: We can keep this call (but the certs must be generated) or the TBAM Agent could be integrated in the AMsoil
    server = SecureXMLRPCServerOriginal(server_address, logRequests=False, keyfile=SERVER_KEY_PATH, 
                                        certfile=SERVER_CERT_PATH,
                                        ca_certs=TRUSTED_CERT_PATH)
    server.register_instance(xmlrpc_registers())

    print "Serving HTTPS on %s, port %d" % (SERVER_ADDRESS, SERVER_PORT)
    server.serve_forever()


if __name__ == '__main__':
    main()
    