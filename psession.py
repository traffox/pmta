import socket, select
import threading
import re
import time
import pstorage
import psmtp
import ppop3

class psession(threading.Thread):
    def __init__(self, ps, domain_name, arg, session_type, isssl = False):
        threading.Thread.__init__(self)
        self.__sockfd = arg[0]
        self.__sslfd = arg[1]
        self.__clientip = arg[2]
        self.__session_type = session_type
        self.__domainname = domain_name
        self.__ps = ps
        self.__isssl = isssl
        
    def recvline(self, strline):
        detect_fds = [self.__sockfd,]
        rrdy, wrdy, erdy = select.select(detect_fds, [], [], 20)
        if len(rrdy) == 0:
            #print 'DEBUG: RECV TIMEOUT'
            return False
        else:
            while True:
                try:
                    if self.__isssl == True:
                        strtmp = self.__sockfd.read(1)
                    else:
                        strtmp = self.__sockfd.recv(1)
                        
                    strline[0] += strtmp[0]
                    if(strtmp[0] == '\n'):
                        break
                except:
                    return False
            return True

    def run(self):
        cmdstr = ['',]
        if(self.__session_type == 0): #smtp session
            try:
                hsmtp = psmtp.psmtp(self.__sockfd, self.__sslfd, self.__ps, self.__domainname, self.__clientip)
                while True:
                    cmdstr[0] = ''
                    if(self.recvline(cmdstr) == False):
                        break
                    
                    if(hsmtp.parse(cmdstr[0]) == False):
                        break
                    else:
                        continue
            except Exception, e:
                print 'DEBUG: Create SMTP object:',e
        else:
            try:
                
                hpop3 = ppop3.ppop3(self.__sockfd, self.__sslfd, self.__ps, self.__domainname, self.__clientip)
                while True:
                    cmdstr[0] = ''
                    if(self.recvline(cmdstr) == False):
                        break
                    if(hpop3.parse(cmdstr[0]) == False):
                        break
                    else:
                        continue
            except Exception, e:
                print 'DEBUG: Create POP3 object:',e
        try:
            if self.__isssl == True:
                del self.__sockfd

            self.__sockfd.close()
        except:
            pass
        
if __name__ == '__main__':
    print "psession class\n"



