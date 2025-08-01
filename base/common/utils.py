import firebase_admin, jwt
from firebase_admin import credentials, messaging
import secrets
from werkzeug.utils import secure_filename
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import url_for, jsonify, request
from base.apis.v1.admin.models import Admin
from functools import wraps
import boto3

from pathlib import Path
from dotenv import load_dotenv
# env_path = Path('/var/www/html/backend/base/.env')
# load_dotenv(dotenv_path=env_path)
load_dotenv()

REGION_NAME = os.getenv("REGION_NAME")
ACCESS_KEY = os.getenv("ACCESS_KEY")
SECRET_KEY = os.getenv("S3_SECRET_KEY")
S3_BUCKET = os.getenv("S3_BUCKET")

s3_client = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                         aws_secret_access_key=SECRET_KEY)

USER_FOLDER = 'base/static/images/'


# def send_otp(user, otp):
#     otp_value = str(otp)
#
#     print('Composing Email.......')
#
#     SERVER = 'smtp.gmail.com'  # smtp server
#     PORT = 587  # mail port number
#     # FROM = 'fearsfight211@gmail.com'  # sender Mail
#     FROM = 'Datoappsoporte@gmail.com'
#     TO = user.email  # receiver mail
#     # PASS = 'mdltifkjmclajper'
#     PASS = 'jucakyjhnjeivvuk'
#     MAIL_FROM_NAME = "Dato!"
#
#     msg = MIMEMultipart()
#     content = '''
# <!DOCTYPE html>
# <html>
# <head>
#   <meta charset="UTF-8">
#   <title>Verify Your Sign-Up</title>
# </head>
# <body style="margin: 0; padding: 0; background-color: #f5f5f5; font-family: Arial, sans-serif;">
#   <table align="center" width="100%" cellpadding="0" cellspacing="0" style="max-width: 500px; margin: 40px auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 0 10px rgba(0,0,0,0.08);">
#
#     <!-- Header -->
#     <tr>
#       <td align="center" style="background-color: #FF864A; padding: 30px;">
#         <!-- Optional logo -->
#         <!-- <img src="https://your-logo-url.com/logo.png" alt="Logo" style="width: 60px; height: auto; margin-bottom: 10px;"> -->
#         <h1 style="margin: 0; font-size: 24px; color: #ffffff;">Welcome to Dato</h1>
#       </td>
#     </tr>
#
#     <!-- Body -->
#     <tr>
#       <td style="padding: 30px; text-align: center;">
#         <p style="font-size: 20px; color: #333333; font-weight: bold; margin: 0 0 15px;">Verify Your Sign-Up</p>
#         <p style="font-size: 16px; color: #555555; margin: 0 0 25px;">
#           Enter the OTP below to verify your email and complete the sign-up process.
#         </p>
#         <div style="display: inline-block; padding: 14px 30px; font-size: 22px; font-weight: bold; background-color: #F4F4F4; color: #333333; border-radius: 8px; margin-bottom: 20px;">
#           '''+ otp_value +'''
#         </div>
#         <p style="font-size: 14px; color: #999999; margin-top: 30px;">
#           If you did not request this, you can ignore this email.
#         </p>
#       </td>
#     </tr>
#
#     <!-- Footer -->
#     <tr>
#       <td align="center" style="padding: 20px; font-size: 12px; color: #aaaaaa;">
#         ©2025 Dato. All rights reserved.
#       </td>
#     </tr>
#
#   </table>
# </body>
# </html>
#
#
#
#  '''
#
#     msg['Subject'] = 'Email Verification - Dato!'
#     msg['From'] = f'{MAIL_FROM_NAME} <{FROM}>'
#     msg['To'] = TO
#
#     msg.attach(MIMEText(content, 'html'))
#
#     print('Initiating server ...')
#
#     server = smtplib.SMTP(SERVER, PORT)
#     server.set_debuglevel(1)
#     server.ehlo()
#     server.starttls()
#     server.login(FROM, PASS)
#     server.sendmail(FROM, TO, msg.as_string().encode('utf-8'))
#     print('Email Sent...')
#     server.quit()

cred = credentials.Certificate('base/retaillense.json')
firebase_admin.initialize_app(cred)

