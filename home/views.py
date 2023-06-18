from django.http import JsonResponse,HttpResponse,HttpResponseRedirect
from django.template import loader
from . import models
import hashlib
import json
from django.core.mail import send_mail
from django.conf import settings
from email_validator import validate_email
import uuid
import base64
from urllib.parse import unquote
import urllib
from .pages.home_page import HomePage



def cookie_valid(request):
    if 'AUTHSAVER' in request.COOKIES:
        auth_data_enc = request.COOKIES['AUTHSAVER']
        data_str = unquote(base64.urlsafe_b64decode(auth_data_enc))
        data = json.loads(data_str)
        username = data['username']
        password = data['password']
        users = models.User.objects.filter(username=username,password=password)
        if users.count() == 1:
            return True
    return False

def home(request):
    if cookie_valid(request):
        homePage = HomePage(request)
        homePage.main_page()
        time_sort = False
        if "sort" in request.GET:
            if request.GET['sort'] == "time":
                time_sort = True
        template = loader.get_template('HomePage.html')
        context = {
            "gas_stations" : homePage.gas_station_dict,
            "time_sort" : time_sort,
            "is_get_loc" : homePage.check_query()
        }
        return HttpResponse(template.render(context))
    return login(request)

def login(request):
    if 'AUTHENTICATION' in request.GET:
        data_enc = request.GET['AUTHENTICATION']
        data_str = unquote(base64.urlsafe_b64decode(data_enc))
        data = json.loads(data_str)
        print(data)
        username = data['username']
        password = data['password']
        password_encode = hashlib.sha256(bytes(password,'utf-8')).hexdigest()
        users = models.User.objects.filter(username=username,password=password_encode,active=True)
        if users.count() == 1:
            response = HttpResponseRedirect('/')
            user_json = {
                'username' : username,
                'password' : password_encode
            }
            user_str = json.dumps(user_json)
            response.set_cookie('AUTHSAVER',base64.b64encode(user_str.encode()).decode('utf-8'))
            return response
        context = {'status':False}
        template = loader.get_template("LoginPage.html")
        return HttpResponse(template.render(context))
    template = loader.get_template("LoginPage.html")
    context = {'status':True}
    return HttpResponse(template.render(context))

def register(request):
    context = {
        'username_valid' : True,
        'password_valid' : True,
        'repassword_valid' : True,
        'email_valid':True
    }
    if 'SIGNUP-DATA-ENCODE' in request.GET:
        data_encode = request.GET['SIGNUP-DATA-ENCODE']
        data_str = unquote(base64.urlsafe_b64decode(data_encode))
        data = json.loads(data_str)
        print(data)
        # Get Data
        username = data['username']
        password = data['password']
        re_password = data['repassword']
        email = data['email']
        firstname = data['name']
        lastname = data['lastname']


        # Valid The Data
        username_valid = True
        password_valid = True
        repassword_valid = True
        email_valid = True

        #Valid Check
        if username.find(' ') > -1 or models.User.objects.filter(username=username).count() > 0 or len(username) < 4:
            username_valid = False
        if len(password) < 8:
            password_valid = False
        if password != re_password:
            repassword_valid = False
        if models.User.objects.filter(email=email).count() > 0:
            email_valid = False
        try:
            validate_email(email)
        except:
            email_valid = False

        context = {
            'username_valid' : username_valid,
            'password_valid' : password_valid,
            'repassword_valid' : repassword_valid,
            'email_valid':email_valid
        }
        if username_valid == True and password_valid == True and repassword_valid == True and email_valid == True:
            auth_link = str(uuid.uuid4())
            New_user = models.User(
                username = username,
                password = hashlib.sha256(bytes(password,'utf-8')).hexdigest(),
                firstname = firstname,
                lastname = lastname,
                email = email,
                active = False,
                auth_link = auth_link,
                recovery_link = ''
            )
            New_user.save()
            send_mail("Authentication Link","Your Activate Account Link is "+"http://127.0.0.1:8000/activeated-account/?ACTIVECODE="+auth_link,settings.EMAIL_HOST_USER,[email])
            template = loader.get_template('VerficationLink.html')
            context = {
                'email' : email
            }
            return HttpResponse(template.render(context))
    template = loader.get_template('Register.html')
    return HttpResponse(template.render(context))
        
