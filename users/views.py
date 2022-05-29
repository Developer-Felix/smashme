from django.shortcuts import redirect, render
from config.sms import send_otp_to_validate_phone
from otp.models import Otps
from otp.views import random_number_generator

from users.models import Account

from django.contrib.auth import authenticate, login, logout
from django.urls import reverse

from django.contrib import messages
from django.contrib.auth.hashers import make_password

def index(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        print(phone)
        password = request.POST.get('password')
        print(password)

        if phone == '123' and password == '123':
            return redirect('/customer/home')
        else:
            phone == '321' and password == '321'
            return redirect('/engineer/home')

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
        country = request.POST.get('country')
        pin = request.POST.get('pin')

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
            return redirect('users:ptc-register')

    

        #     create a custom user with the phone number as the username and email backend as the password
        parent = Account(
            phone_number = phone,
            user_name = username,
            country = country,
            password=make_password(pin),
            email = phone + "@gmail.com"
        )
        parent.is_parent = True
        
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