def push_notification(token, title=None, body=None):
    try:

        sound = "default"

        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,

            ),

            android=messaging.AndroidConfig(
                notification=messaging.AndroidNotification(
                    sound=sound
                ),
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        sound=sound
                        # badge=0,
                        # # content_available=True,
                    )
                )
            ),

            token=token,

        )

        response = messaging.send(message)

        # Log the response
        print(f'Successfully sent message: {response}')

    except Exception as e:
        print('Error sending message:', e)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {
        "jpg",
        "jpeg",
        "png",
        "gif",
        "bmp",
        "tiff",
        "tif",
        "webp",
        "svg",
        "psd",
        "raw",
        "crw",
        "cr2",
        "cr3",
        "nef",
        "arw",
        "orf",
        "raf",
        "dng",
        "pef",
        "srf",
        "sr2",
        "rw2",
        "jfif"
    }

def static_upload_photos(file):
    try:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # extension = os.path.splitext(filename)[1]
            extension2 = os.path.splitext(filename)[1][1:].lower()
            content_type = f'image/{extension2}'
            x = secrets.token_hex(10)
            # picture = x + extension
            file.seek(0)
            s3_client.upload_fileobj(file, S3_BUCKET, filename,
                                     ExtraArgs={'ContentType': content_type})
            file_path = f"https://{S3_BUCKET}.s3.amazonaws.com/{filename}"

            return file_path, filename

    except Exception as e:
        print('errorrrrrrrrrrrrrrrrr:', str(e))
        return {'status': 0, 'message': 'Something went wrong'}, 500

def upload_photos(file):
    try:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            extension = os.path.splitext(filename)[1]
            extension2 = os.path.splitext(filename)[1][1:].lower()
            content_type = f'image/{extension2}'
            x = secrets.token_hex(10)
            picture = x + extension
            file.seek(0)
            s3_client.upload_fileobj(file, S3_BUCKET, picture,
                                     ExtraArgs={'ContentType': content_type})
            file_path = f"https://{S3_BUCKET}.s3.amazonaws.com/{picture}"

            return file_path, picture

    except Exception as e:
        print('errorrrrrrrrrrrrrrrrr:', str(e))
        return {'status': 0, 'message': 'Something went wrong'}, 500

def upload_photos_local(file):
    try:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            extension = os.path.splitext(filename)[1]

            x = secrets.token_hex(10)
            picture = x + extension

            image_path = os.path.join(USER_FOLDER)
            file.save(os.path.join(image_path, picture))
            file_path = image_path.replace("base", "")

            return file_path, picture

    except Exception as e:
        print('errorrrrrrrrrrrrrrrrr:', str(e))
        return {'status': 0, 'message': 'Something went wrong'}, 500

def delete_photos_local(file):
    try:
        os.remove(os.path.join(USER_FOLDER, file))
    except Exception as e:
        print('errorrrrrrrrrrrrrrrrr:', str(e))
        return {'status': 0, 'message': 'Something went wrong'}, 500

def delete_photos(file):
    try:
        s3_client.delete_object(Bucket=S3_BUCKET, Key=file)
    except Exception as e:
        print('errorrrrrrrrrrrrrrrrr:', str(e))
        return {'status': 0, 'message': 'Something went wrong'}, 500

