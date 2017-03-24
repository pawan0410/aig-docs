"""
Default module
"""

import hashlib

from app.urls import default_module
from app.models.user import User

from flask import render_template
from flask import request
from flask import url_for
from flask import redirect
from flask_login import login_user
from flask_login import logout_user
from flask_mail import Message

from app.extensions import login_manager
from app.extensions import db
from app.extensions import mail
from app.models.departments import Department
from app.models.user import UserDepartment


@login_manager.user_loader
def load_user(id):
    return User.query.filter(User.id == id, User.active == 1).first()


@default_module.route('', methods=['GET', 'POST', ])
def index():
    error = ''
    success = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(
            email=email,
            password=hashlib.md5(password.encode()).hexdigest()
        ).first()

        if user and user.active:
            user.authenticated = True
            login_user(user)
            db.session.commit()
            if user.admin():
                return render_template('default/admin_welcome.html')
            else:
                return redirect('/main')
        else:
            error = 'Invalid login..'

    return render_template(
        'default/index.html',
        error=error,
        success=success
    )


@default_module.route('logout')
def logout():
    logout_user()
    return redirect(url_for('default.views.index'))


@default_module.route('forgot_password', methods=['GET', 'POST'])
def forgot_password():
    message = ''
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter(User.email == email).first()
        if user:
            msg = Message('Password link', sender='reset@aigbusiness.in', recipients=[
                email
            ])
            link = 'http://{0}/reset?_={1}&__={2}'.format(request.host, user.password, user.email)
            msg.html = render_template(
                'default/forgot_password_email.html',
                name=user.name,
                link=link
            )
            mail.send(msg)

        message = 'You will shortly get an email. If the email provided by you exists in our database.'
        return render_template(
            'default/forgot_password.html',
            message=message
        )

    return render_template(
        'default/forgot_password.html',
        message=message
    )


@default_module.route('reset', methods=['GET', 'POST', ])
def reset_password():
    message = ''
    hash_code = request.args.get('_')
    email = request.args.get('__')

    if request.method == 'POST':
        hash_code = request.form['hashcode']
        email = request.form['email']
        password = request.form['new_password']

        user = User.query.\
            filter(User.email == email, User.password == hashlib.md5(password.encode()).hexdigest()).\
            first()

        if user:
            user.password = hashlib.md5(password.encode()).hexdigest()
            db.session.add(user)
            db.session.commit()
            message = 'Congratulation! Your password been successfully updated. &nbsp; <a href="/">Login</a>.'
            return render_template(
                'default/reset_password.html',
                message=message,
            )
        else:
            message = 'Sorry, Invalid Request..'
            return render_template(
                'default/reset_password.html',
                message=message,
                hash_code=hash_code,
                email=email
            )

    return render_template(
        'default/reset_password.html',
        hash_code=hash_code,
        email=email,
        message=message
    )


@default_module.route('sign_up', methods=['GET', 'POST', ])
def sign_up():

    departments = [{'id': row.id, 'name': row.name} for row in Department.query.all()]
    message = ''
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        password = request.form['password']
        department_id = request.form.get('department_id', type=int, default=0)

        user = User.query.filter(User.email == email).first()
        if user:
            message = 'Sorry, that email is already taken.'
        else:
            u = User(
                email=email,
                name=name,
                is_admin=0,
                active=1,
                password=hashlib.md5(password.encode()).hexdigest()
            )
            db.session.add(u)
            db.session.commit()

            db.session.add(UserDepartment(
                user_id=u.id,
                department_id=department_id
            ))
            db.session.commit()
            message = 'Congratulation ! Your registration has been successfully done. &nbsp;&nbsp;\
             <a href="/">Login</a>'

    return render_template(
        'default/sign_up.html',
        departments=departments,
        message=message
    )
