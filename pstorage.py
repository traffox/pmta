import MySQLdb
import md5, sys

class pstorage():
    def __init__(self ,dbhost, username, password, dbname):
        try:
            self.__conn = MySQLdb.Connection(dbhost, username, password, dbname)
        except Exception, e:
            print 'DEBUG: Open MYSQL:', e

    def __del__(self):
        self.__conn.close()
        
    def checklogin(self, uname, password):
        hmd5 = md5.new()
        hmd5.update(password)
        sqlcmd = "select * from usertbl where uname='%s' and upasswd ='%s'"%(uname, hmd5.hexdigest())
        cur = self.__conn.cursor()
        cur.execute(sqlcmd)
        if len(cur.fetchall()) > 0:
            return True
        else:
            return False
              
    def adduser(self, uname, password, alias, utype):
        sqlcmd = "select * from usertbl where uname='%s'"%uname
        cur = self.__conn.cursor()
        cur.execute(sqlcmd)
        if len(cur.fetchall()) > 0:
            return False
        
        hmd5 = md5.new()
        hmd5.update(password)
        sqlcmd = "insert into usertbl(uname, upasswd, ualias, utype) values('%s', '%s', '%s', '%s')"%(uname, hmd5.hexdigest(), alias, utype)
        cur = self.__conn.cursor()
        cur.execute(sqlcmd)
        return True
    
    def deluser(self, uname):
        sqlcmd = "select uname from usertbl where uname='%s'"%uname
        cur = self.__conn.cursor()
        cur.execute(sqlcmd)
        if len(cur.fetchall()) == 0:
            return False
        
        sqlcmd = "delete from usertbl where uname='%s'"%uname
        cur = self.__conn.cursor()
        cur.execute(sqlcmd)
        return True
    
    def insertmail(self, uniqid, from_addr, to_addr, mail_body, recv_time, need_tranfer):
        mail_body = mail_body.replace("'","''")
        sqlcmd = "insert into mailtbl(muniqid, mfrom, mto, mbody, mtime, mtx) values('%s','%s','%s','%s', %d , '%s')"%(uniqid, from_addr, to_addr, mail_body, recv_time, need_tranfer)
        #print sqlcmd
        cur = self.__conn.cursor()
        cur.execute(sqlcmd)
        
    def listmail(self, to_addr, listtbl):
        sqlcmd = "select length(mbody),muniqid, mid from mailtbl where mto='%s'"%to_addr
        cur = self.__conn.cursor()
        cur.execute(sqlcmd)
        listtbl[0] = cur.fetchall()

    def listuser(self, uname, listtbl):
        if uname == '':
            sqlcmd = "select uname, ualias from usertbl"
        else:
            sqlcmd = "select uname, ualias from usertbl where uname='%s'"%uname
        cur = self.__conn.cursor()
        cur.execute(sqlcmd)
        listtbl[0] = cur.fetchall()
        
    def verifyuser(self, uname):
        sqlcmd = "select uname from usertbl where uname='%s'"%uname
        cur = self.__conn.cursor()
        cur.execute(sqlcmd)
        if len(cur.fetchall()) == 0:
            return False
        return True
    
    def passwd(self, uname, upasswd, listtbl):
        upasswd = upasswd.replace("'","''")
        sqlcmd = "select uname from usertbl where uname='%s'"%uname
        cur = self.__conn.cursor()
        cur.execute(sqlcmd)
        if len(cur.fetchall()) == 0:
            return False
        sqlcmd = "update set upasswd='%s' usertbl where uname='%s'"%(upasswd,uname)
        cur = self.__conn.cursor()
        cur.execute(sqlcmd)
        return True
        
    def getmailbody(self, mid, mailbody):
        sqlcmd = "select mbody from mailtbl where mid='%s'"%mid
        cur = self.__conn.cursor()
        cur.execute(sqlcmd)
        mailbody[0] = cur.fetchall()[0][0]

    def delmail(self, mid):
        sqlcmd = "delete from mailtbl where mid='%s'"%mid
        cur = self.__conn.cursor()
        cur.execute(sqlcmd)

    def setupdb(self):
        sqlcmd = '''CREATE TABLE `pmailbox`.`usertbl` (
`uid` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
`uname` VARCHAR( 255 ) NOT NULL ,
`upasswd` VARCHAR( 255 ) NOT NULL ,
`ualias` VARCHAR( 255 ) NOT NULL ,
`utype` VARCHAR( 2 ) NOT NULL ,
PRIMARY KEY ( `uid` ) 
) ENGINE = MYISAM '''
        cur = self.__conn.cursor()
        cur.execute(sqlcmd)
        sqlcmd = '''CREATE TABLE `pmailbox`.`mailtbl` (
`mid` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
`muniqid` VARCHAR( 255 ) NOT NULL ,
`mfrom` VARCHAR( 255 ) NOT NULL ,
`mto` VARCHAR( 255 ) NOT NULL ,
`mbody` LONGTEXT NOT NULL ,
`mtime` INT NOT NULL ,
`mtx` VARCHAR( 2 ) NOT NULL ,
`mdeleted` VARCHAR( 2 ) NOT NULL DEFAULT 'N',
PRIMARY KEY ( `mid` ) 
) ENGINE = MYISAM '''
        cur = self.__conn.cursor()
        cur.execute(sqlcmd)
	
if __name__ == '__main__':
    if len(sys.argv) != 5:
        print 'usage: pstorage.py [hostname|ip] [username] [password] [datebase name]'
    else:
        ps = pstorage.pstorage(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
        ps.setupdb()
        print 'Datebase is ready.'