# def user_invite_email(active_user,user_email):
#     try:
#
#         print('Composing Email.......')
#
#         SERVER = 'smtp.gmail.com'  # smtp server
#         PORT = 587  # mail port number
#         FROM = 'Datoappsoporte@gmail.com'  # sender Mail
#         TO = user_email  # receiver mail
#         PASS = 'jucakyjhnjeivvuk'
#         MAIL_FROM_NAME = "Dato"
#
#         msg = MIMEMultipart()
#         content = '''
#     <!DOCTYPE html>
# <html lang="en">
#   <head>
#     <meta charset="UTF-8" />
#     <meta name="viewport" content="width=device-width, initial-scale=1.0" />
#     <title>Email Template</title>
#     <style>
#       body {
#         font-family: 'Arial', sans-serif;
#         margin: 0;
#         padding: 0;
#         background-color: #ececec;
#         color: #333;
#       }
#
#       .email-container {
#         max-width: 600px;
#         margin: 20px auto;
#         background: #ffffff;
#         border-radius: 10px;
#         box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
#         overflow: hidden;
#         position: relative;
#       }
#
#       .email-header {
#         background: linear-gradient(45deg, #ff7f50, #ff6347);
#         color: white;
#         text-align: center;
#         padding: 30px 15px;
#       }
#
#       .email-header h1 {
#         font-size: 32px;
#         margin: 0;
#         letter-spacing: 1px;
#         text-transform: uppercase;
#       }
#
#       .email-body {
#         padding: 25px 20px;
#         background-color: #f9f9f9;
#         border-top: 5px solid #ff7f50;
#         text-align: center;
#       }
#
#       .email-body p {
#         font-size: 16px;
#         line-height: 1.6;
#         margin: 15px 0;
#         color: #333;
#       }
#
#       .download-links {
#         margin-top: 20px;
#       }
#
#       .download-links a {
#         display: inline-block;
#         margin: 10px;
#       }
#
#       .email-footer {
#         background-color: #f4f4f4;
#         padding: 15px;
#         text-align: center;
#         color: #777;
#         font-size: 14px;
#       }
#
#       .email-footer a {
#         color: #ff7f50;
#         text-decoration: none;
#         font-weight: bold;
#       }
#
#       .email-footer a:hover {
#         color: #ff6347;
#       }
#
#       a {
#         text-decoration: none;
#       }
#     </style>
#   </head>
#
#   <body>
#     <div class="email-container">
#       <div class="email-header">
#         <h1>Welcome to Dato!</h1>
#       </div>
#       <div class="email-body">
#         <p>
#           You have been invited to join Dato!
#         </p>
#         <p>''' + active_user.firstname + ''' ''' + active_user.lastname + ''' has invited you to our platform.
#           To get started, please register using your email address.</p>
#         <p>
#           Simply download the app from the links below and complete your registration using the same email address you received this invitation on.
#         </p>
#         <div class="download-links">
#           <a href="#">
#             <img src="https://dato-app-buck.s3.amazonaws.com/Google-Play-Icon.png" alt="Download on Google Play" width="150" />
#           </a>
#           <a href="#">
#             <img src="https://dato-app-buck.s3.amazonaws.com/App-Store-Icon.png" alt="Download on the App Store" width="150" />
#           </a>
#         </div>
#       </div>
#       <div class="email-footer">
#         <p>
#           Need help? <a href="#">Contact Support</a> |
#           <a href="#">Unsubscribe</a>
#         </p>
#         <p>&copy; 2025 Dato!. All rights reserved.</p>
#       </div>
#     </div>
#   </body>
# </html>
#
#      '''
#
#         msg['Subject'] = 'Invitation - Dato'
#         # msg['From'] = FROM
#         msg['From'] = f'{MAIL_FROM_NAME} <{FROM}>'
#         msg['To'] = TO
#
#         msg.attach(MIMEText(content, 'html'))
#
#         print('Initiating server ...')
#
#         server = smtplib.SMTP(SERVER, PORT)
#         server.set_debuglevel(1)
#         server.ehlo()
#         server.starttls()
#         server.login(FROM, PASS)
#         server.sendmail(FROM, TO, msg.as_string())
#         print('Email Sent...')
#         server.quit()
#
#     except Exception as e:
#         print('errorrrrrrrrrrrrrrrrr:', str(e))
#         return {'status': 0, 'message': 'Something went wrong'}, 500

