import requests
from bs4 import BeautifulSoup
from flask_login import current_user

from . import db
from .models import Message, Student, Change


def ykps_auth(username, password):
    '''Authenticates the given credentials through Powerschool.'''
    url = 'https://powerschool.ykpaoschool.cn/guardian/home.html'
    form_data = {
        'account': username,
        'ldappassword': password,
        'pw': 'surveyor'
    }

    try:
        req = requests.post(url, data=form_data, timeout=5)
        soup = BeautifulSoup(req.text, 'html.parser')
        name = soup.select('#userName > span')[0].get_text().strip()
        ret = 0
    except Exception as e:
        name = str(e)
        ret = -1
    return ret, name


def get_available_students():
    '''(NOT USED) Get all students the current user has not written a message to.'''
    # Perform database query
    subquery = db.session.query(Message.recipient_id).filter(Message.author_id == current_user.student.id)
    query_filter = Student.id.notin_(subquery)
    students = Student.query.filter(query_filter).filter(Student.id != current_user.student.id).all()

    # Restructure data
    students = [student.get_id_name() for student in students]
    return students


def record_change(message_id, change_type, commit=False):
    '''Record a change in the status of a message.'''
    if change_type not in ('new', 'delete', 'edit'):
        return -1
    change = Change(message_id=message_id, change_type=change_type)
    db.session.add(change)
    if commit:
        db.session.commit()
