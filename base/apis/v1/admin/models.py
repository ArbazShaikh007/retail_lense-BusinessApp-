from base.database.db import db
from base.common.path import generate_presigned_url
from itsdangerous import URLSafeTimedSerializer as Serializer
from base.apis.v1.user.models import User
import os

# This is admin model to store admin information
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(150), nullable=True)
    email = db.Column(db.String(150), nullable=True)
    profile_pic = db.Column(db.String(100))
    profile_pic_path = db.Column(db.String(200))
    password = db.Column(db.String(150), nullable=True)
    created_at = db.Column(db.DateTime)

    def as_dict(self,token):

        profile_pic = ''
        if self.profile_pic is not None:
            profile_pic = generate_presigned_url(self.profile_pic)

        return {
            'id': self.id,
            'fullname': self.fullname,
            'email': self.email,
            'image_url': profile_pic,
            'created_at': str(self.created_at),
            'token': token
        }

    def get_admin_token(self, expiress_sec=1800):
        serial = Serializer(os.getenv("ADMIN_SECRET_KEY"))
        return serial.dumps({'user_id': self.id})

    @staticmethod
    def verify_admin_token(token):
        serial = Serializer(os.getenv("ADMIN_SECRET_KEY"))
        try:
            user_id = serial.loads(token)['user_id']
        except:
            return None
        return Admin.query.get(user_id)

# class LocationDetails(db.Model):
#     id = db.Column(db.Integer, primary_key=True,
#                    autoincrement=True, nullable=False)
#     fullname = db.Column(db.String(150))
#     image_name = db.Column(db.String(100))
#     image_path = db.Column(db.String(200))
#     start_time = db.Column(db.String(150))
#     end_time = db.Column(db.String(150))
#     location = db.Column(db.String(350))
#     lat = db.Column(db.String(50))
#     long = db.Column(db.String(50))
#     delivery_date = db.Column(db.Date)
#     delivery_day = db.Column(db.String(50))
#     created_time = db.Column(db.DateTime)
#     is_deleted = db.Column(db.Boolean(), default=False)
#     status = db.Column(db.String(50), default="Pending")
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'))
#     user_comment_details = db.relationship('AddCommentDeliveryDetails', backref='user_comment_details')
#
#     def as_dict(self):
#
#         image = ''
#         if self.image_name is not None:
#             image = COMMON_URL + self.image_path + self.image_name
#
#         input_date = datetime.strptime(str(self.created_time), "%Y-%m-%d %H:%M:%S")
#         output_date = input_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
#
#         user_profile_pic = ""
#
#         if self.user_delivery_details.profile_pic is not None:
#             user_profile_pic = COMMON_URL + self.user_delivery_details.profile_pic_path + self.user_delivery_details.profile_pic
#
#         delivery_time = self.delivery_day + ' - '+ self.start_time+ ' Untill '+ self.end_time
#         comment = ''
#
#         image_list = []
#
#         if self.user_comment_details:
#             comment = self.user_comment_details[0].comment
#             print('self.user_comment_details',self.user_comment_details[0])
#
#             get_comment_images = ImageDeliveryDetails.query.filter_by(comment_id = self.user_comment_details[0].id).all()
#             if len(get_comment_images)>0:
#                 image_list = [ i.as_dict() for i in  get_comment_images]
#
#         return {
#
#             'id': self.id,
#             'fullname': self.fullname,
#             'image': image,
#             'start_time': self.start_time,
#             'end_time': self.end_time,
#             'delivery_time': delivery_time,
#             'location': self.location,
#             'lat': self.lat,
#             'long': self.long,
#             'delivery_date': str(self.delivery_date),
#             'created_time': output_date,
#             'is_deleted': self.is_deleted,
#             'status': self.status,
#             'delivery_day': self.delivery_day,
#             'user_id': self.user_id,
#             'username': self.user_delivery_details.firstname + ' ' + self.user_delivery_details.lastname,
#             'user_image': user_profile_pic,
#             'comment': comment,
#             'comment_images': image_list
#
#                     }

# This model for the saving cms page like terms and condition, privacy and policies etc
class Cms(db.Model):
    id = db.Column(db.Integer, primary_key=True,
                       autoincrement=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)

    content = db.Column(db.Text, nullable=False)

    def as_dict(self):
        return {
                'content': self.content if self.content is not None else ""
                    }

#This model for send message to user with title and description.
class UserChats(db.Model):
    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, nullable=False)
    title = db.Column(db.String(500),
                         nullable=False)
    description = db.Column(db.Text,
                         nullable=False)
    user_ids = db.Column(db.String(250),
                         nullable=False)
    created_time = db.Column(db.DateTime)

    def as_dict(self):

        user_list = []

        split_user_id = self.user_ids.split(',')

        for i in split_user_id:
            get_user = User.query.get(i)
            if get_user:

                profile_pic = ""

                if self.profile_pic is not None:
                    profile_pic = generate_presigned_url(get_user.profile_pic)

                user_dict = {

                    'user_id': get_user.id,
                    'firstname': get_user.firstname,
                    'lastname': get_user.lastname,
                    'profile_pic': profile_pic
                }

                user_list.append(user_dict)

        return {'id': self.id,
                'title': self.title,
                'description': self.description,
                'user_list': user_list
                }