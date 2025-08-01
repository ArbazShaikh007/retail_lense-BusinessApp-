from flask import request, jsonify
from flask_restful import Resource
from base.common.utils import admin_login_required
from base.common.path import generate_presigned_url
from base.apis.v1.admin.models import Admin,Cms,UserChats
from base.database.db import db
from pathlib import Path
from base.apis.v1.user.models import User,AddCommentDeliveryDetails
from datetime import datetime
from dotenv import load_dotenv
from base.common.utils import push_notification
# env_path = Path('/var/www/html/backend/base/.env')
# load_dotenv(dotenv_path=env_path)
load_dotenv()

class UserChatsResource(Resource):
    @admin_login_required
    def post(self, active_user):
        try:
            data = request.get_json()

            title = data.get('title')
            description = data.get('description')
            user_id = data.get('user_id')

            if not title:
                return jsonify({'status': 'Title is required'})
            if not description:
                return jsonify({'status': 'Description is required'})
            if not user_id:
                return jsonify({'status': 'Please select users to send message'})

            add_chat = UserChats(title=title,description=description,user_ids=user_id,created_time=datetime.utcnow())
            db.session.add(add_chat)
            db.session.commit()

            split_user_ids = user_id.split(',')
            if len(split_user_ids)>0:
                for i in split_user_ids:
                    get_user = User.query.filter(User.device_token != None,User.device_type != None).first()
                    if get_user:

                        title = f'{title}'
                        msg = f'{description}'

                        push_notification(token=get_user.device_token, title=title, body=msg)

            return jsonify({'status': 1,'message': 'Message successfully sent to users'})

        except Exception as e:
            print('errorrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': 'Something went wrong'}, 500

    @admin_login_required
    def get(self, active_user):
        try:
            get_chats = UserChats.query.order_by(UserChats.id.desc()).all()

            get_chats_list = [ i.as_dict() for i in get_chats ]

            return jsonify({'status': 1,'message': 'Success','get_chats_list': get_chats_list})

        except Exception as e:
            print('errorrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': 'Something went wrong'}, 500

class GetDeletedUserListResource(Resource):
    @admin_login_required
    def post(self, active_user):
        try:
            data = request.get_json()
            page = int(data.get('page', 1))
            search_text = data.get('search_text')
            per_page = 10

            get_users = User.query.filter_by(is_deleted = True).order_by(User.id.desc()).paginate(page=page, per_page=per_page, error_out=False)

            user_list = [i.as_dict_user() for i in get_users.items]

            pagination_info = {
                "current_page": page,
                "has_next": get_users.has_next,
                "per_page": per_page,
                "total_pages": get_users.pages,
            }

            return jsonify({'status': 1,'message': 'Success','user_list': user_list,'pagination_info': pagination_info})

        except Exception as e:
            print('errorrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': 'Something went wrong'}, 500

class GetBlockedUserListResource(Resource):
    @admin_login_required
    def post(self, active_user):
        try:
            data = request.get_json()
            page = int(data.get('page', 1))
            search_text = data.get('search_text')
            per_page = 10

            get_users = User.query.filter_by(is_block = True).order_by(User.id.desc()).paginate(page=page, per_page=per_page, error_out=False)

            user_list = [i.as_dict_user() for i in get_users.items]

            pagination_info = {
                "current_page": page,
                "has_next": get_users.has_next,
                "per_page": per_page,
                "total_pages": get_users.pages,
            }

            return jsonify({'status': 1,'message': 'Success','user_list': user_list,'pagination_info': pagination_info})

        except Exception as e:
            print('errorrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': 'Something went wrong'}, 500

class DeleteUserResource(Resource):
    @admin_login_required
    def post(self, active_user):
        try:
            user_id = request.json.get('user_id')
            if not user_id:
                return jsonify({'status': 0,'message': 'Please select user first'})

            get_user = User.query.get(user_id)
            if not get_user:
                return jsonify({'status': 0,'message': 'Invalid user'})

            get_user.is_deleted = True
            db.session.commit()

            return jsonify({'status': 1,'message': 'User deleted successfully'})

        except Exception as e:
            print('errorrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': 'Something went wrong'}, 500

