from datetime import datetime
from distutils.ccompiler import gen_lib_options
from django.shortcuts import redirect, render
from pytz import utc
from config.sms import send_otp_to_validate_phone
from otp.models import Otps
from otp.views import random_number_generator

from users.models import Account

from django.contrib.auth import authenticate, login, logout
from django.urls import reverse

from django.contrib import messages
from django.contrib.auth.hashers import make_password

def index(request):
    username = password = ''

    if request.method == "POST":
        password = request.POST['password']
        phone_number = request.POST['phone']
        #if phone number starts with 07 remove the 0 and add +254
        if phone_number[0] == '0':
            phone_number = phone_number[1:]
            phone_number = '+254'+phone_number
        
        #if phone_number number does not start with + append + 
        elif phone_number[0] != '+':
            phone_number = '+'+phone_number

        # password = make_password('password')
        # print(password)
        user = authenticate(username=phone_number, password=password)
        # if user is not None:
        login(request,user)
        acc = Account.objects.all()

        if user.is_authenticated:
            return redirect('users:customer_home')

        # for acc in acc:
        #     print(acc.phone_number)
        #     if acc.phone_number == phone_number:
        #         print(acc.is_parent)
        #         if acc.is_parent == True:
        #             return redirect("users:customer-home")
        #         if acc.is_child == True:
        #             return redirect("users:engineer-home")

    return render(request, 'index.html')

def customer_home(request):
    engineer = Account.objects.filter(is_customer = True)
    data = {
        'engineer': engineer
    }
    return render(request, 'customer/home.html',data)

def chat(request):
    return render(request, 'customer/chat.html')

def engineer_home(request):
    return render(request, 'engineer/home.html')


def register(request):
    data = {}
    if request.method == "POST":
        username = request.POST.get('username')
        phone = request.POST.get('phone')
        age = request.POST.get('age')
        pin = request.POST.get('password')
        gender = request.POST.get('gender')
        wants = request.POST.get('wants')

        #if phone number starts with 07 remove the 0 and add +254
        if phone[0] == '0':
            phone = phone[1:]
            phone = '+254'+phone
        
        #if phone number does not start with + append + 
        elif phone[0] != '+':
            phone = '+'+phone

        #check if the phone number is already registered
        if Account.objects.filter(phone_number=phone).exists():
            print("phone number already registered")
            messages.info(request, f"Phone number already registered")
            return redirect('users:register')

    

        #     create a custom user with the phone number as the username and email backend as the password
        parent = Account(
            phone_number = phone,
            user_name = username,
            age = age,
            password=make_password(pin),
            email = phone + "@gmail.com",
            gender = gender,
            wants = wants,
        )
        parent.is_customer = True
        
        parent.save()
        messages.info(request, f"You are now registered as {username}")

        user = authenticate(request,username=phone,password=pin)
        login(request,parent)

        phonenumber = phone
        otp_number = random_number_generator(size=4)
        try:
            #Check number if it exist
            check_number_if_otp_exists = Otps.objects.filter(phone_number=phone)
        except:
            check_number_if_otp_exists = {}
            
        if bool(check_number_if_otp_exists) == False:
            otp = Otps(
                    phone_number = phone,
                    otp = otp_number
            )
            print(otp_number)
            send_otp_to_validate_phone(
                phone=phone,
                otp=otp_number
            )
            otp.save()
            print("OTP Saved Sucessfull")

                # add otp id to the user model to authenticate before login
            try:
                Account.objects.filter(phone_number=phone).update(
                        otp=Otps.objects.filter(otp=otp_number))
            except:
                print("none")

        elif bool(check_number_if_otp_exists) == True:
            new_otp = Otps.objects.filter(phone_number=phone).update(otp=otp_number)
            print(otp)
            print("OTP updated")
            send_otp_to_validate_phone(
                phone=phone,
                otp=otp_number
            )
            messages.info(request, f"OTP has been sent to your phone number")

        return redirect('otp/?phone='+phone)

    # except:
    #     return redirect('users:ptc-register')
    print("Done")

    return render(request,'customer/register.html',data)



def otp(request):
    if request.method == "POST":
        phone = request.GET.get('phone')
        otp = request.POST.get('otp')
        phone = str(phone)
        phone = phone[len(phone)-12:]
        print(phone)

        #Validate otp to authenticate the user
        validate_otp = Otps.objects.all()
        print("test1")
        for otps in validate_otp:
            print(otps.otp)
            db_phone = str(otps.phone_number)
            print(db_phone)
            new_db_phone = db_phone.replace('+', '')
            if  str(otp) == str(otps.otp) and str(phone)==new_db_phone:
                print("test3")
                if datetime.now().replace(tzinfo=utc) <= (otps.expire_at.replace(tzinfo=utc)):
                    print("test4")
                # update validation and mark the otp was successfully validated
                    Otps.objects.filter(otp=otp).update(is_otp_authenticated=True)

                    print("Authenticated")
                    return redirect('users:customer_home')
                else:
                    print("Fail")
                    

            else:
                print("fail2")
    return render(request,'customer/otp.html')
