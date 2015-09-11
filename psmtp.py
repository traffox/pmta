import socket
import base64
import re
import pstorage
import time
import sys
import random
import selfdef
import ptx

class psmtp():
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
        
    def __init__(self, sockfd, sslfd, ps, domianname, clientip, isssl = False):
        self.__sockfd = sockfd
        self.__sslfd = sslfd
        self.__ps = ps
        self.__status = 0
        self.__helloname = ''
        self.__mailbody = ''
        self.__mailtop = ''
        self.__username = ''
        self.__password = ''
        self.__mailfrom = ''
        self.__rcptto = ''
        self.__domainname = domianname
        self.__clientip = clientip
        self.__isssl =  isssl
        self.__istx = False
        self.send('220 pMail Server ready\r\n')
    def parse(self, line_string):     
        cmd_string = re.split('\r|\n', line_string, 1)[0]
        if((self.__status & selfdef.PHASE_USERNAME) == selfdef.PHASE_USERNAME):
            self.__username = base64.b64decode(cmd_string)
            self.__status ^= selfdef.PHASE_USERNAME
            self.__status |= selfdef.PHASE_PASSWORD
            self.send('334 UGFzc3dvcmQ6\r\n')
            
        elif ((self.__status & selfdef.PHASE_PASSWORD) == selfdef.PHASE_PASSWORD):
            self.__password = base64.b64decode(cmd_string)
            if self.__ps.checklogin(self.__username, self.__password) == True:
                self.__status ^= selfdef.PHASE_PASSWORD
                self.__status |= selfdef.PHASE_AUTHED
                self.send('235 authentication successful.\r\n')
            else:
                self.__status ^= selfdef.PHASE_PASSWORD
                self.send('535 authentication failed.\r\n')
                
        elif ((self.__status & selfdef.PHASE_DATAING) == selfdef.PHASE_DATAING):
            self.__mailbody += line_string
            if len(self.__mailbody) > selfdef.MAX_EMAIL_LENGTH:
                return False
            
            if(cmd_string == ''):
                self.__status |= selfdef.PHASE_DATAED
            elif(cmd_string == '.') and ((self.__status & selfdef.PHASE_DATAED) == selfdef.PHASE_DATAED):
                self.__status ^= selfdef.PHASE_DATAED
                self.__status ^= selfdef.PHASE_DATAING
                self.__mailbody = re.sub('\r\n\.\r\n|\n\.\n|\r\n\.\n|\n\.\r\n', '', self.__mailbody)


                if self.__istx == False:
                    now_time = time.time()
                    str_uniqid = ''
                    for i in range(0,22):
                        str_uniqid += '%c'%random.choice('1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_')
                    self.__ps.insertmail(str_uniqid, self.__mailfrom, re.split('@',self.__rcptto)[0], \
                                         self.__mailbody, int(now_time), 'N')
                self.send('250 requested mail action okay, completed.\r\n')
            else:
                self.__status ^= selfdef.PHASE_DATAED
                
        else:
            cmd_unit = re.split(' |\t', cmd_string)
            cmd_main = cmd_unit[0].lower()
            
            if(cmd_main == 'ehlo'):
                self.__status |= selfdef.PHASE_EHELLOED
                self.__helloname = cmd_unit[1]
                self.send('''250-smtp3
250-PIPELINING
250-AUTH LOGIN PLAIN NTLM
250-AUTH=LOGIN PLAIN NTLM
250-8BITMIME
250 OK
''')
                
            elif(cmd_main == 'helo'):
                self.__status |= selfdef.PHASE_HELLOED
                self.__helloname = cmd_unit[1]
                self.send('250 requested mail action okay, completed\r\n')

            elif(cmd_main == 'auth'):
                self.send('334 VXNlcm5hbWU6\r\n')
                self.__status |= selfdef.PHASE_USERNAME

            elif(cmd_main == 'mail'):
                if self.__status & selfdef.PHASE_AUTHED != selfdef.PHASE_AUTHED and self.__status & selfdef.PHASE_HELLOED != selfdef.PHASE_HELLOED:
                    self.send('503 bad sequence of commands\r\n')
                else:
                    self.__mailfrom = re.split('<|>',cmd_string)[1]
                    if self.__status & selfdef.PHASE_HELLOED == selfdef.PHASE_HELLOED and self.__mailfrom.strip()  ==  '':
                        self.send('250 requested mail action okay, completed\r\n')
                    elif self.__status & selfdef.PHASE_EHELLOED == selfdef.PHASE_EHELLOED and self.__mailfrom.strip() == '%s@%s'%(self.__username,self.__domainname):
                        self.send('250 requested mail action okay, completed\r\n')
                    else:
                        self.send('553 mail address forbid\r\n');

            elif(cmd_main == 'rcpt'):
                if self.__status & selfdef.PHASE_AUTHED != selfdef.PHASE_AUTHED and self.__status & selfdef.PHASE_HELLOED != selfdef.PHASE_HELLOED:
                    self.send('503 bad sequence of commands\r\n')
                else:
                    self.__rcptto = re.split('<|>',cmd_string)[1]
                    if re.match('.+@.+', self.__rcptto) == None:
                        self.send('553 rcpt mail address error\r\n')
                    else:
                        if re.match('.+%s'%self.__domainname, self.__rcptto) == None:
                            self.__istx = True
                            self.send('250 requested mail action okay, completed\r\n')
                        else:
                            if self.__ps.verifyuser(re.split('@',self.__rcptto)[0]) == False:
                                self.send('553 sorry, that user is not in my user list\r\n')
                            else:
                                self.send('250 requested mail action okay, completed\r\n')

            elif cmd_main == 'rest':
                self.__status = selfdef.PHASE_HELLOED
                self.send('250 requested mail action okay, completed\r\n')
                
            elif(cmd_main == 'data'):
                if self.__status & selfdef.PHASE_AUTHED != selfdef.PHASE_AUTHED and self.__status & selfdef.PHASE_HELLOED != selfdef.PHASE_HELLOED:
                    self.send('503 bad sequence of commands\r\n')
                else:
                    self.__mailbody = ''
                    self.__status |= selfdef.PHASE_DATAING
                    self.send('354 send the mail data, end with . \r\n')
                
            elif(cmd_main == 'quit'):
                self.send('221 pMail service closing transmission channel from %s\r\n'%self.__helloname)
                if self.__istx == True:
                    now_time = time.time()
                    str_uniqid = ''
                    for i in range(0,22):
                        str_uniqid += '%c'%random.choice('1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_')

                    if time.timezone / -36 >= 0:
                        time_str = "%s +%04d"%(time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime()),time.timezone / -36)
                    else:
                        time_str = "%s -%04d"%(time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime()),time.timezone /36)
                        
                    zone_str = time.strftime("%Z", time.gmtime())
                    tx_stamp = "Received: from %s (unknown [%s]) by %s (Postfix) with SMTP id %s for <%s>; %s (%s)\r\n" \
                               %(self.__helloname, self.__clientip[0], self.__domainname,str_uniqid, self.__rcptto, time_str, zone_str)
                    #print tx_stamp
                    self.__mailbody = tx_stamp + self.__mailbody 
                    
                    tx = ptx.ptx()
                    if tx.txmail(self.__domainname, self.__mailfrom, self.__rcptto, self.__mailbody) == False:
                        #self.__ps.insertmail(str_uniqid, self.__mailfrom, self.__rcptto, self.__mailbody, int(now_time), 'Y')
                        retrun_mailbody = '''From: "postmaster" <postmaster@%s>
To: "%s"
Subject: System Return Mail
Date: %s
MIME-Version: 1.0
Content-Type: multipart/mixed;
	boundary="----=_NextPart_000_006A_01C8A3B0.2E680640"
X-Priority: 3
X-MSMail-Priority: Normal
X-Unsent: 1
X-MimeOLE: Produced By Microsoft MimeOLE V6.00.2900.3028

This is a multi-part message in MIME format.

------=_NextPart_000_006A_01C8A3B0.2E680640
Content-Type: text/plain;
	format=flowed;
	charset="gb2312";
	reply-type=original
Content-Transfer-Encoding: 7bit

This message is generated by pMail system.
I'm sorry to have to inform you that the message returned.

Send to: %s failed
Cause: %s
------=_NextPart_000_006A_01C8A3B0.2E680640
Content-Type: message/rfc822;
	name="%s.eml"
Content-Transfer-Encoding: 7bit
Content-Disposition: attachment;
	filename="%s.eml"

%s

------=_NextPart_000_006A_01C8A3B0.2E680640--
'''%(self.__domainname, self.__mailfrom, time_str, self.__rcptto, tx.errmsg, str_uniqid, str_uniqid, self.__mailbody)
                        #print retrun_mailbody
                        self.__ps.insertmail(str_uniqid, 'postmaster@%s'%self.__domainname, re.split('@', self.__mailfrom)[0], retrun_mailbody, int(now_time), 'N')
                        
                return False
            else:
                self.send('502 command not implemented[%s].\r\n'%cmd_main)
        return True
        
if __name__ == '__main__':
    print 0
    
