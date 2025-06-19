from flask import request, make_response, render_template, jsonify, url_for, redirect
from flask_restful import Resource
from base.common.utils import admin_login_required
from datetime import datetime, timedelta
import os
import jwt
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from base.apis.v1.admin.models import Admin
from base.database.db import db
from base.common.utils import user_send_reset_email,upload_photos_local,upload_photos
from pathlib import Path
from dotenv import load_dotenv
# env_path = Path('/var/www/html/backend/base/.env')
# load_dotenv(dotenv_path=env_path)
load_dotenv()

UPLOAD_FOLDER = "base/static/images/"

class RegisterResource(Resource):
    def post(self):
        data = request.get_json()

        fullname = data.get("fullname")
        email = data.get("email")
        password = data.get("password")

        if not fullname:
            return jsonify({'status': 0,'message': 'Please provide fullname'})
        if not email:
            return jsonify({'status': 0,'message': 'Please provide email'})
        if not password:
            return jsonify({'status': 0,'message': 'Please provide password'})

        hashed_password = generate_password_hash(password)

        admin = Admin.query.filter_by(email=email).first()

        if admin:
            return jsonify({'status':0,'message': "Email already exists. Please try another one."})

        admin = Admin(
            fullname=fullname,
            email=email,
            password=hashed_password,
            created_at=datetime.utcnow(),
        )

        db.session.add(admin)
        db.session.commit()

        token = jwt.encode(
            {"id": admin.id, "exp": datetime.utcnow() + timedelta(days=365)},
            os.getenv("ADMIN_SECRET_KEY"),
        )

        return jsonify({'status': 1,'message': "Registration successfully.", 'data':admin.as_dict(token)})

class LoginResource(Resource):
    def post(self):
        data = request.get_json()

        email = data.get("email")
        password = data.get("password")

        admin = Admin.query.filter_by(email=email).first()

        if admin and check_password_hash(admin.password, password):
            token = jwt.encode(
                {"id": admin.id, "exp": datetime.utcnow() + timedelta(days=365)},
                os.getenv("ADMIN_SECRET_KEY"),
            )

            return jsonify({'status': 1,'message': "Login successfully.", 'data':admin.as_dict(token)})
        else:
            return jsonify({'status': 0,'message': "Invalid email or password."})

class GetUserResource(Resource):
    @admin_login_required
    def get(self, active_user):
        token = request.headers.get("authorization")
        return jsonify({'status':1,'message':"Success",'data': active_user.as_dict(token)})

class ChangePasswordResource(Resource):
    @admin_login_required
    def put(self, active_user):

        data = request.get_json()

        current_password = data.get("current_password")
        new_password = data.get("new_password")

        if check_password_hash(active_user.password, current_password):
            active_user.password = generate_password_hash(new_password)
            db.session.commit()

            return jsonify({'status': 1,'message': "Password changed successfully."})
        else:
            return jsonify({'status': 0,'message': "Invalid current password."})

class EditProfileResource(Resource):
    @admin_login_required
    def put(self, active_user):
        try:
            token = request.headers.get("authorization")

            data = request.form

            fullname = data.get("fullname")
            email = data.get("email")
            file = request.files.get("file")

            admin = Admin.query.filter(Admin.email==email,Admin.id != active_user.id).first()

            if admin:
                return jsonify({'status': 0,'message': "Email already exists."})

            active_user.fullname = fullname
            active_user.email = email

            profile_pic = active_user.profile_pic
            profile_pic_path = active_user.profile_pic_path

            if file:
                file_path, picture = upload_photos(file)
                profile_pic = picture
                profile_pic_path = file_path

            active_user.profile_pic = profile_pic
            active_user.profile_pic_path = profile_pic_path

            db.session.commit()

            return jsonify({'status':1,'message': "Profile updated successfully.", 'data':active_user.as_dict(token)})
        except Exception as e:
            print('errorrrrrrrrrrrrrrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': 'Something went wrong'}, 400

class AdminForgetPassword(Resource):
    def post(self):
        try:
            email = request.json.get('email')
            if not email:
                return jsonify({'status': 0, 'message': 'Please enter your email'})

            admin_data = Admin.query.filter_by(email=email).first()
            if not admin_data:
                return jsonify({'status': 0, 'message': 'Wrong email address you entered try again'})
            else:
                user_send_reset_email(admin_data,"admin")
                return jsonify({'status': 1, "message": "Reset password link sucessfully sent to your email"})

        except Exception as e:
            return {'status': 0, 'message': 'Something went wrong', 'error': str(e)}, 400

class AdminResetPassword(Resource):
    def get(self):
        token = request.args.get('token')
        print('token ', token)
        admin_data = Admin.verify_admin_token(token)

        if admin_data is None:
            return '<h5>Invalid or Expired Token</h5>'

        return make_response(render_template('resetPassword.html', common_path='', token=token,type = 'admin'))

    def post(self):
        token = request.args.get('token')
        print('runningggggggggggggggggggggggggggggggggggggggggggggg')
        admin_data = Admin.verify_admin_token(token)

        if admin_data is None:
            return '<h5>Invalid or Expired Token</h5>', 400  # Return a status code for an invalid token

        password = request.form.get('newPassword')
        hax_password = generate_password_hash(password)

        admin_data.password = hax_password

        db.session.commit()

        return make_response(redirect(url_for('success_page')))

class SuccessPage(Resource):
    def get(self):
        return make_response(render_template('success_msg.html', common_path=''))