def active_account(request):
    query = request.GET
    Users = models.User.objects.filter(auth_link=query['ACTIVECODE'])
    active_valid = False
    if Users.count() > 0:
        user = Users[0]
        user.active = True
        user.auth_link = ''
        active_valid = True
        response = HttpResponseRedirect('/')
        user_json = {
            'username' : user.username,
            'password' : user.password
        }
        user_str = json.dumps(user_json)
        response.set_cookie('AUTHSAVER',base64.b64encode(user_str.encode()).decode('utf-8'))
        user.save()
        return response

def forget_password(request):
    if "DATARECOVERY" in request.GET:
        data_enc = request.GET['DATARECOVERY']
        data_str = unquote(base64.urlsafe_b64decode(data_enc))
        data = json.loads(data_str)
        username = data['username']
        users = models.User.objects.filter(username=username,active=True)
        if users.count() == 1:
            user = users[0]
            recovery_link = str(uuid.uuid4())
            user.recovery_link = recovery_link
            send_mail("Recovery Password Link","Your Recovery Account Link is "+"http://127.0.0.1:8000/change-password/?RECOVERYCODE="+recovery_link,settings.EMAIL_HOST_USER,[user.email])
            s = user.email
            email_format = s[0:len(s.split('@')[0])//3] + len(s[len(s.split('@')[0])//3:(len(s.split('@')[0])//3)*2])*"*" + s[(len(s.split('@')[0])//3)*2:len(s.split('@')[0])] + "@" + s.split("@")[1]
            context = {
                "status" : True,
                "valid" : True,
                "email" : email_format
            }
            user.save()
            template = loader.get_template('ForgetPassword.html')
            return HttpResponse(template.render(context))
        else:
            context = {
                "status" : False,
                "valid" : False,
                "email" : ''
            }
            template = loader.get_template('ForgetPassword.html')
            return HttpResponse(template.render(context))
    context = {
        "status" : True,
        "valid" : False,
        "email" : ''
    }
    template = loader.get_template('ForgetPassword.html')
    return HttpResponse(template.render(context))

def change_password(request):
    if "RECOVERYCODE" in request.GET:
        users = models.User.objects.filter(recovery_link=request.GET['RECOVERYCODE'])
        if users.count() == 0:
            template = loader.get_template('404.html')
            return HttpResponse(template.render())
        if "DATACHANGE" in request.GET:
            data_enc = request.GET['DATACHANGE']
            data_str = unquote(base64.urlsafe_b64decode(data_enc))
            data = json.loads(data_str)
            password = data['password']
            repassword = data['repassword']
            password_status = True
            repassword_status = True
            if len(password) < 8:
                password_status = False
            if repassword != password:
                repassword_status = False
            if password_status == True and repassword_status == True:
                user = users[0]
                user.password = hashlib.sha256(bytes(password,'utf-8')).hexdigest()
                user.recovery_link = ''
                user.save()
                return HttpResponseRedirect('/')
            else:
                context = {
                    'password_status' : password_status,
                    'repassword_status' : repassword_status
                }
                template = loader.get_template('RecoveryPassword.html')
                return HttpResponse(template.render(context))
        context = {
            'password_status' : True,
            'repassword_status' : True
        }
        template = loader.get_template('RecoveryPassword.html')
        return HttpResponse(template.render(context))
    else:
        template = loader.get_template('404.html')
        return HttpResponse(template.render())

def raw_body_convertor(body):
    return json.loads(body.decode('utf-8'))

def base64_encode_unicode(s):
    # First, we convert the string to bytes using UTF-8 encoding
    utf8_bytes = s.encode('utf-8')

    # Then, we URL-encode the bytes using urllib.parse.quote
    url_encoded_bytes = urllib.parse.quote(utf8_bytes)

    # Finally, we use base64 encoding to encode the URL-encoded bytes
    base64_encoded_bytes = base64.b64encode(url_encoded_bytes.encode('utf-8'))

    return base64_encoded_bytes.decode('utf-8')