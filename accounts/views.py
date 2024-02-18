from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.db.models import Q
from .models import Account
from .forms import RegistrationForm
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required

#library for account verification
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.html import strip_tags
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage, EmailMultiAlternatives

from carts.views import _get_cart
from carts.models import Cart, CartItem
import requests

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split("@")[0]

            user = Account.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.phone_number = phone_number
            user.save()

            #USER ACTIVATION
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })
            text_content = strip_tags(message)
            to_email = email
            #send_mail = EmailMessage(mail_subject, message, to=[to_email])
            send_mail = EmailMultiAlternatives(mail_subject, text_content, to=[to_email])
            send_mail.attach_alternative(message, 'text/html')
            send_mail.send()
            #messages.success(request, 'Thank yo for registering with us. Plaese verify your Account through activation link sent to your mail.')
            return redirect('/accounts/login/?command=verification&email='+email)

    else:
        form = RegistrationForm()

    context = {
        'form': form
    }
    return render(request, 'accounts/register.html', context)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                cart_current_user = _get_cart(request)
                cart_logged_user = Cart.objects.get(cart_id=user.email)
                is_current_user_cart_items_exist = CartItem.objects.filter(cart=cart_current_user).exists()
                if is_current_user_cart_items_exist:
                    current_user_cart_items = CartItem.objects.filter(cart=cart_current_user)
                    for item in current_user_cart_items:
                        is_cartItem_exists = CartItem.objects.filter(cart=cart_logged_user, product=item.product).exists()
                        if is_cartItem_exists:
                            ExistedItem = CartItem.objects.filter(cart=cart_logged_user, product=item.product)
                            VariationNotFound = True
                            for i in ExistedItem:
                                if set(i.variations.all()) == set(item.variations.all()):
                                    VariationNotFound = False
                                    i.quantity += item.quantity
                                    i.save()
                                    break
                            if VariationNotFound:
                                item.cart = cart_logged_user
                                item.save()
                        else:
                            item.cart = cart_logged_user
                            item.save()

                cart_current_user.delete()
            except Cart.DoesNotExist:
                try:
                    cart_current_user.cart_id = user.email
                    cart_current_user.save()
                except Exception as e:
                    # Handle the exception for saving cart_current_user
                    pass
            except Exception as e:
                # Handle other exceptions
                pass
            auth.login(request, user)
            #messages.success(request, 'Succesfully Logged In')
            try:
                url = request.META.get('HTTP_REFERER')
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    if params['next'] == "/cart/checkout/":
                        return redirect('cart')
                    else:
                        return redirect(params['next'])
            except:
                return redirect('home')
        else:
            messages.error(request, 'Invalid Login Credentials!')
            return redirect('login')
        
    return render(request, 'accounts/login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('login')

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulations! Your Account is activated.")
        return redirect('login')
    else:
        messages.error(request, "Invalid activation link")
        return redirect('register')

@login_required(login_url='login')   
def dashboard(request):
    return render(request, 'accounts/dashboard.html')

def forget_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email__exact=email).exists():
            user = Account.objects.get(email__exact=email)

            # Reset Password Email
            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })
            text_content = strip_tags(message)
            to_email = email
            #send_mail = EmailMessage(mail_subject, message, to=[to_email])
            send_mail = EmailMultiAlternatives(mail_subject, text_content, to=[to_email])
            send_mail.attach_alternative(message, 'text/html')
            send_mail.send()
            messages.success(request, 'Password reset email has been sent to your email.')
            return redirect('login')
        else:
            messages.error(request, "Account Doesn't Exists!")
            return redirect('forget_password')
    return render(request, 'accounts/forget_password.html')

def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, "Please reset your password.")
        return redirect('reset_password')
    else:
        messages.error(request, "This link has been expired!")
        return redirect('login')
    
def reset_password(request):
    if request.method == 'POST':
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        if new_password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(new_password)
            user.save()
            messages.success(request, "Your Accounty Password has been reset.")
            return redirect('login')
        else:
            messages.error(request, "Password and Confirm Password doesn't matched!")
            return redirect('reset_password')
    return render(request, 'accounts/reset_password.html')