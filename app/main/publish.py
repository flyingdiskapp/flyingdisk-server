from flask import jsonify, render_template, request, abort, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import json
import os
import re
from . import main
from ..models import User, Package
from .. import db

allowed_package_names = re.compile(r'^[0-9A-Za-z-]{3,30}$')
allowed_versions = re.compile(r'^\d+(\.\d+)*(-[a-z]?\d*)?$')

def get_package_info(package_name, package_version=None):
    if package_version:
        return Package.query.filter_by(package=package_name, version=package_version).first()
    else:
        return Package.query.filter_by(package=package_name).all()

def save_package_info(package_info):
    package = Package(
        name=package_info['name'],
        description=package_info['description'],
        version=package_info['version'],
        dependencies=package_info['dependencies'],
        files=package_info['files']
    )
    db.session.add(package)
    db.session.commit()

def publish():
    data = json.loads(request.form.get('json'))

    if not allowed_package_names.match(data['name']):
        return 'Invalid package name', 400

    if not allowed_versions.match(data['version']):
        return 'Invalid package version', 400

    package_info_list = get_package_info(data['package'])

    if package_info_list:
        if not current_app.config['ALLOW_PUBLISHING_NEW_RELEASES']:
            return 'Publishing new releases is disabled on this server.', 403
        if data['name'] not in json.loads(current_user.packages):
            return f'You are not the original owner of {data["name"]}.', 401
    else:
        if not current_app.config['ALLOW_PUBLISHING_NEW_PACKAGES']:
            return 'Publishing new packages is disabled on this server.', 403

    if current_app.config['REQUIRE_ADMIN_TO_PUBLISH']:
        if not current_user.admin:
            return 'You must be an administrator of this server to publish!', 403

    if not package_info_list or data['version'] > max(pkg.version for pkg in package_info_list):
        package_data = {
            'package': data['package'],
            'name': data['name'],
            'shortDescription': data['shortDescription'],
            'description': data['description'],
            'version': data['version'],
            'files': []
        }

        files = request.files
        for file_key in files:
            file = files[file_key]
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.root_path, 'packages', data['package'], f"{data['version']}", filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            file.save(file_path)
            package_data['files'].append(filename)

        save_package_info(package_data)

        user_packages = json.loads(current_user.packages)
        if data['name'] not in user_packages:
            user_packages.append(data['name'])
            current_user.packages = json.dumps(user_packages)
            db.session.commit()

        return 'Package published successfully!', 200
    else:
        return f'Version {data["version"]} already exists for {data["packageName"]}.', 400