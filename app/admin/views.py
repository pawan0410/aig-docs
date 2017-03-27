"""
Admin module
"""
import os
import sqlalchemy
from collections import defaultdict
import ftplib

from app.urls import admin_module
from flask import render_template
from flask import request
from flask_login import current_user
from flask_login import login_required
from flask import redirect
from flask import current_app

from app.models.user import UserDepartment
from app.models.files import Files
from app.models.files import FilePermissions
from app.models.departments import Department
from app.extensions import db
from .utils import admin_required

from werkzeug.utils import secure_filename
from werkzeug.exceptions import BadRequest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

UPLOAD_PATH = os.path.join(
    BASE_DIR,
    'app',
    'static',
    'uploads'
)


@admin_module.route('/')
@admin_module.route('/<int:parent_id>')
@login_required
@admin_required
def index(parent_id=0):
    user_department = UserDepartment.query. \
        filter(UserDepartment.user_id == current_user.id).first()

    rows = Files.query.filter(Files.parent_id == parent_id, Files.department_id == user_department.department_id).all()

    departments = [{'id': row.id, 'name': row.name} for row in Department.query.all()]

    departments_dict = {d['id']: d['name'] for d in departments}

    users_data = db.session.execute("""
    select ud.user_id, u.name, ud.department_id from users u, user_department ud, \
    departments d where u.id=ud.user_id and ud.department_id=d.id;
    """)

    users = defaultdict(list)
    for u in users_data:
        users[u.department_id].append({
            'user_id': u.user_id,
            'name': u.name,
            'department_id': u.department_id
        })

    permissions = defaultdict(list)
    for f in FilePermissions.query.all():
        permissions[f.file_id].append(f.user_id)

    user_department_name = departments_dict[user_department.department_id]
    return render_template(
        'admin/index.html',
        rows=rows,
        parent_id=parent_id,
        departments=departments,
        users=users,
        permissions=permissions,
        user_department_name=user_department_name
    )


@admin_module.route('/upload', methods=['GET', 'POST', ])
@admin_module.route('/upload/<int:parent_id>', methods=['GET', 'POST', ])
@login_required
@admin_required
def upload(parent_id=0):

    success = ''
    error = ''

    user_department = UserDepartment.query. \
        filter(UserDepartment.user_id == current_user.id).first()

    departments_dict = {row.id: row.name for row in Department.query.all()}
    user_department_name = departments_dict[user_department.department_id]

    try:
        title = Files.query.get(parent_id).title
    except AttributeError:
        title = ''

    if request.method == 'POST':
        title = request.form['title']
        parent_id = parent_id
        file = request.files['file']
        active = request.form.get('active', type=int, default=0)

        filename = secure_filename(file.filename) if file else ''
        file_size = 0

        if not filename.endswith('.docx'):
            raise BadRequest('Only docx file is allowed.')

        upload_path = '%s/%s/%s' % (UPLOAD_PATH, user_department.department_id, parent_id)

        if file:
            os.makedirs(upload_path, exist_ok=True)
            file.save(
                os.path.join(upload_path, filename)
            )
            file_size = os.path.getsize(os.path.join(upload_path, filename)) // 1024

            ftp_path = r'{0}/{1}'.format(
                user_department.department_id, parent_id
            )

            with ftplib.FTP(current_app.config['FTP_SERVER']) as ftp:
                try:
                    ftp.login(user=current_app.config['FTP_USER'], passwd=current_app.config['FTP_PASSWORD'])
                except ftplib.error_perm:
                    pass
                else:
                    for f in ftp_path.split('/'):
                        try:
                            ftp.mkd(f)
                            ftp.cwd(f)
                        except ftplib.error_perm:
                            ftp.cwd(f)
                    with open(os.path.join(upload_path, filename), 'rb') as upload_file:
                        ftp.storbinary('STOR %s' % filename, upload_file)
                    ftp.quit()

        f = Files(
            department_id=user_department.department_id,
            title=title,
            file_name=filename,
            file_size=file_size,
            parent_id=parent_id,
            active=active,
            updated_by=current_user.id
        )

        try:
            db.session.add(f)
            db.session.commit()
        except sqlalchemy.exc.OperationalError:
            pass
        else:
            return redirect('/admin/%d' % parent_id)

    return render_template(
        'admin/upload.html',
        success=success,
        error=error,
        parent_id=parent_id,
        title=title,
        user_department_name=user_department_name
    )


@admin_module.route('/user_permissions', methods=['GET', 'POST', ])
@login_required
@admin_required
def user_permissions():
    user_ids = request.form.getlist('user_ids[]')
    file_id = request.form.get('fileid', type=int)

    try:
        FilePermissions.query.filter(FilePermissions.file_id == file_id).delete()
        db.session.add_all(
            [FilePermissions(
                user_id=u,
                file_id=file_id
            ) for u in user_ids]
        )
        db.session.commit()
    except sqlalchemy.exc.OperationalError:
        return 'Oops! Please try again.'
    return 'success'


@admin_module.route('/publish_file', methods=['GET', 'POST', ])
@login_required
@admin_required
def publish_file():
    file_id = request.form.get('fileid')
    status = request.form.get('status')

    try:
        f = Files.query.get(file_id)
        f.active = status
        db.session.add(f)
        db.session.commit()
    except sqlalchemy.exc.OperationalError:
        return 'Oops! Please try again.'
    return 'success'


@admin_module.route('/change_file', methods=['POST', ])
@login_required
@admin_required
def change_file():
    title = request.form['title']
    file = request.files['file']
    fileid = request.form['fileid']

    filename = secure_filename(file.filename) if file else ''

    if not filename.endswith('.docx'):
        raise BadRequest('Only docx file is allowed.')

    file_data = Files.query.get(fileid)

    user_department = UserDepartment.query.\
        filter(UserDepartment.user_id == current_user.id).first()

    upload_path = '%s/%s/%s' % (UPLOAD_PATH, user_department.department_id, file_data.parent_id)

    if file and file_data:
        os.makedirs(upload_path, exist_ok=True)
        file.save(
            os.path.join(upload_path, filename)
        )
        file_size = os.path.getsize(os.path.join(upload_path, filename)) // 1024

        file_data.department_id = user_department.department_id
        file_data.title = title
        file_data.file_name = filename
        file_data.file_size = file_size
        file_data.updated_by = current_user.id

        try:
            db.session.add(file_data)
            db.session.commit()
        except sqlalchemy.exc.OperationalError:
            pass
        else:
            return redirect('/admin/%d' % file_data.parent_id)

    return ''
