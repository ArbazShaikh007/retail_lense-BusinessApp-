import jwt,json
import os
import secrets
from datetime import datetime, timedelta, date
from flask import request, jsonify,make_response,render_template,redirect,url_for
from flask_restful import Resource
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from base.database.db import db
from dotenv import load_dotenv
from pathlib import Path
from base.common.utils import upload_photos_local,upload_photos,user_send_reset_email,delete_photos,delete_photos_local
from base.common.path import COMMON_URL
from base.apis.v1.user.models import User,token_required,AddCommentDeliveryDetails,ImageDeliveryDetails
from base.apis.v1.admin.models import LocationDetails,Cms

# env_path = Path('/var/www/html/backend/base/.env')
# load_dotenv(dotenv_path=env_path)

load_dotenv()
USER_FOLDER = 'base/static/images/'

class GetTermsResource(Resource):
    def get(self):
        try:
            get_terms = Cms.query.get(1)

            return jsonify({'status': 1,'message': 'Success','data': get_terms.as_dict()})

        except Exception as e:
            print('errorrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': 'Something went wrong'}, 500

class GetPrivacyResource(Resource):
    def get(self):
        try:
            get_privacy = Cms.query.get(2)

            return jsonify({'status': 1, 'message': 'Success', 'data': get_privacy.as_dict()})

        except Exception as e:
            print('errorrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': 'Something went wrong'}, 500

class UserDeleteAccountResource(Resource):
    @token_required
    def get(self, active_user):
        try:
            active_user.is_deleted = True
            db.session.commit()

            return jsonify({'status': 1,'message': 'Successfully account deleted'})

        except Exception as e:
            print('errorrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': 'Something went wrong'}, 500

class UserDeliveryDetailsListResource(Resource):
    @token_required
    def post(self, active_user):
        try:
            data = request.get_json()
            page = int(data.get('page', 1))
            per_page = 10

            today = date.today()

            get_deliverys = LocationDetails.query.filter(LocationDetails.user_id == active_user.id,LocationDetails.delivery_date == today ).order_by(LocationDetails.id.desc()).paginate(page=page,
                                                                                               per_page=per_page,
                                                                                               error_out=False)

            get_delivery_list = [i.as_dict() for i in get_deliverys.items]

            pagination_info = {
                "current_page": page,
                "has_next": get_deliverys.has_next,
                "per_page": per_page,
                "total_pages": get_deliverys.pages,
            }

            user_image = ''
            if active_user.profile_pic is not None:
                user_image = COMMON_URL+active_user.profile_pic_path+active_user.profile_pic

            return jsonify({'status': 1, 'message': 'Success', 'get_delivery_list': get_delivery_list,
                            'pagination_info': pagination_info,'username': active_user.firstname + ' '+ active_user.lastname,'user_image': user_image,'notification_count': '0'})

        except Exception as e:
            print('errorrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': 'Something went wrong'}, 500

class AddDetailsResource(Resource):
    @token_required
    def post(self, active_user):
        try:
            comment = request.form.get('comment')
            location_id = request.form.get('location_id')
            image = request.files.getlist('image')
            print('image',image)

            if not comment:
                return jsonify({'status': 0,'message': 'Please add comment'})
            if not image:
                return jsonify({'status': 0,'message': 'Please add images'})
            if not location_id:
                return jsonify({'status': 0,'message': 'Please select delivery details first'})

            get_location_details = LocationDetails.query.get(location_id)
            if not get_location_details:
                return jsonify({'status': 0,'message': 'Invalid delivery details'})
            check_existing = AddCommentDeliveryDetails.query.filter_by(user_id = active_user.id,location_id = location_id).first()
            if check_existing:
                return jsonify({'status': 0,'message': 'Already commented'})


            add_comment = AddCommentDeliveryDetails(comment=comment,user_id = active_user.id,location_id = location_id,created_time=datetime.utcnow())
            db.session.add(add_comment)
            db.session.commit()

            if image:
                if len(image)>0:
                    for i in image:
                        file_path, picture = upload_photos_local(i)
                        add_images = ImageDeliveryDetails(image_path = file_path,image_name = picture,created_time=datetime.utcnow(),location_id =location_id,user_id = active_user.id,comment_id=add_comment.id)
                        db.session.add(add_images)
                        db.session.commit()

            get_location_details.status = 'Completed'
            db.session.commit()

            return jsonify({'status': 1,'message': 'Successfully updated'})
        except Exception as e:
            print('errorrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': 'Something went wrong'}, 500