class BlockUserResource(Resource):
    @admin_login_required
    def post(self, active_user):
        try:
            user_id = request.json.get('user_id')
            if not user_id:
                return jsonify({'status': 0,'message': 'Please select user first'})

            get_user = User.query.get(user_id)
            if not get_user:
                return jsonify({'status': 0,'message': 'Invalid user'})

            get_user.is_block = True
            db.session.commit()

            return jsonify({'status': 1,'message': 'User blocked successfully'})

        except Exception as e:
            print('errorrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': 'Something went wrong'}, 500

class TermsConditionsResource(Resource):
    @admin_login_required
    def get(self, active_user):
        try:
            get_terms = Cms.query.get(1)
            return jsonify({'status': 1, 'data': get_terms.as_dict(), 'message': 'Success'})
        except Exception as e:
            print('errorrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': 'Something went wrong'}, 500

    @admin_login_required
    def post(self, active_user):
        try:
            content = request.json.get('content')

            get_terms = Cms.query.get(1)
            if not get_terms:
                return jsonify({'status': 0, 'messsage': 'Invalid data'})

            get_terms.content = content
            db.session.commit()

            return jsonify({'status': 1, 'data': get_terms.as_dict(), 'message': 'Success'})

        except Exception as e:
            print('errorrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': 'Something went wrong'}, 500

class PrivacyPolicyResource(Resource):
    @admin_login_required
    def get(self, active_user):
        try:
            get_privacy = Cms.query.get(2)

            return jsonify({'status': 1, 'data': get_privacy.as_dict(), 'message': 'Success'})

        except Exception as e:
            print('errorrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': 'Something went wrong'}, 500

    @admin_login_required
    def post(self, active_user):
        try:
            content = request.json.get('content')

            get_privacy = Cms.query.get(2)
            if not get_privacy:
                return jsonify({'status': 0,'messsage': 'Invalid data'})

            get_privacy.content=content
            db.session.commit()

            return jsonify({'status': 1, 'data': get_privacy.as_dict(), 'message': 'Success'})
        except Exception as e:
            print('errorrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': 'Something went wrong'}, 500

class DashboardResource(Resource):
    @admin_login_required
    def get(self, active_user):
        try:
            user_counts = User.query.filter_by(is_deleted = False,is_block = False).count()
            approved_user_counts = User.query.filter_by(is_deleted=False, is_block=False, is_approved=True).count()

            return jsonify({'status': 1,'message': 'Success','user_counts': user_counts,'approved_user_counts': approved_user_counts})
        except Exception as e:
            print('errorrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': 'Something went wrong'}, 500

class GetUserListNoPaginationResource(Resource):
    @admin_login_required
    def get(self, active_user):
        try:

            get_users = User.query.filter_by(is_deleted=False, is_block=False).order_by(
                User.id.desc()).all()

            user_list = []

            if len(get_users)>0:
                for i in get_users:
                    profile_pic = ""

                    if i.profile_pic is not None:
                        profile_pic = generate_presigned_url(i.profile_pic)

                    user_dict = {

                        'id': i.id,
                        'firstname': i.firstname,
                        'lastname': i.lastname,
                        'profile_pic': profile_pic
                    }

                    user_list.append(user_dict)

            return jsonify({'status': 1,'message': 'Success','user_list': user_list})

        except Exception as e:
            print('errorrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': 'Something went wrong'}, 500

