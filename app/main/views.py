"""
Main module
"""

import os
import hashlib
from collections import defaultdict

import mammoth

from app.urls import main_module

from flask import render_template
from flask import jsonify
from flask import request
from flask_login import login_required
from flask_login import current_user

from app.extensions import db
from app.models.files import Files
from app.models.files import FilePermissions
from app.models.departments import Department
from app.models.user import UserDepartment
from app.models.user import User
from werkzeug.exceptions import Forbidden

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

UPLOAD_PATH = os.path.join(
    BASE_DIR,
    'app',
    'static',
    'uploads'
)


@main_module.route('')
@login_required
def index():
    rows = Files.query.filter(Files.active == 1, Files.parent_id == 0).all()

    departments = [{'id': row.id, 'name': row.name} for row in Department.query.all()]

    departments_dict = {d['id']: d['name'] for d in departments}

    user_department = UserDepartment.query. \
        filter(UserDepartment.user_id == current_user.id).first()

    user_department_name = departments_dict[user_department.department_id]

    files_by_department = defaultdict(list)
    for row in rows:
        files_by_department[row.department_id].append({
            'id': row.id,
            'department_id': row.department_id,
            'title': row.title,
            'file_name': row.file_name,
            'file_size': row.file_size,
            'parent_id': row.parent_id,
            'active': row.active
        })

    return render_template(
        'main/index.html',
        rows=rows,
        departments=departments,
        files_by_department=files_by_department,
        user_department_name=user_department_name
    )


@main_module.route('/menu')
@main_module.route('/menu/<int:parent_id>')
@login_required
def menu(parent_id=0):
    permissions = defaultdict(list)
    for f in FilePermissions.query.all():
        permissions[f.file_id].append(f.user_id)

    file_permission = permissions[parent_id]

    if file_permission and current_user.id not in file_permission:
        raise Forbidden()

    rows = Files.query.filter(Files.parent_id == parent_id, Files.active == 1).all()

    results = [{'title': row.title, 'id': row.id, 'parent_id': row.parent_id} for row in rows]

    file_content = Files.query.filter(Files.id == parent_id).first()

    file_path = '%s/%s/%s/%s' % (UPLOAD_PATH,
                                 file_content.department_id,
                                 file_content.parent_id, file_content.file_name)

    file_url = 'http://%s/static/uploads/%s/%s/%s' % (request.host,
                                                      file_content.department_id,
                                                      file_content.parent_id, file_content.file_name)

    if os.path.isfile(file_path):
        with open(file_path, 'rb') as doc_file:
            result = mammoth.convert_to_html(doc_file)
            html = result.value
    else:
        html = 'Nothing to show here.'

    return jsonify(results=results, parent_id=parent_id, content=html, file_url=file_url)


@main_module.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    departments = [{'id': row.id, 'name': row.name} for row in Department.query.all()]

    departments_dict = {d['id']: d['name'] for d in departments}

    user_department = UserDepartment.query. \
        filter(UserDepartment.user_id == current_user.id).first()

    user_department_name = departments_dict[user_department.department_id]
    message = ''
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        user = User.query.\
            filter(User.id == current_user.id, User.password == hashlib.md5(current_password.encode()).hexdigest()).\
            first()
        if user:
            user.password = hashlib.md5(confirm_password.encode()).hexdigest()
            db.session.add(user)
            db.session.commit()
            message = 'Congratulation! Your password been successfully updated.'
        else:
            message = 'Sorry. Your current password does not match any records.'

        if new_password != confirm_password:
            message = 'Sorry. Password does not match.'

    return render_template(
        'main/settings.html',
        user_department_name=user_department_name,
        message=message
    )
