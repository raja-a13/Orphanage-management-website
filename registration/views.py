from django.shortcuts import render, redirect, reverse

from homepage.models import Orphanage, Type, UserDetails,Transport,donatevaluables
from registration.form import RegisterForm, CustomAuthForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from .tokens import account_activation_token
from django.core.mail import EmailMessage


# Create your views here.
def index(request):
    return render(request, 'registration/../../templates/userdashboard/userdashboard.html')


def index1(request):
    return render(request, 'registration/donate-history.html')


def index2(request):
    return render(request, 'registration/join-orphan.html')


def index3(request):
    return render(request, 'registration/near-you.html')


def index4(request):
    return render(request, 'registration/pending.html')


# Just initializing it, as per the login.html page
register_user_type = 'user'


def get_data(request, user_type):
    global register_user_type
    register_user_type = user_type
    print(register_user_type)
    return None


def signup(request):
    signup_type = register_user_type
    if request.method == "POST":
        if signup_type == 'user':
            new_user_form = RegisterForm(request.POST)
            if new_user_form.is_valid():
                new_user = User.objects.create_user(
                    username=new_user_form.cleaned_data["username"],
                    password=new_user_form.cleaned_data["password"],
                    email=new_user_form.cleaned_data["email"]
                )

                new_user.first_name = new_user_form.cleaned_data["first_name"]
                new_user.last_name = new_user_form.cleaned_data["last_name"]
                new_user.is_active = False
                new_user.save()
                user_details = UserDetails.objects.create(
                    user_id=new_user,
                    date_of_birth=request.POST["DOB"],
                    gender=request.POST["gender"],
                    phone_no=request.POST["phone_number"]
                )
                user_type = Type.objects.create(
                    user=new_user,
                    ref_no=1
                )
                new_user.save()
                user_details.save()
                user_type.save()
                print("Form is valid")

                current_site = get_current_site(request)
                mail_subject = 'Activate your OMS user account.'
                message = render_to_string('registration/acc_active_email.html', {
                    'user': new_user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(new_user.pk)),
                    'token': account_activation_token.make_token(new_user),
                })
                to_email = new_user_form.cleaned_data.get('email')
                email = EmailMessage(
                    mail_subject, message, to=[to_email]
                )
                email.send()
                return HttpResponse(
                    '<h1>New user created successfully</h1><br>Please confirm your email address to complete the registration')

            else:
                print("User signup form Invalid")
                return render(request, 'registration/signup_page.html',
                              {"signup_form": new_user_form, 'signup_type': signup_type})
        elif signup_type == 'orphanage':
            new_user_form = RegisterForm(request.POST)
            if new_user_form.is_valid():
                new_user = User.objects.create_user(
                    username=new_user_form.cleaned_data["username"],
                    password=new_user_form.cleaned_data["password"],
                    email=new_user_form.cleaned_data["email"]
                )
                print(request.POST["current_latitude"])
                print(request.POST["current_longitude"])
                new_user.save()
                new_orphanage_user = Orphanage.objects.create(
                    orphanage_id=User.objects.get(username=new_user_form.cleaned_data["username"]),
                    orphanage_name=request.POST["orphanage_name"],
                    year_of_establishment=request.POST["year_of_establishment"],
                    address=request.POST["address"],
                    phone_no=request.POST["phone_number"],
                    description=request.POST["description"],
                    image=request.FILES.get("orphanage_image"),
                    lat=float(request.POST["current_latitude"]),
                    lon=float(request.POST["current_longitude"]),
                )

                user_type = Type.objects.create(
                    user=new_user,
                    ref_no=2
                )
                new_user.is_active = False

                new_user.save()
                new_orphanage_user.save()
                user_type.save()

                current_site = get_current_site(request)
                mail_subject = 'Activate your OMS user account.'
                message = render_to_string('registration/acc_active_email.html', {
                    'user': new_user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(new_user.pk)),
                    'token': account_activation_token.make_token(new_user),
                })
                to_email = new_user_form.cleaned_data.get('email')
                email = EmailMessage(
                    mail_subject, message, to=[to_email]
                )
                email.send()
                return HttpResponse(
                    '<h1>New orphanage user created successfully</h1><br>'
                    'Please confirm your email address to complete the registration')
                # return HttpResponse("<h1>New orphanage user created successfully</h1>")
            else:
                print("Orphanage signup form Invalid")
                return render(request, 'registration/signup_page.html',
                              {"signup_form": new_user_form, 'signup_type': signup_type})
        else:
            new_form = RegisterForm()
            print("Signup type not available now.")
            return render(request, 'registration/signup_page.html',
                          {"signup_form": new_form, 'signup_type': signup_type})
    else:
        new_form = RegisterForm()
        print("Invalid request")
        return render(request, 'registration/signup_page.html', {"signup_form": new_form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('home')
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')


# def user_signup(request):
#     if request.method == "POST":
#         new_user_form = RegisterForm(request.POST)
#         if new_user_form.is_valid():
#             new_user = User.objects.create_user(
#                 username=new_user_form.cleaned_data["username"],
#                 password=new_user_form.cleaned_data["password"],
#                 email=new_user_form.cleaned_data["email"]
#             )
#
#             new_user.first_name = new_user_form.cleaned_data["first_name"]
#             new_user.last_name = new_user_form.cleaned_data["last_name"]
#
#             user_details = UserDetails.objects.create(
#                 user_id=new_user,
#                 date_of_birth=request.POST["DOB"],
#                 gender=request.POST["gender"],
#                 phone_no=request.POST["phone_number"]
#             )
#             user_type = Type.objects.create(
#                 user=new_user,
#                 ref_no=1
#             )
#             new_user.save()
#             user_details.save()
#             user_type.save()
#             print("Form is valid")
#             return HttpResponse("<h1>New user created successfully</h1>")
#         else:
#             print("Form Invalid")
#             return render(request, 'registration/signup_page.html', {"signup_form": new_user_form})
#     else:
#         new_form = RegisterForm()
#         print("Invalid request")
#         return render(request, 'registration/signup_page.html', {"signup_form": new_form})


# def loginstatus(request):
#     return render(request, 'registration/login_success.html')
#
#
def login_view(request):
    if request.method == "POST":
        form = CustomAuthForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        print("User is " + request.user.username)
        print(user, username, password)
        if user is not None:
            login(request, user)
            type = Type.objects.get(user=user)
            if type.ref_no == 1:
                return redirect('userdashboard:u_Profile')
            elif type.ref_no == 2:
                return HttpResponse("<h1>Please wait to get into the dashboard, until your orphanage gets verified</h1>")
            elif type.ref_no == 3:
                return redirect('orphanageadmin:o_profile')
            else:
                return HttpResponse("Not a regular user")
        else:
            error_message = "Please enter a correct username and password. Note that both fields may be case-sensitive."
            return render(request, 'registration/login.html', {'form': form, 'error': error_message})
    else:
        new_form = CustomAuthForm()
        return render(request, 'registration/login.html', {'form': new_form})




# def login12_django_form(request):
#     if request.method == "POST":


# def user_signup1(request):
#     return render(request, 'registration/user_signup.html')
#
#
# def user_signup12(request):
#     if request.method == "POST":
#         new_user = User.objects.create_user(
#             username=request.POST["username"],
#             password=request.POST["password"],
#             email=request.POST["email"],
#         )
#         user_details = UserDetails.objects.create(
#             user_id=new_user,
#             date_of_birth=request.POST["DOB"],
#             gender=request.POST["gender"],
#             phone_no=request.POST["phone_number"]
#         )
#
#         user_type = Type.objects.create(
#             user=new_user,
#             ref_no=1
#         )
#         new_user.save()
#         user_details.save()
#         user_type.save()
#         return HttpResponse("<h1>New user created successfully</h1>")
#
#
# def orphanage_signup1(request):
#     return render(request, 'registration/orphanage_signup.html')

#
# def orphanage_signup(request):
#     print(request)
#     type(request)
#     if request.method == "POST":
#         new_user_form = RegisterForm(request.POST)
#         if new_user_form.is_valid():
#             new_user = User.objects.create_user(
#                 username=new_user_form.cleaned_data["username"],
#                 password=new_user_form.cleaned_data["password"],
#                 email=new_user_form.cleaned_data["email"]
#             )
#             new_orphanage_user = Orphanage.objects.create(
#                 orphanage_name=request.POST["orphanage_name"],
#                 year_of_establishment=request.POST["year_of_establishment"],
#                 address=request.POST["address"],
#                 phone_no=request.POST["phone_number"],
#                 description=request.POST["description"],
#                 image=request.FILES.get("orphanage_image"),
#                 lat=request.POST["current_latitude"],
#                 lon=request.POST["current_longitude"]
#             )
#
#             user_type = Type.objects.create(
#                 user=new_user,
#                 ref_no=2
#             )
#             new_user.save()
#             new_orphanage_user.save()
#             user_type.save()
#             return HttpResponse("<h1>New orphanage user created successfully</h1>")
#         else:
#             print("Form Invalid")
#             return render(request, 'registration/orphanage_signup.html', {"signup_form": new_user_form})
#     else:
#         new_form = RegisterForm()
#         print("Invalid request")
#         return render(request, 'registration/orphanage_signup.html', {"signup_form": new_form})
#
#
# def signup1(request):
#     return render(request, 'registration/signup_page.html')



def logout_view(request):
    logout(request)
    return redirect('h_index')

def solution(request):
    user = request.user
    #print(user)
    id=request.POST['name']
    print(id,'###')
    data=Transport.objects.filter(danation_id=id)
    for each in data:
        h=each.danation_id
        l=donatevaluables.objects.get(pk=h)
        #print(l.user_id,User.objects.get(username=user))
        if l.user_id==User.objects.get(username=user)  : #0 means not delivered
            print(l.pk)
            data1=Transport.objects.filter(danation_id=l.pk)
            print(data1)
            break;
    return render(request,'registration/accep.html',{"data1":data1})

def result(request):
    if request.method == "POST":
        id=request.POST['name']
        print(id,'123')
        data=Transport.objects.get(danation_id=id)
        k=data.danation_id
        h=Transport.objects.filter(danation_id=k)
        #print(data.company_name)
        
        data.status='1' #1 means Accepted
        data.save()
        l=donatevaluables.objects.get(pk=data.danation_id)
        l.status=1 #1 means Accepted
        l.save()
        for each in h:
            if str(each.danation_id) !=str(id):
                print(each.danation_id,id)
                each.status='2'
                each.save() #2 means Rejected
        return redirect('donation:accepted')