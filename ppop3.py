import socket
import re
import pstorage
import time
import os,sys
import copy
import string
import selfdef

class ppop3():
    def send(self, buf):
        try:
            if self.__isssl == True:
                byteswritten = 0
                while byteswritten < len(buf):
                    byteswritten += self.__sslfd.write(buf[byteswritten:])
            else:
                byteswritten = 0
                while byteswritten < len(buf):
                    byteswritten += self.__sockfd.send(buf[byteswritten:])
        except:
            pass

    def __init__(self, sockfd, sslfd, ps, domainname, clientip, isssl = False):
        self.__sockfd = sockfd
        self.__sslfd = sslfd
        self.__status = 0
        self.__ps = ps
        self.__domianname = domainname
        self.__clientip = clientip
        self.__isssl =  isssl
        self.__maillist = []
        self.__mailcount = 0
        self.__mailsize = 0
        self.send('+OK pMail Sever POP3 server ready <%d.%d@%s>\r\n'%(os.getpid(),int(time.time()),self.__domianname))
        
    def parse(self, line_string):
        #sys.stdout.write(line_string)
        #sys.stdout.flush()
        cmd_string = re.split('\r|\n', line_string, 1)[0]
        cmd_unit = re.split(' |\t', cmd_string)
        cmd_main = cmd_unit[0].lower()
        if cmd_main == 'user':
            self.__username = cmd_unit[1]
            self.send('+OK core mail\r\n')
            
        elif cmd_main == 'pass':
            self.__password = cmd_unit[1]
            if self.__ps.checklogin(self.__username, self.__password) == True:
                self.__status |= selfdef.PHASE_AUTHED
               # tmpstr = self.__username + '@' + self.__domianname
                tmplist = [[],]
                self.__ps.listmail(self.__username, tmplist)
                self.__mailcount = 0
                self.__mailsize = 0
                for mitem in tmplist[0]:
                    #print mitem
                    self.__maillist.append([mitem[0],mitem[1],'N',mitem[2]])
                    self.__mailsize += mitem[0]
                    self.__mailcount +=1
                self.send('+OK %d message<s> [%d byte(s)]\r\n'%(self.__mailcount, self.__mailsize))
            else:
                self.send('-ERR unable to log on.\r\n')
                
        elif cmd_main == 'stat':
            if self.__status & selfdef.PHASE_AUTHED != selfdef.PHASE_AUTHED:
                self.send('-ERR command not valid in this state\r\n')
            else:
                self.send('+OK %d %d\r\n'%(self.__mailcount, self.__mailsize))
            
        elif cmd_main == 'list':
            if self.__status & selfdef.PHASE_AUTHED != selfdef.PHASE_AUTHED:
                self.send('-ERR command not valid in this state\r\n')
            else:
                if len(cmd_unit) <= 1:
                    self.send('+OK %d %d\r\n'%(self.__mailcount, self.__mailsize))
                    i = 1
                    for mitem in self.__maillist:
                        #print '%d %d\r\n'%(i,mitem[0])
                        self.send('%d %d\r\n'%(i,mitem[0]))
                        i += 1
                    self.send('.\r\n')
                else:
                    mid = string.atoi(cmd_unit[1])
                    if self.__mailcount < mid or mid <= 0:
                        self.send('-ERR no such message\r\n')
                    else:
                        self.send('+OK %d %d\r\n'%(mid, self.__maillist[mid-1][0]))
            
        elif cmd_main == 'retr':
            if self.__status & selfdef.PHASE_AUTHED != selfdef.PHASE_AUTHED:
                self.send('-ERR command not valid in this state\r\n')
            else:
                if len(cmd_unit) <= 1:
                    self.send('-ERR no such message\r\n')
                else:
                    mid = string.atoi(cmd_unit[1])
                    if self.__mailcount < mid or mid <= 0:
                        self.send('-ERR no such message\r\n')
                    else:
                        self.send('+OK %d octets\r\n'%self.__maillist[mid-1][0])
                        strbody = ['',]
                        self.__ps.getmailbody(self.__maillist[mid-1][3], strbody)
                        self.send(strbody[0])
                        self.send('\r\n.\r\n')
                    
        elif cmd_main == 'rest':
            if self.__status & selfdef.PHASE_AUTHED != selfdef.PHASE_AUTHED:
                self.send('-ERR command not valid in this state\r\n')
            else:
                #reset all delete mail status to undeleted
                for mitem in self.__maillist:
                    mitem[2] = 'N'
                self.send('+OK reset all.\r\n')
            
        elif cmd_main == 'uidl':
            if self.__status & selfdef.PHASE_AUTHED != selfdef.PHASE_AUTHED:
                self.send('-ERR command not valid in this state\r\n')
            else:
                if len(cmd_unit) <= 1:
                    self.send('+OK %d %d\r\n'%(self.__mailcount, self.__mailsize))
                    i = 1
                    for mitem in self.__maillist:
                        self.send('%d %s\r\n'%(i,mitem[1]))
                        i += 1
                    self.send('.\r\n')
                else:
                    mid = string.atoi(cmd_unit[1])
                    if self.__mailcount < mid or mid <= 0:
                        self.send('-ERR no such message\r\n')
                    else:
                        self.send('+OK %d %s\r\n'%(mid, self.__maillist[mid-1][1]))
                
        elif cmd_main == 'dele':
            if self.__status & selfdef.PHASE_AUTHED != selfdef.PHASE_AUTHED:
                self.send('-ERR command not valid in this state\r\n')
            else:
                if len(cmd_unit) <= 1:
                    self.send('-ERR no such message\r\n')
                else:
                    mid = string.atoi(cmd_unit[1])
                    if self.__mailcount < mid or mid <= 0:
                        self.send('-ERR no such message\r\n')
                    else:
                        if self.__maillist[mid-1][2] == 'Y':
                            self.send('-ERR message %d already deleted\r\n'%mid)
                        else:
                            self.__maillist[mid-1][2] = 'Y'
                            self.send('+OK message %d deleted\r\n'%mid)
                
        elif cmd_main == 'quit':
            for mitem in self.__maillist:
                if mitem[2] == 'Y':
                    self.__ps.delmail(mitem[3])
            self.send('+OK pMail Server POP3 server.\r\n')
            return False

        else:
            self.send('-ERR unrecognized command line\r\n')
