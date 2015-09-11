import email
import tempfile

if __name__ == '__main__':
    temp=tempfile.TemporaryFile()
    print temp
    temp.close()
    fp = open("mymail.eml", "r")
    msg = email.message_from_file(fp)
    subject = msg.get("subject")
    h = email.Header.Header(subject)
    dh = email.Header.decode_header(h)
    subject = dh[0][0]
    print "subject:", subject
    print "from: ", email.utils.parseaddr(msg.get("from"))[1]
    print "to: ", email.utils.parseaddr(msg.get("to"))[1]

    for par in msg.walk():
        if not par.is_multipart():
            name = par.get_param("name")
            if name:
                h = email.Header.Header(name)
                dh = email.Header.decode_header(h)
                fname = dh[0][0]
                print 'file name:', fname
                #data = par.get_payload(decode=False)
                #print data
            else:
                print par.get_payload(decode=True)
    fp.close()
