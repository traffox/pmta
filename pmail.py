import socket, select
import threading
import psession
import sys
import pstorage
import pcli

if __name__ == '__main__':
    if len(sys.argv) == 6:
        param_db_host = sys.argv[1]
        param_db_user = sys.argv[2]
        param_db_pwd = sys.argv[3]
        param_db_name = sys.argv[4]
        param_domia_name = sys.argv[5]
    else:
        param_db_host = raw_input('Datebase Hostname:')
        param_db_user = raw_input('Datebase Username:')
        param_db_pwd = raw_input('Datebase Password')
        param_db_name = raw_input('Datebase Name:')
        param_domia_name = raw_input('Mail Domian Name:')

    mailbox_db = pstorage.pstorage(param_db_host, param_db_user, param_db_pwd, param_db_name)
    domain_name = param_domia_name
    
    smtp_sockfd_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    pop3_sockfd_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    
    smtp_sockfd_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    pop3_sockfd_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    smtp_sockfd_s.bind(('', 25))
    pop3_sockfd_s.bind(('', 110))

    smtp_sockfd_s.listen(5)
    pop3_sockfd_s.listen(5)
    detect_fds = [smtp_sockfd_s, pop3_sockfd_s, sys.stdin]
    bRuning = True
    print 'Welcome to pMail Server console.'
    print '>>',
    sys.stdout.flush()
    cli = pcli.pcli(mailbox_db)
    while bRuning:
        try:
            rrdy, wrdy, erdy = select.select(detect_fds, [], [], 0.1)
            
            for fd in rrdy:
                if fd == smtp_sockfd_s:
                    try:
                        smtp_sockfd_c, smtp_c_addr = smtp_sockfd_s.accept()
                        try:
                            smtp_hsid = psession.psession(mailbox_db, domain_name, [smtp_sockfd_c, None, smtp_c_addr], 0)
                            smtp_hsid.start()
                        except Exception, e:
                            print 'DEBUG: Create SMTP session:', e
                
                    except Exception, e:
                        print 'DEBUG: Accept SMTP client socket:',e
                
                elif fd == pop3_sockfd_s:
                    try:
                        pop3_sockfd_c, pop3_c_addr = pop3_sockfd_s.accept()
                        try:
                            pop3_hsid = psession.psession(mailbox_db, domain_name, [pop3_sockfd_c, None, pop3_c_addr], 1)
                            pop3_hsid.start()
                        except Exception, e:
                            print 'DEBUG: Create POP3 session:', e
                
                    except Exception, e:
                        print 'DEBUG: Accept POP3 client socket:',e
                        
                elif fd == sys.stdin:
                    try:
                        cli_string = sys.stdin.readline().strip()
                        bRuning = cli.parse(cli_string)
                        print '>>',
                        sys.stdout.flush()
                    except Exception, e:
                        print 'DEBUG: Read sys.stdio:',e
                        bRuning = False
        except Exception, e:
            bRuning = False
            print 'DEBUG: select.select:', e
    smtp_sockfd_s.close()
    pop3_sockfd_s.close()