def user_send_reset_email(user, type):
    try:
        token = ''
        url = '#'

        token = user.get_admin_token()

        print('Composing Email.......')

        SERVER = 'smtp.gmail.com'  # smtp server
        PORT = 587  # mail port number
        FROM = 'fearsfight211@gmail.com'  # sender Mail
        TO = user.email  # receiver mail
        PASS = 'mdltifkjmclajper'
        MAIL_FROM_NAME = "Buisnessapp"

        msg = MIMEMultipart()
        content = '''
    <!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Reset Password</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f4f4f4; font-family: 'Segoe UI', sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#f4f4f4">
    <tr>
      <td align="center" style="padding: 40px 20px;">
        <table width="600" cellpadding="0" cellspacing="0" border="0" style="background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
          
          <!-- Header -->
          <tr>
            <td align="center" style="background: linear-gradient(45deg, #5db1aa, #5db1aa); padding: 50px 20px;">
              <h1 style="margin: 0; color: #ffffff; font-size: 36px; font-weight: bold; letter-spacing: 1.5px;">BuisnessApp</h1>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding: 50px 30px; text-align: center;">
              <p style="font-size: 18px; color: #333333; margin-bottom: 24px;">
                Hi '''+user.fullname+''',
              </p>
              <p style="font-size: 16px; color: #555555; line-height: 1.6; margin-bottom: 30px;">
                We received a request to reset your password. If this was you, click the button below to reset it.
              </p>
              <a href="''' + url_for('admin_reset_password', token=token, _external=True) + '''" style="display: inline-block; background-color: #5db1aa; color: #ffffff; padding: 14px 28px; font-size: 16px; font-weight: bold; border-radius: 6px; text-decoration: none; box-shadow: 0 3px 6px rgba(0,0,0,0.15); margin-bottom: 30px;">
                Reset Password
              </a>
              <p style="font-size: 14px; color: #888888; line-height: 1.5; margin-top: 40px;">
                If you didn’t request this, you can safely ignore this email.
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding: 30px; background-color: #fafafa; text-align: center; color: #999999; font-size: 12px;">
              Need help? Contact our support team anytime.
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>


     '''

        msg['Subject'] = 'Reset Password - BuisnessApp'
        # msg['From'] = FROM
        msg['From'] = f'{MAIL_FROM_NAME} <{FROM}>'
        msg['To'] = TO

        msg.attach(MIMEText(content, 'html'))

        print('Initiating server ...')

        server = smtplib.SMTP(SERVER, PORT)
        server.set_debuglevel(1)
        server.ehlo()
        server.starttls()
        server.login(FROM, PASS)
        server.sendmail(FROM, TO, msg.as_string())
        print('Email Sent...')
        server.quit()

    except Exception as e:
        print('errorrrrrrrrrrrrrrrrr:', str(e))
        return {'status': 0, 'message': 'Something went wrong'}, 500

