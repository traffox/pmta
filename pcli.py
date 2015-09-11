import re
import pstorage

class pcli():
    def __init__(self, ps):
        self.__ps = ps
        
    def parse(self, cli_string):
        cli_unit = re.split(' |\t', cli_string)
        if cli_unit[0] == 'quit':
            print 'Quit from pMail server.'
            return False

        if cli_unit[0] == 'help':
            print 'adduser deluser lsuser passwd'
            
        elif cli_unit[0] == 'adduser':
            if len(cli_unit) == 5:
                if self.__ps.adduser(cli_unit[1], cli_unit[2], cli_unit[3], cli_unit[4]) == False:
                    print 'add user failed'
                else:
                    print 'add user done'
            else:
                print 'wrong argrments; Usage: adduser [username] [password] [alias] [U|G]'
            
        elif cli_unit[0] == 'deluser':
            if len(cli_unit) == 2:
                if self.__ps.deluser(cli_unit[1]) == False:
                    print 'delete user failed'
                else:
                    print 'delete user done'
            else:
                print 'wrong argrments; Usage: deluser [username]'

        elif cli_unit[0] == 'passwd':
            if len(cli_unit) == 3:
                if self.__ps.passwd(cli_unit[1], cli_unit[2]) == False:
                    print 'change password failed'
                else:
                    print 'change password done'
            else:
                print 'wrong argrments; Usage: passwd [username] [password]'
                
        elif cli_unit[0] == 'lsuser':
            userlist = [[],]
            if len(cli_unit) == 2:
                self.__ps.listuser(cli_unit[1], userlist)
                if len(userlist[0]) == 0:
                    print 'no user named %s'%cli_unit[1]
                else:
                    for i in userlist[0]:
                        print '%s \t %s'%(i[0],i[1])
            elif len(cli_unit) == 1:
                self.__ps.listuser('', userlist)
                if len(userlist[0]) == 0:
                    print 'no user'
                else:
                    for i in userlist[0]:
                        print '%s \t %s'%(i[0],i[1])
            else:
                print 'wrong argrments; Usage: lsuser [username]  | userls'
                
        else:
            print 'unknown command.'
        return True
    
