import socket
import select
import base64
import os,re
import dns.resolver

class pmta():
    def __init__(self):
        self.errmsg = ''
        
    def send(self, buf):
        try:
            byteswritten = 0
            while byteswritten < len(buf):
                byteswritten += self.__sockfd.send(buf[byteswritten:])
        except:
            pass
        
    def recvline(self, strline):
        detect_fds = [self.__sockfd,]
        rrdy, wrdy, erdy = select.select(detect_fds, [], [], 20)
        if len(rrdy) == 0:
            return False
        else:
            while True:
                try:
                    strtmp = self.__sockfd.recv(1)
                    strline[0] += strtmp[0]
                    if(strtmp[0] == '\n'):
                        break
                except:
                    return False
            return True
    
    def getresp(self, resp_str):
        while True:
            if(self.recvline(resp_str) == False):
                return False
            else:
                if resp_str[0][3] != '-':
                    break;
        return True  
        
    def mailhelo(self, hostname):
        self.send('helo %s\n'%hostname)
        #print 'helo %s\n'%hostname
        resp_str = ['',]
        if(self.getresp(resp_str) == False):
            return False
        if resp_str[0][0:3] == '250':
            return True
        else:
            self.errmsg = resp_str[0]
            return False
        
    def mailfrom(self, fromstr):
        self.send('mail from: <%s>\n'%fromstr)
        resp_str = ['',]
        if(self.getresp(resp_str) == False):
            return False
        if resp_str[0][0:3] == '250':
            return True
        else:
            self.errmsg = resp_str[0]
            return False
        
    def mailto(self, tostr):
        self.send('rcpt to: <%s>\n'%tostr)
        resp_str = ['',]
        if(self.getresp(resp_str) == False):
            return False
        if resp_str[0][0:3] == '250':
            return True
        else:
            self.errmsg = resp_str[0]
            return False
        
    def maildata(self):
        self.send('data\n')
        #print 'data'
        resp_str = ['',]
        if(self.getresp(resp_str) == False):
            return False
        if resp_str[0][0:3] == '354':
            return True
        else:
            self.errmsg = resp_str[0]
            return False
        
    def mailbody(self, bodystr):
        self.send(bodystr)
        self.send('\r\n.\r\n')
        resp_str = ['',]
        if(self.getresp(resp_str) == False):
            return False
        if resp_str[0][0:3] == '250':
            return True
        else:
            self.errmsg = resp_str[0]
            return False
        
    def mailquit(self):
        self.send('quit\n')
        resp_str = ['',]
        if(self.getresp(resp_str) == False):
            return False
        if resp_str[0][0:3] == '221':
            return True
        else:
            self.errmsg = resp_str[0]
            return False
        
    def sendmail(self, hostname, mailfrom, rcptto, bodystr):
        mail_postfix = re.split('@',rcptto)
		mx_server_list = dns.resolver.query(mail_postfix[1], 'MX')
		if len(mx_server_list) == 0:
            self.errmsg = 'Can not find MX server'
            return False
		for x in mx_server_list:
			return_val = True
            mx_server_ip = socket.gethostbyname(x.to_text())
            tx_sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
            try:
                tx_sockfd.connect((mx_server_ip, 25))
                self.__sockfd = tx_sockfd
                resp_str = ['',]
                self.getresp(resp_str)
                if self.mailhelo(hostname) and self.mailfrom(mailfrom) \
                   and self.mailto(rcptto) and self.maildata() and self.mailbody(bodystr) and self.mailquit():
                    pass
                else:
                    return_val = False
            except Exception, e:
                return_val = False
            try:    
                tx_sockfd.close()
            except:
                pass
            
            if return_val == True:
                break
        return return_val
    
if __name__ == '__main__':
    print 'hello world'