class GetUserListResource(Resource):
    @admin_login_required
    def post(self, active_user):
        try:
            data = request.get_json()
            page = int(data.get('page', 1))
            search_text = data.get('search_text')
            per_page = 10

            # get_users = User.query.filter_by(is_deleted = False,is_block = False,is_approved = False).order_by(User.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
            get_users = User.query.filter_by(is_deleted=False, is_block=False).order_by(
                User.id.desc()).paginate(page=page, per_page=per_page, error_out=False)

            user_list = [i.as_dict_user() for i in get_users.items]

            pagination_info = {
                "current_page": page,
                "has_next": get_users.has_next,
                "per_page": per_page,
                "total_pages": get_users.pages,
            }

            return jsonify({'status': 1,'message': 'Success','user_list': user_list,'pagination_info': pagination_info})

        except Exception as e:
            print('errorrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': 'Something went wrong'}, 500

# class GetApprovedUserListResource(Resource):
#     @admin_login_required
#     def post(self, active_user):
#         try:
#             data = request.get_json()
#             page = int(data.get('page', 1))
#             search_text = data.get('search_text')
#             per_page = 10
#
#             get_users = User.query.filter_by(is_deleted=False, is_block=False, is_approved=True).order_by(
#                 User.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
#
#             user_list = [i.as_dict_user() for i in get_users.items]
#
#             pagination_info = {
#                 "current_page": page,
#                 "has_next": get_users.has_next,
#                 "per_page": per_page,
#                 "total_pages": get_users.pages,
#             }
#
#             return jsonify({'status': 1, 'message': 'Success', 'user_list': user_list, 'pagination_info': pagination_info})
#
#         except Exception as e:
#             print('errorrrrrrrrrrrrrrrrr:', str(e))
#             return {'status': 0, 'message': 'Something went wrong'}, 500

# class ApproveUserResource(Resource):
#     @admin_login_required
#     def post(self, active_user):
#         try:
#             data = request.get_json()
#             user_id = data.get('user_id')
#
#             if not user_id:
#                 return jsonify({'status': 0,'message': 'Please select user first'})
#
#             get_user = User.query.get(user_id)
#             if not get_user:
#                 return jsonify({'status': 0,'message': 'Invalid user'})
#
#             if get_user.is_approved==True:
#                 get_user.is_approved = False
#                 db.session.commit()
#
#                 return jsonify({'status': 1,'message': 'User disapproved successfully'})
#
#             elif get_user.is_approved == False:
#                 get_user.is_approved = True
#                 db.session.commit()
#
#                 return jsonify({'status': 1, 'message': 'User approved successfully'})
#
#             else:
#                 return jsonify({'status': 0, 'message': 'Something went wrong'})
#
#         except Exception as e:
#             print('errorrrrrrrrrrrrrrrrr:', str(e))
#             return {'status': 0, 'message': 'Something went wrong'}, 500

