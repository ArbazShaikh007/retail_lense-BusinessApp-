import jwt
import os
from datetime import datetime, timedelta
from flask import request, jsonify
from flask_restful import Resource
from base.database.db import db
from dotenv import load_dotenv
from pathlib import Path
from base.common.utils import upload_photos
from base.apis.v1.user.models import User,token_required


# env_path = Path('/var/www/html/backend/base/.env')
# load_dotenv(dotenv_path=env_path)

load_dotenv()
USER_FOLDER = 'base/static/images/'

# This is user register api to store data in to database and create jwt token for authentication
class UserRegisterResource(Resource):
    def post(self):
        try:
            data = request.get_json()

            firstname = data.get('firstname')
            lastname = data.get('lastname')
            email = data.get('email')
            country_code = data.get('country_code')
            mobile_number = data.get('mobile_number')
            dob = data.get('dob')

            device_token = data.get('device_token')
            device_type = data.get('device_type')

            print('data',data)

            if not firstname:
                return jsonify({'status': 0,'message': 'Please provide firstname'})
            if not lastname:
                return jsonify({'status': 0,'message': 'Please provide lastname'})

            if not email:
                return jsonify({'status': 0,'message': 'Please provide email'})
            if not country_code:
                return jsonify({'status': 0,'message': 'Please provide country code'})
            if not mobile_number:
                return jsonify({'status': 0,'message': 'Please provide mobile_number'})
            if not dob:
                return jsonify({'status': 0,'message': 'Please provide date of birth'})

            if dob:
                dob = datetime.strptime(dob, "%d-%m-%Y").strftime("%Y-%m-%d")

            # dob_data = datetime.strptime(dob, "%Y-%m-%d").date()
            # today = date.today()
            # age = today.year - dob_data.year - ((today.month, today.day) < (dob_data.month, dob_data.day))
            #
            # if age < 1    2:
            #     return {"status": 0, "message": "User must be at least 12 years old."}

            check_email = User.query.filter_by(email=email, is_deleted=False).first()
            check_mobile_number = User.query.filter_by(mobile_number=mobile_number, is_deleted=False).first()

            if check_email:
                if check_email.is_block == True:
                    return jsonify({'status':0,'message': 'Your account blocked by admin with this email.'})
                return jsonify({'status':0,'message': 'User already exists with this email.'})

            if check_mobile_number:
                if check_mobile_number.is_block == True:
                    return jsonify({'status':0,'message': 'Your account blocked by admin with this mobile number.'})
                return jsonify({'status':0,'message': 'User already exists with this mobile number.'})

            add_user = User(mobile_number=mobile_number,country_code=country_code,dob=dob,firstname=firstname,lastname=lastname,email=email,
                                profile_pic=None
                                ,profile_pic_path=None,created_time = datetime.utcnow(),device_token=device_token,device_type=device_type)

            db.session.add(add_user)
            db.session.commit()

            token = jwt.encode({'id': add_user.id,'exp': datetime.utcnow() + timedelta(days=365)},
                                   os.getenv("SECRET_KEY"))

            return jsonify({'status': 1,'message': 'Register successfully','data': add_user.as_dict_user_token(token)})

        except Exception as e:
            print('errorrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': 'Something went wrong'}, 500

# This is user login api
class UserLoginResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            country_code = data.get('country_code')
            mobile_number = data.get('mobile_number')
            device_token = data.get('device_token')
            device_type = data.get('device_type')

            check_user = User.query.filter_by(mobile_number=mobile_number,country_code=country_code, is_deleted=False).first()

            if check_user:
                if check_user.is_block == True:
                    return jsonify({'status': 0, 'message': 'Your account blocked by admin with this mobile number.'})

            if not check_user:
                return jsonify({'status': 0, 'message': 'Invalid mobile number,please try again'})


            none_exitsting_device_token = User.query.filter_by(device_token=device_token).first()
            if none_exitsting_device_token:
                none_exitsting_device_token.device_token = None
                none_exitsting_device_token.device_type = None
                db.session.commit()

                check_user.device_token = device_token
                check_user.device_type = device_type
                db.session.commit()


            token = jwt.encode({'id': check_user.id,'type': 'User', 'exp': datetime.utcnow() + timedelta(days=365)},os.getenv("SECRET_KEY"))

            return jsonify({ 'status': 1, 'message':'Login successfully','data': check_user.as_dict_user_token(token)})

        except Exception as e:
            print('errorrrrrrrrrrrrrrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': 'Something went wrong'}, 500

# This api for testing otp scenario
class StaticOtpVerifyResource(Resource):
    @token_required
    def get(self,active_user):
        try:
            active_user.is_otp = True
            db.session.commit()

            return jsonify({'status': 1,'message': 'Success','data': active_user.as_dict_user()})

        except Exception as e:
            print('errorrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': 'Something went wrong'}, 500

# This api for the user can update own profile informations, and retrive user profile
class UserUpdateResource(Resource):
    @token_required
    def post(self,active_user):
        try:
            data = request.form

            firstname = data.get('firstname')
            lastname = data.get('lastname')
            country_code = data.get('country_code')
            mobile_number = data.get('mobile_number')
            dob = data.get('dob')
            profile_pic = request.files.get('profile_pic')

            print('data',data)

            if not firstname:
                return jsonify({'status': 0,'message': 'Please provide firstname'})
            if not lastname:
                return jsonify({'status': 0,'message': 'Please provide lastname'})

            if not country_code:
                return jsonify({'status': 0,'message': 'Please provide country code'})
            if not mobile_number:
                return jsonify({'status': 0,'message': 'Please provide mobile_number'})
            if not dob:
                return jsonify({'status': 0,'message': 'Please provide date of birth'})

            if dob:
                dob = datetime.strptime(dob, "%d-%m-%Y").strftime("%Y-%m-%d")

            # dob_data = datetime.strptime(dob, "%Y-%m-%d").date()
            # today = date.today()
            # age = today.year - dob_data.year - ((today.month, today.day) < (dob_data.month, dob_data.day))
            #
            # if age < 1    2:
            #     return {"status": 0, "message": "User must be at least 12 years old."}

            check_mobile_number = User.query.filter(User.mobile_number==mobile_number, User.is_deleted==False,User.id != active_user.id).first()

            if check_mobile_number:
                return jsonify({'status':0,'message': 'User already exists with this mobile number.'})

            profile_pic_name = active_user.profile_pic
            profile_pic_path = active_user.profile_pic_path

            if profile_pic:
                file_path, picture = upload_photos(profile_pic)
                profile_pic_name = picture
                profile_pic_path = file_path

            active_user.mobile_number = mobile_number
            active_user.country_code = country_code
            active_user.dob = dob
            active_user.firstname = firstname
            active_user.lastname = lastname
            active_user.profile_pic = profile_pic_name
            active_user.profile_pic_path = profile_pic_path

            db.session.commit()

            return jsonify({'status': 1,'message': 'Profile updated successfully','data': active_user.as_dict_user()})

        except Exception as e:
            print('errorrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': 'Something went wrong'}, 500

    @token_required
    def get(self, active_user):
        try:
            return jsonify({'status': 1, 'message': 'Success', 'data': active_user.as_dict_user()})
        except Exception as e:
            print('errorrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': 'Something went wrong'}, 500

