from base.database.db import db
from functools import wraps
from flask import request
import jwt, os,json
from werkzeug.security import check_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer
from base.common.path import COMMON_URL
from datetime import datetime
from enum import Enum
from sqlalchemy.dialects.mysql import LONGTEXT
from base.common.path import generate_presigned_url
from pathlib import Path
from dotenv import load_dotenv
# env_path = Path('/var/www/html/backend/base/.env')
# load_dotenv(dotenv_path=env_path)
load_dotenv()

# This is user model to store user data
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, nullable=False)
    firstname = db.Column(db.String(150))
    lastname = db.Column(db.String(150))
    email = db.Column(db.String(50), nullable=False)

    country_code = db.Column(db.String(5))
    mobile_number = db.Column(db.String(20))

    profile_pic = db.Column(db.String(100))
    profile_pic_path = db.Column(db.String(200))
    dob = db.Column(db.Date)

    created_time = db.Column(db.DateTime)
    is_approved = db.Column(db.Boolean(), default=False)
    is_otp = db.Column(db.Boolean(), default=False)
    is_deleted = db.Column(db.Boolean(), default=False)
    delete_reason = db.Column(db.String(1000))
    deleted_time = db.Column(db.DateTime)
    is_block = db.Column(db.Boolean(), default=False)
    device_token = db.Column(db.String(500))
    device_type = db.Column(db.String(50))

    is_notification = db.Column(db.Boolean(), default=True)
    # user_delivery_details = db.relationship('LocationDetails', backref='user_delivery_details')
    delivery_comment_details = db.relationship('AddCommentDeliveryDetails', backref='delivery_comment_details')

    def get_user_token(self):
        serial = Serializer(os.getenv("SECRET_KEY"))
        return serial.dumps({'user_id': self.id})

    @staticmethod
    def verify_user_token(token, expiress_sec=1800):  # Add expiress_sec here
        serial = Serializer(os.getenv("SECRET_KEY"))
        try:
            user_id = serial.loads(token, max_age=expiress_sec)['user_id']  # Enforce expiration
        except:
            return None
        return User.query.get(user_id)

    # def check_password(self, password):
    #     return check_password_hash(self.password, password)

    def as_dict_user_token(self,token):

        dob = ""

        if self.dob is not None:
            dob = datetime.strptime(str(self.dob), "%Y-%m-%d").strftime("%d-%m-%Y")

        profile_pic = ""

        if self.profile_pic is not None:
            profile_pic = generate_presigned_url(self.profile_pic)
            # profile_pic = self.profile_pic_path

        return {

            'id': str(self.id),
            'firstname': self.firstname,
            'lastname': self.lastname,
            'dob': str(dob),
            'email': self.email,
            'country_code':self.country_code,
            'mobile_number': self.mobile_number,
            'profile_pic': profile_pic,
            'is_notification': self.is_notification,
            'device_token': self.device_token if self.device_token is not None else '',
            'device_type': self.device_type if self.device_type is not None else '',
            'token': token,
            'is_approved': self.is_approved,
            'is_otp': self.is_otp
        }

    def as_dict_user(self):

        dob = ""

        if self.dob is not None:
            dob = datetime.strptime(str(self.dob), "%Y-%m-%d").strftime("%d-%m-%Y")

        profile_pic = ""

        if self.profile_pic is not None:
            profile_pic = generate_presigned_url(self.profile_pic)
            # profile_pic = self.profile_pic_path
        return {

            'id': str(self.id),
            'firstname': self.firstname,
            'lastname': self.lastname,
            'dob': str(dob),
            'email': self.email,
            'country_code': self.country_code,
            'mobile_number': self.mobile_number,
            'profile_pic': profile_pic,
            'is_notification': self.is_notification,
            'device_token': self.device_token if self.device_token is not None else '',
            'device_type': self.device_type if self.device_type is not None else '',
            "is_block": self.is_block,
            'is_approved': self.is_approved,
            'is_otp': self.is_otp
        }

# This is user decorator to validate user with its jwt authorize token which is pass in api header
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None

        if "authorization" in request.headers:
            token = request.headers["authorization"]
        if not "authorization" in request.headers:
            return {'status': 0,'message': 'authorization is missing'}, 401

        if not token:
            return {"status": 0, "message": "a valid token is missing"}, 401
        try:
            data = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
            print('data', data)

            active_user = User.query.filter_by(id=data["id"]).first()

            if active_user is None:
                return {'status': 0, 'message': 'Invalid user'}, 401

            if active_user.is_block == True:
                return {'status': 0, 'message': 'You are block by admin'}, 401
            if active_user.is_deleted == True:
                return {'status': 0, 'message': 'Your account is deleted'}, 401

        except jwt.ExpiredSignatureError:
            return {"status": 0, "message": "Token has expired"}, 401
        except jwt.InvalidTokenError:
            return {"status": 0, "message": "Invalid token"}, 401
        except Exception as e:
            return {"status": 0, "message": f"An error occurred: {str(e)}"}, 401

        if not active_user:
            return {'status': 0, 'message': 'Invalid user'}, 401

        kwargs['active_user'] = active_user

        return f(*args, **kwargs)

    return decorator

# This model for the add image and comment on the delivery of users
class AddCommentDeliveryDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, nullable=False)
    comment = db.Column(db.String(550))
    lat = db.Column(db.String(50))
    long = db.Column(db.String(50))
    created_time = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'))
    # location_id = db.Column(db.Integer, db.ForeignKey('location_details.id', ondelete='CASCADE', onupdate='CASCADE'))

    def as_dict(self):
        input_date = datetime.strptime(str(self.created_time), "%Y-%m-%d %H:%M:%S")
        output_date = input_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        profile_pic = ""

        if self.delivery_comment_details.profile_pic is not None:
            profile_pic = generate_presigned_url(self.delivery_comment_details.profile_pic)

        get_images = ImageDeliveryDetails.query.filter_by(comment_id=self.id).all()

        get_images_list = [ i.as_dict() for i in get_images ]

        return {

            'id': self.id,
            'comment': self.comment if self.comment is not None else '',
            'lat': self.lat if self.lat is not None else '',
            'long': self.long if self.long is not None else '',
            'created_time': output_date,
            'user_id': self.user_id,
            'username': self.delivery_comment_details.firstname+ ' '+ self.delivery_comment_details.lastname,
            'user_image': profile_pic,
            'image_list': get_images_list

        }

# This model is saved multiple images data for getting list of images
class ImageDeliveryDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, nullable=False)
    image_name = db.Column(db.String(150))
    image_path = db.Column(db.String(150))
    created_time = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'))
    # location_id = db.Column(db.Integer, db.ForeignKey('location_details.id', ondelete='CASCADE', onupdate='CASCADE'))
    comment_id = db.Column(db.Integer, db.ForeignKey('add_comment_delivery_details.id', ondelete='CASCADE', onupdate='CASCADE'))

    def as_dict(self):
        return {

            'id': self.id,
            'image': generate_presigned_url(self.image_name)
        }