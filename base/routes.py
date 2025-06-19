from flask_restful import Api
from base.apis.v1.user.auth import UserRegisterResource,UserLoginResource,UserUpdateResource
from base.apis.v1.user.view import UserDeleteAccountResource,GetPrivacyResource,GetTermsResource,AddDetailsResource,UserDeliveryDetailsListResource
from base.apis.v1.admin.auth import SuccessPage,AdminResetPassword,AdminForgetPassword,RegisterResource,LoginResource,GetUserResource,ChangePasswordResource
from base.apis.v1.admin.view import GetDeletedUserListResource,GetBlockedUserListResource,DeleteUserResource,BlockUserResource,UserWiseDeliveryDetailsListResource,PrivacyPolicyResource,TermsConditionsResource,DashboardResource,DeliveryDetailsListResource,LocationDetailsResource,GetUserListResource,GetApprovedUserListResource,ApproveUserResource

api = Api()

admin_base = '/admin/'

api.add_resource(RegisterResource, admin_base+"register")
api.add_resource(LoginResource, admin_base+"login")
api.add_resource(GetUserResource, admin_base+"get_data")
api.add_resource(ChangePasswordResource, admin_base+"change_password")
api.add_resource(AdminForgetPassword,admin_base+"admin_forget_password")
api.add_resource(AdminResetPassword,admin_base+"admin_reset_password", endpoint="admin_reset_password")

admin_view = '/admin_view/'

api.add_resource(BlockUserResource, admin_view+"block_user")
api.add_resource(DeleteUserResource, admin_view+"delete_user")
api.add_resource(GetBlockedUserListResource, admin_view+"blocked_user_list")
api.add_resource(GetDeletedUserListResource, admin_view+"deleted_user_list")


api.add_resource(DashboardResource, admin_view+"dashboard")
api.add_resource(DeliveryDetailsListResource, admin_view+"get_delivery_list")
api.add_resource(UserWiseDeliveryDetailsListResource, admin_view+"get_user_delivery_list")
api.add_resource(LocationDetailsResource, admin_view+"location_details")
api.add_resource(GetUserListResource, admin_view+"user_list")
api.add_resource(GetApprovedUserListResource, admin_view+"approved_user_list")
api.add_resource(ApproveUserResource, admin_view+"approved_user")
api.add_resource(TermsConditionsResource, admin_view+"terms_conditions")
api.add_resource(PrivacyPolicyResource, admin_view+"privacy_policies")

user_base = '/user/'

api.add_resource(UserRegisterResource, user_base+"register")
api.add_resource(UserLoginResource, user_base+"login")
api.add_resource(UserUpdateResource, user_base+"update")

user_view = '/user_view/'

api.add_resource(UserDeliveryDetailsListResource, user_view+"user_delivery_list")
api.add_resource(AddDetailsResource, user_view+"add_delivery_comment")
api.add_resource(GetTermsResource, user_view+"get_terms")
api.add_resource(GetPrivacyResource, user_view+"get_privacy_policy")
api.add_resource(UserDeleteAccountResource, user_view+"delete_account")
api.add_resource(SuccessPage,user_view+"success_page", endpoint="success_page")