def admin_login_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if "authorization" in request.headers:
            token = request.headers["authorization"]
        if not token:
            return {"status": 0, "message": "a valid token is missing"}
        try:
            data = jwt.decode(token, os.getenv("ADMIN_SECRET_KEY"), algorithms=["HS256"])
            active_user = Admin.query.filter_by(id=data["id"]).first()
        except jwt.ExpiredSignatureError:
            return {"status": 0, "message": "Token has expired"}, 401
        except jwt.InvalidTokenError:
            return {"status": 0, "message": "Invalid token"}, 401
        except Exception as e:
            return {"status": 0, "message": f"An error occurred: {str(e)}"}

        kwargs['active_user'] = active_user

        return f(*args, **kwargs)

    return decorator

    # def send_admin_reset_email(admin):
    #     token = admin.get_admin_token()
    #
    #     print('Composing Email.......')
    #
    #     SERVER = 'mail.app.fight-fears.com'
    #     PORT = 465  # SSL port for SMTP
    #     FROM = 'no-reply@app.fight-fears.com'
    #     TO = admin.email
    #     PASS = 'FightFears.App.@@2024'
    #
    #     msg = MIMEMultipart()
    #     content = '''
    # <!DOCTYPE html>
    # <html>
    #
    # <head>
    #     <title>Reset Password</title>
    #     <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    #     <meta name="viewport" content="width=device-width, initial-scale=1">
    #     <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    #     <style type="text/css">
    #         @media screen {
    #             @font-face {
    #                 font-family: 'Lato';
    #                 font-style: normal;
    #                 font-weight: 400;
    #                 src: local('Lato Regular'), local('Lato-Regular'), url(https://fonts.gstatic.com/s/lato/v11/qIIYRU-oROkIk8vfvxw6QvesZW2xOQ-xsNqO47m55DA.woff) format('woff');
    #             }
    #
    #             @font-face {
    #                 font-family: 'Lato';
    #                 font-style: normal;
    #                 font-weight: 700;
    #                 src: local('Lato Bold'), local('Lato-Bold'), url(https://fonts.gstatic.com/s/lato/v11/qdgUG4U09HnJwhYI-uK18wLUuEpTyoUstqEm5AMlJo4.woff) format('woff');
    #             }
    #
    #             @font-face {
    #                 font-family: 'Lato';
    #                 font-style: italic;
    #                 font-weight: 400;
    #                 src: local('Lato Italic'), local('Lato-Italic'), url(https://fonts.gstatic.com/s/lato/v11/RYyZNoeFgb0l7W3Vu1aSWOvvDin1pK8aKteLpeZ5c0A.woff) format('woff');
    #             }
    #
    #             @font-face {
    #                 font-family: 'Lato';
    #                 font-style: italic;
    #                 font-weight: 700;
    #                 src: local('Lato Bold Italic'), local('Lato-BoldItalic'), url(https://fonts.gstatic.com/s/lato/v11/HkF_qI1x_noxlxhrhMQYELO3LdcAZYWl9Si6vvxL-qU.woff) format('woff');
    #             }
    #         }
    #
    #         /* CLIENT-SPECIFIC STYLES */
    #         body,
    #         table,
    #         td,
    #         a {
    #             -webkit-text-size-adjust: 100%;
    #             -ms-text-size-adjust: 100%;
    #         }
    #
    #         table,
    #         td {
    #             mso-table-lspace: 0pt;
    #             mso-table-rspace: 0pt;
    #         }
    #
    #         img {
    #             -ms-interpolation-mode: bicubic;
    #         }
    #
    #         /* RESET STYLES */
    #         img {
    #             border: 0;
    #             height: auto;
    #             line-height: 100%;
    #             outline: none;
    #             text-decoration: none;
    #         }
    #
    #         table {
    #             border-collapse: collapse !important;
    #         }
    #
    #         body {
    #             height: 100% !important;
    #             margin: 0 !important;
    #             padding: 0 !important;
    #             width: 100% !important;
    #             background-color: black;
    #         }
    #
    #         a[x-apple-data-detectors] {
    #             color: inherit !important;
    #             text-decoration: none !important;
    #             font-size: inherit !important;
    #             font-family: inherit !important;
    #             font-weight: inherit !important;
    #             line-height: inherit !important;
    #         }
    #
    #         /* Responsive Styles */
    #         @media screen and (max-width: 600px) {
    #             h1 {
    #                 font-size: 32px !important;
    #                 line-height: 32px !important;
    #             }
    #         }
    #
    #         /* Custom Styles */
    #         h1,
    #         p {
    #             color: #ffffff;
    #             font-family: 'Lato', Helvetica, Arial, sans-serif;
    #         }
    #
    #         h1 {
    #             font-size: 28px;
    #             font-weight: 300;
    #             margin: 25px 0 0;
    #         }
    #
    #         p {
    #             font-size: 18px;
    #             font-weight: 400;
    #             line-height: 25px;
    #             margin: 0;
    #         }
    #
    #         .email-container {
    #             background-color: black;
    #             border-radius: 10px;
    #             box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.15);
    #             max-width: 600px;
    #             margin: 0 auto;
    #             padding: 50px 30px;
    #             margin-top: 75px;
    #         }
    #
    #         .header {
    #             background-color: black;
    #             padding: 20px;
    #             border-radius: 4px 4px 0 0;
    #             text-align: center;
    #         }
    #
    #         .button {
    #             display: inline-block;
    #             padding: 15px 25px;
    #             font-size: 20px;
    #             color: white !important;
    #             background-color: #646d77;
    #             text-decoration: none;
    #             border-radius: 6px;
    #             font-family: 'Lato', Helvetica, Arial, sans-serif;
    #             font-weight: bold;
    #             box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
    #         }
    #
    #         .footer {
    #             padding: 20px 0;
    #             text-align: center;
    #             font-size: 14px;
    #             color: #aaaaaa;
    #         }
    #     </style>
    # </head>
    #
    # <body>
    #     <table border="0" cellpadding="0" cellspacing="0" width="100%">
    #         <!-- HIDDEN PREHEADER TEXT -->
    #         <div style="display: none; font-size: 1px; color: #fefefe; line-height: 1px; font-family: 'Lato', Helvetica, Arial, sans-serif; max-height: 0px; max-width: 0px; opacity: 0; overflow: hidden;">
    #             We're thrilled to have you here! Get ready to dive into your new account.
    #         </div>
    #         <!-- LOGO -->
    #         <tr>
    #             <td align="center">
    #                 <div class="email-container">
    #                     <div class="header">
    #                         <img src="https://first-face.s3.amazonaws.com/89e884021a321b83698b.png" width="240" height="150" style=" border: 0; margin-inline: auto " alt="Logo">
    #
    #                     </div>
    #                     <h1>Trouble signing in?</h1>
    #                     <div style="padding: 20px 30px;">
    #                         <p>Resetting your password is easy. Just press the button below and follow the instructions. We'll have you up and running in no time.</p>
    #                     </div>
    #                     <div style="text-align: center; padding: 20px 0;">
    #                         <a href="''' + url_for('admin_reset_password', token=token, _external=True) + '''" class="button">Reset Password</a>
    #                     </div>
    #                 </div>
    #             </td>
    #         </tr>
    #         <tr>
    #             <td align="center">
    #                 <div class="footer">
    #                     © 2024 FirstFace. All rights reserved.
    #                 </div>
    #             </td>
    #         </tr>
    #     </table>
    # </body>
    #
    # </html>
    #
    #
    #
    #  '''
    #
    #     msg['Subject'] = 'Reset Password - First Face'
    #     msg['From'] = FROM
    #     msg['To'] = TO
    #
    #     msg.attach(MIMEText(content, 'html'))
    #
    #     print('Initiating server ...')
    #
    #     try:
    #         server = smtplib.SMTP_SSL(SERVER, PORT)
    #         server.set_debuglevel(1)
    #         server.login(FROM, PASS)
    #         server.sendmail(FROM, TO, msg.as_string())
    #         print('Email Sent...')
    #     except smtplib.SMTPServerDisconnected as e:
    #         print(f"Server disconnected unexpectedly: {e}")
    #
    #     # server = smtplib.SMTP(SERVER, PORT)
    #     # server.set_debuglevel(1)
    #     # server.ehlo()
    #     # server.starttls()
    #     # server.login(FROM, PASS)
    #     # server.sendmail(FROM, TO, msg.as_string())
    #     print('Email Sent...')
    #     server.quit()

