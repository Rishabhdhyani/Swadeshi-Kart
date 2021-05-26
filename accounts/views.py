from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import Account, UserProfile
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
# Create your views here.

# Verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from carts.views import _cart_id
from carts.models import Cart, CartItem
from orders.models import Order, Payment, OrderProduct
import requests

def register(request):
    if request.method=="POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.save()

            #User profile
            profile = UserProfile()
            profile.user_id = user.id
            profile.profile_picture = 'default/user.png'
            profile.save()

            # USER ACTIVATION
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            #messages.success(request, 'Registration Successfull!')
            return redirect('/accounts/login/?command=verification&email='+email)

    else:
        form = RegistrationForm()
    context={
          'form':form,
    }
    return render(request,'accounts/register.html',context)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    # Getting the product variations by cart id
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    # Get the cart items from the user to access his product variations
                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)

                    # product_variation = [1, 2, 3, 4, 6]
                    # ex_var_list = [4, 6, 3, 5]

                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()

            except:
                pass
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            url = request.META.get('HTTP_REFERER')
            string = str(url).split('?')
            if len(string)==2:
                if string[1][0:4] == "next":
                    return redirect('checkout')
            else:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid login credentials!')

    return render(request,'accounts/login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out successfully.')
    return redirect('login')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')

@login_required(login_url='login')
def dashboard(request):
    orders = Order.objects.order_by('created_at').filter(user_id=request.user.id,is_ordered=True)
    userprofile = UserProfile.objects.get(user=request.user)
    order_count = orders.count()
    context={
       'order_count':order_count,
       'userprofile':userprofile,
    }
    return render(request,'accounts/dashboard.html',context)


def forgotPassword(request):
    if request.method=='POST':
        email = request.POST['email']

        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__iexact=email)
            current_site = get_current_site(request)
            mail_subject = 'Reset your password.'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgotPassword')

    return render(request,'accounts/forgotPassword.html')

def change_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('password_reset_temp')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('forgotPassword')

def password_reset_temp(request):
    if request.method=='POST':
        pwd = request.POST['password']
        cnf_pwd = request.POST['confirm_password']
        if pwd!=cnf_pwd:
            messages.error(request, 'Password do not match. Please re-type.')
            return redirect('password_reset_temp')
        else:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(pwd)
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
    return render(request,'accounts/password_reset_temp.html')

@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id,is_ordered=True)
    context={
       'orders':orders,
    }
    return render(request,'accounts/my_orders.html',context)

@login_required(login_url='login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile,user=request.user)
    if request.method=='POST':
        user_form = UserForm(request.POST,instance=request.user)
        profile_form = UserProfileForm(request.POST,request.FILES,instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request,"Your profile has been updated")
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    return render(request,'accounts/edit_profile.html',context)

@login_required(login_url='login')
def change_password(request):
    if request.method=='POST':
        current_password = request.POST["current_password"]
        new_password = request.POST["new_password"]
        confirm_password = request.POST["confirm_password"]
        email = request.user.email
        user = auth.authenticate(email=email, password=current_password)
        if user is not None:
            if new_password!=confirm_password:
                messages.error(request, 'Password do not match. Please re-type.')
                return render(request,'accounts/change_password.html')
            else:
                request.user.set_password(new_password)
                request.user.save()
                messages.success(request, 'Password changed successfully')
                return redirect('login')
        else:
            messages.error(request, 'Invalid Password!')
            return render(request,'accounts/change_password.html')
    else:
        return render(request,'accounts/change_password.html')

@login_required(login_url='login')
def order_detail(request,order_id):
    try:
        total = 0
        gst = 0
        grand_total = 0
        order = Order.objects.get(order_number=order_id)
        order_item = OrderProduct.objects.filter(order=order)
        for item in order_item:
            total += (item.product.price*item.quantity)
        gst = round(total*0.01,2)
        grand_total = round(total + gst,2)

        context={
           'total':total,
           'gst':gst,
           'grand_total':grand_total,
           'order':order,
           'order_item':order_item,
        }
        return render(request,'accounts/order_detail.html',context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')