# class LocationDetailsResource(Resource):
#     @admin_login_required
#     def post(self, active_user):
#         try:
#
#             data = request.form
#
#             fullname = data.get('fullname')
#             start_time = data.get('start_time')
#             end_time = data.get('end_time')
#             location = data.get('location')
#             lat = data.get('lat')
#             long = data.get('long')
#             delivery_date = data.get('delivery_date')
#             user_id = data.get('user_id')
#
#             image = request.files.get('image')
#
#             if not fullname:
#                 return jsonify({'status': 0,'message': 'Name is required'})
#             if not start_time:
#                 return jsonify({'status': 0,'message': 'Time is required'})
#             if not end_time:
#                 return jsonify({'status': 0,'message': 'Time is required'})
#             if not location:
#                 return jsonify({'status': 0,'message': 'Location is required'})
#             if not lat:
#                 return jsonify({'status': 0,'message': 'Latitude is required'})
#             if not long:
#                 return jsonify({'status': 0,'message': 'Longitude is required'})
#             if not delivery_date:
#                 return jsonify({'status': 0,'message': 'Date is required'})
#             if not user_id:
#                 return jsonify({'status': 0,'message': 'Please select user first'})
#             if not image:
#                 return jsonify({'status': 0,'message': 'Image is required'})
#
#             get_user = User.query.filter_by(is_deleted = False,is_block = False,is_approved=True,id=user_id).first()
#             if not get_user:
#                 return jsonify({'status': 0,'message': 'Invalid user'})
#
#             image_name = None
#             image_path = None
#
#             if image:
#                 file_path, picture = upload_photos_local(image)
#                 image_name = picture
#                 image_path = file_path
#
#             date_obj = datetime.strptime(delivery_date, "%Y-%m-%d")
#             day_of_week = date_obj.strftime("%A")
#
#             add_location_details = LocationDetails(created_time=datetime.utcnow(),delivery_day=day_of_week,image_name=image_name,image_path=image_path,fullname=fullname,start_time=start_time,end_time=end_time
#                                                            ,location=location,lat=lat,long=long,delivery_date=delivery_date,user_id=get_user.id)
#
#             db.session.add(add_location_details)
#             db.session.commit()
#
#             return jsonify({'status': 1,'message': 'Successfully created location details'})
#
#         except Exception as e:
#             print('errorrrrrrrrrrrrrrrrr:', str(e))
#             return {'status': 0, 'message': 'Something went wrong'}, 500
#
#     @admin_login_required
#     def put(self, active_user):
#         try:
#             data = request.form
#
#             fullname = data.get('fullname')
#             start_time = data.get('start_time')
#             end_time = data.get('end_time')
#             location = data.get('location')
#             lat = data.get('lat')
#             long = data.get('long')
#             delivery_date = data.get('delivery_date')
#             user_id = data.get('user_id')
#             location_id = data.get('location_id')
#
#             image = request.files.get('image')
#             if not location_id:
#                 return jsonify({'status': 0, 'message': 'Please select delivery details first'})
#
#             get_delivery_details = LocationDetails.query.get(location_id)
#             if not get_delivery_details:
#                 return jsonify({'status': 0, 'message': 'Invalid delivery details first'})
#
#             if not fullname:
#                 return jsonify({'status': 0, 'message': 'Name is required'})
#             if not start_time:
#                 return jsonify({'status': 0, 'message': 'Time is required'})
#             if not end_time:
#                 return jsonify({'status': 0, 'message': 'Time is required'})
#             if not location:
#                 return jsonify({'status': 0, 'message': 'Location is required'})
#             if not lat:
#                 return jsonify({'status': 0, 'message': 'Latitude is required'})
#             if not long:
#                 return jsonify({'status': 0, 'message': 'Longitude is required'})
#             if not delivery_date:
#                 return jsonify({'status': 0, 'message': 'Date is required'})
#             if not user_id:
#                 return jsonify({'status': 0, 'message': 'Please select user first'})
#
#             if get_delivery_details.user_id != int(user_id):
#                 get_user = User.query.filter_by(is_deleted=False, is_block=False, is_approved=True, id=user_id).first()
#                 if not get_user:
#                     return jsonify({'status': 0, 'message': 'Invalid user'})
#
#             image_name = get_delivery_details.image_name
#             image_path = get_delivery_details.image_path
#
#             if image:
#                 delete_photos_local(get_delivery_details.image_name)
#                 file_path, picture = upload_photos_local(image)
#                 image_name = picture
#                 image_path = file_path
#
#             date_obj = datetime.strptime(delivery_date, "%Y-%m-%d")
#             day_of_week = date_obj.strftime("%A")
#
#             get_delivery_details.delivery_day=day_of_week
#             get_delivery_details.image_name=image_name
#             get_delivery_details.image_path=image_path
#             get_delivery_details.fullname=fullname
#             get_delivery_details.start_time=start_time
#             get_delivery_details.end_time=end_time
#             get_delivery_details.location=location
#             get_delivery_details.lat=lat
#             get_delivery_details.long=long
#             get_delivery_details.delivery_date=delivery_date
#             get_delivery_details.user_id = user_id
#
#             db.session.commit()
#
#             return jsonify({'status': 1, 'message': 'Successfully updated location details'})
#
#         except Exception as e:
#             print('errorrrrrrrrrrrrrrrrr:', str(e))
#             return {'status': 0, 'message': 'Something went wrong'}, 500
#
#     @admin_login_required
#     def delete(self, active_user):
#         try:
#             data = request.get_json()
#
#             location_id = data.get('location_id')
#
#             if not location_id:
#                 return jsonify({'status': 0, 'message': 'Please select delivery details first'})
#
#             get_delivery_details = LocationDetails.query.get(location_id)
#             if not get_delivery_details:
#                 return jsonify({'status': 0, 'message': 'Invalid delivery details'})
#
#             get_delivery_details.is_deleted = True
#             db.session.commit()
#
#             return jsonify({'status': 1,'message': 'Delivery details deleted successfully'})
#
#         except Exception as e:
#             print('errorrrrrrrrrrrrrrrrr:', str(e))
#             return {'status': 0, 'message': 'Something went wrong'}, 500
#
# class DeliveryDetailsListResource(Resource):
#     @admin_login_required
#     def post(self, active_user):
#         try:
#             data = request.get_json()
#             page = int(data.get('page', 1))
#             per_page = 10
#
#             get_deliverys = LocationDetails.query.filter(LocationDetails.is_deleted==False).order_by(LocationDetails.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
#
#             get_delivery_list = [ i.as_dict() for i in  get_deliverys.items ]
#
#             pagination_info = {
#                 "current_page": page,
#                 "has_next": get_deliverys.has_next,
#                 "per_page": per_page,
#                 "total_pages": get_deliverys.pages,
#             }
#
#             return jsonify({'status': 1,'message': 'Success','get_delivery_list': get_delivery_list,'pagination_info': pagination_info})
#
#         except Exception as e:
#             print('errorrrrrrrrrrrrrrrrr:', str(e))
#             return {'status': 0, 'message': 'Something went wrong'}, 500
#
# class UserWiseDeliveryDetailsListResource(Resource):
#     @admin_login_required
#     def post(self, active_user):
#         try:
#             data = request.get_json()
#             user_id = data.get('user_id')
#             page = int(data.get('page', 1))
#             per_page = 10
#
#             if not user_id:
#                 return jsonify({'status': 0,'message': 'Please select user first.'})
#
#             get_user = User.query.filter_by(is_approved = True,id = user_id).first()
#             if not get_user:
#                 return jsonify({'status': 0,'message': 'Invalid user.'})
#
#             get_deliverys = LocationDetails.query.filter(LocationDetails.is_deleted==False,LocationDetails.user_id == get_user.id).order_by(LocationDetails.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
#
#             get_delivery_list = [ i.as_dict() for i in  get_deliverys.items ]
#
#             pagination_info = {
#                 "current_page": page,
#                 "has_next": get_deliverys.has_next,
#                 "per_page": per_page,
#                 "total_pages": get_deliverys.pages,
#             }
#
#             return jsonify({'status': 1,'message': 'Success','get_delivery_list': get_delivery_list,'pagination_info': pagination_info})
#
#         except Exception as e:
#             print('errorrrrrrrrrrrrrrrrr:', str(e))
#             return {'status': 0, 'message': 'Something went wrong'}, 500

class DeliveryListResource(Resource):
    @admin_login_required
    def post(self, active_user):
        try:
            data = request.get_json()
            page = int(data.get('page', 1))
            per_page = 10

            get_delivery_data = AddCommentDeliveryDetails.query.order_by(AddCommentDeliveryDetails.id.desc()).paginate(page=page, per_page=per_page, error_out=False)

            get_delivery_list = [ i.as_dict() for i in get_delivery_data.items ]

            pagination_info = {
                            "current_page": page,
                            "has_next": get_delivery_data.has_next,
                            "per_page": per_page,
                            "total_pages": get_delivery_data.pages,
                        }

            return jsonify({'status': 1,'message': 'Success','get_delivery_list': get_delivery_list,'pagination_info': pagination_info})


        except Exception as e:
            print('errorrrrrrrrrrrrrrrrr:', str(e))
            return {'status': 0, 'message': 'Something went wrong'}, 500