# <!DOCTYPE html>
# <html lang="en">
#   <head>
#     <meta charset="UTF-8" />
#     <meta name="viewport" content="width=device-width, initial-scale=1.0" />
#     <title>Email Template</title>
#     <style>
#       body {
#         font-family: 'Arial', sans-serif;
#         margin: 0;
#         padding: 0;
#         background-color: #ececec;
#         color: #333;
#       }
#
#       .email-container {
#         max-width: 600px;
#         margin: 20px auto;
#         background: #ffffff;
#         border-radius: 10px;
#         box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
#         overflow: hidden;
#         position: relative;
#       }
#
#       .email-header {
#         background: linear-gradient(45deg, #ff7f50, #ff6347);
#         color: white;
#         text-align: center;
#         padding: 30px 15px;
#       }
#
#       .email-header h1 {
#         font-size: 32px;
#         margin: 0;
#         letter-spacing: 1px;
#         text-transform: uppercase;
#       }
#
#       .email-body {
#         padding: 25px 20px;
#         background-color: #f9f9f9;
#         border-top: 5px solid #ff7f50;
#         text-align: center;
#       }
#
#       .email-body p {
#         font-size: 16px;
#         line-height: 1.6;
#         margin: 15px 0;
#         color: #333;
#       }
#
#       .cta-button {
#         display: inline-block;
#         padding: 12px 25px;
#         font-size: 18px;
#         font-weight: bold;
#         color: white;
#         text-decoration: none;
#         background: linear-gradient(45deg, #ff7f50, #ff6347);
#         border-radius: 50px;
#         text-align: center;
#         margin-top: 20px;
#         box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
#         transition: all 0.3s ease;
#       }
#
#       # .cta-button:hover {
#       #   transform: translateY(-4px);
#       #   box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
#       # }
#
#       .email-footer {
#         background-color: #f4f4f4;
#         padding: 15px;
#         text-align: center;
#         color: #777;
#         font-size: 14px;
#       }
#
#       .email-footer a {
#         color: #ff7f50;
#         text-decoration: none;
#         font-weight: bold;
#       }
#
#       .email-footer a:hover {
#         color: #ff6347;
#       }
#
#       a {
#       color: #ff7f50;
#     text-decoration: none;
#       }
#     </style>
#   </head>
#
#   <body>
#     <div class="email-container">
#       <div class="email-header">
#         <h1>Welcome to Dato</h1>
#       </div>
#       <div class="email-body">
#         <p>
#           Thank you for joining [Your Company Name]! We are excited to have you
#           with us. Explore our services and discover all the ways we can help
#           you achieve your goals. Start your journey today!
#         </p>
#         <p>
#           If you need assistance, don't hesitate to reach out to our support
#           team. We're here to help.
#         </p>
#         <div>
#           <a href="#" class="cta-button">Get Started</a>
#         </div>
#       </div>
#       <div class="email-footer">
#         <p>
#           Need help? <a href="#">Contact Support</a> |
#           <a href="#">Unsubscribe</a>
#         </p>
#         <p>&copy; 2025 [Your Company Name]. All rights reserved.</p>
#       </div>
#     </div>
#   </body>
# </html>