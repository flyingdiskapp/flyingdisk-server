from flask import request, current_app
from flask_login import current_user
from werkzeug.utils import secure_filename  
import json
import os
import re
from ..models import Package, PackageVersion
from .. import db

def get_package_info(name, version=None):
    if version:
        return PackageVersion.query.filter_by(package_id=name, version=version).first()
    else:
        return PackageVersion.query.filter_by(package_id=name).all()

allowed_package_names = re.compile(r'^[0-9A-Za-z-]{3,30}$')
allowed_versions = re.compile(r'^\d+(\.\d+)*(-[a-z]?\d*)?$')

def save_info(info):
    package = Package.query.filter_by(name=info['name']).first()
    if not package:
        package = Package(name=info['name'], author=info['author'])
        db.session.add(package)
        db.session.commit()
    package_version = PackageVersion(
        package_id=package.id,
        version=info['version'],
        short_description=info['shortDescription'],
        description=info['description'],
        changelog=info['changelog'],
        files=info['files'],
        tags=info['tags']
    )
    db.session.add(package_version)
    db.session.commit()

def publish():
    data = json.loads(request.form.get('json'))

    if not allowed_package_names.match(data['name']):
        return 'Invalid package name', 400

    if not allowed_versions.match(data['version']):
        return 'Invalid package version', 400

    package_info_list = get_package_info(data['name'], data['version'])

    if package_info_list:
        return f'Version {data["version"]} already exists for {data["name"]}.', 400
    
    if data['package_id'] not in json.loads(current_user.packages) and current_app.config["UNIQUE_PUBLISHER"]:
        return f'You are not the original publisher of {data["name"]}.', 401

    if not current_app.config['ALLOW_PUBLISHING_NEW_MODS']:
        return 'Publishing new packages is disabled on this server.', 403

    if current_app.config['REQUIRE_ADMIN_TO_PUBLISH']:
        if not current_user.admin:
            return 'You must be an administrator of this server to publish!', 403

    package_data = {
        'name': data['name'],
        'shortDescription': data['shortDescription'],
        'description': data['description'],
        'version': data['version'],
        'changelog': data['changelog'],
        'files': [],
        'tags': data['tags']
    }

    files = request.files
    for file_key in files:
        file = files[file_key]
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.root_path, 'packages', data['name'], f"{data['version']}", filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file.save(file_path)
        package_data['files'].append(filename)

    save_info(package_data)

    user_packages = json.loads(current_user.publishedPackages)
    if data['name'] not in user_packages:
        user_packages.append(data['name'])
        current_user.publishedPackages = json.dumps(user_packages)
        db.session.commit()

    return 'Package published successfully!', 200
