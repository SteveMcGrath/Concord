from hashlib import md5
from time import time
from app.models import User, Submission, Ticket
from app import db

def genpw(username):
    pw = md5()
    pw.update(str(time()))
    pw.update(username)
    return pw.hexdigest()[:8]

def run():
    adminpw = genpw('admin')
    print 'Admin Password : %s' % adminpw
    user = User(username='admin', 
                password=adminpw, 
                email='admin@localhost',
                admin=True,
    )
    db.session.commit()
    user.gen_ticket(ticket_type='root')
    db.session.commit()