from flask import jsonify, render_template, request, abort, current_app, send_from_directory
from flask_login import login_required, current_user
import json
import os
import re
from . import main
from ..models import User, Package, PackageVersion
from .. import db
from .publish import publish

@main.route('/packages/<package>/<package_version>/<filename>', methods=['GET'])
def install_route(package, package_version, filename):
    if not current_app.config['ALLOW_INSTALLATION']:
        return 'Installation is not currently enabled on this server.', 403

    if not current_user.is_authenticated and current_app.config['REQUIRE_LOGIN_TO_INSTALL']:
        if not current_user.admin and current_app.config['REQUIRE_ADMIN_TO_INSTALL']:
            return current_app.login_manager.unauthorized()
        return current_app.login_manager.unauthorized()

    package_dir = os.path.join(current_app.root_path, 'packages', package, package_version)
    return send_from_directory(package_dir, filename)

@main.route('/packages/<package>/<package_version>.json', methods=['GET'])
def package_info_route(package, package_version):
    package_version_obj = PackageVersion.query.join(Package).filter(
        Package.name == package, 
        PackageVersion.version == package_version
    ).first()

    if package_version_obj is None:
        return jsonify({"error": "Package not found"}), 404

    package_data = {
        "package": package_version_obj.package.name,
        "name": package_version_obj.name,
        "shortDescription": package_version_obj.short_description,
        "description": package_version_obj.description,
        "version": package_version_obj.version,
        "dependencies": package_version_obj.dependencies,
        "files": package_version_obj.files
    }

    return jsonify(package_data), 200

@main.route('/packages/<package>/latest.json', methods=['GET'])
def latest_package_info_route(package):
    latest_package_version = PackageVersion.query.join(Package).filter(
        Package.name == package
    ).order_by(PackageVersion.version.desc()).first()

    if latest_package_version is None:
        return jsonify({"error": "Package not found"}), 404
    
    package_data = {
        "package": latest_package_version.package.name,
        "name": latest_package_version.name,
        "shortDescription": latest_package_version.short_description,
        "description": latest_package_version.description,
        "version": latest_package_version.version,
        "files": latest_package_version.files
    }
    
    return jsonify(package_data), 200

@main.route('/publish', methods=['POST'])
@login_required
def publish_route():
    return publish()

@main.route('/userinfo', methods=['GET'])
@login_required
def getownuserinfo():
    user_data = {
        "id": current_user.id,
        "username": current_user.username,
        "mail": current_user.mail,
        "packages": current_user.packages
    }
    return jsonify(user_data), 200

@main.route('/userinfo', methods=['POST'])
def getuserinfo():
    data = request.get_json()
    user = User.query.filter_by(id=data['id']).first()

    if not user:
        abort(404)

    user_data = {
        "id": user.id,
        "username": user.username,
        "mail": user.mail,
        "packages": user.packages
    }

    return jsonify(user_data), 200

@main.route('/changeuserinfo', methods=['POST'])
def setuserinfo():
    data = request.get_json

    if current_user.admin == False:
        return "You must be a server administrator to perform this action.", 403

    user = User.query.filter_by(id=data['id']) if 'id' in data else None
    if 'username' in data: user.username = data['username']
    if 'newID' in data: user.id = data['newID']
    if 'mail' in data: user.mail = data['mail']
    if 'packages' in data: user.packages = data['packages']
    if 'admin' in data: user.admin = bool(data['admin'])
