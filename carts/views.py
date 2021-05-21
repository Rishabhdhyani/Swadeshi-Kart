from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from store.models import Product, Variation
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    current_user = request.user
    if current_user.is_authenticated:

        product = Product.objects.get(id=product_id)
        product_variation=[]
        if request.method=='POST':
            if request.method == 'POST':
                for item in request.POST:
                    key = item
                    value = request.POST[key]

                    try:
                        variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                        product_variation.append(variation)
                    except:
                        pass


        is_cart_item_exists = CartItem.objects.filter(product=product,user=current_user).exists()
        if is_cart_item_exists:

            cart_item = CartItem.objects.filter(product=product,user=current_user)
            # existing variation --> database
            # current variation --> product_variation
            # item_id --> database
            existing_variation_list=[]
            id=[]
            for item in cart_item:
                item_variation = item.variations.all()
                existing_variation_list.append(list(item_variation))
                id.append(item.id)

            if product_variation in existing_variation_list:
                ind = existing_variation_list.index(product_variation)
                item_id = id[ind]
                item = CartItem.objects.get(product=product,id=item_id)
                item.quantity+=1
                item.save()
            else:
                item = CartItem.objects.create(product=product,quantity=1,user=current_user)
                if len(product_variation)>0:
                    item.variations.clear()
                    item.variations.add(*product_variation)

                item.save()
        else:
            cart_item = CartItem.objects.create(
            user=current_user,
            product = product,
            quantity = 1,
            )

            if len(product_variation)>0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)

            cart_item.save()
        return redirect('cart')

    else:

        product = Product.objects.get(id=product_id)
        product_variation=[]
        if request.method=='POST':
            if request.method == 'POST':
                for item in request.POST:
                    key = item
                    value = request.POST[key]

                    try:
                        variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                        product_variation.append(variation)
                    except:
                        pass

        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
            cart_id = _cart_id(request)
            )
        cart.save()
        is_cart_item_exists = CartItem.objects.filter(product=product,cart=cart).exists()
        if is_cart_item_exists:

            cart_item = CartItem.objects.filter(product=product,cart=cart)
            # existing variation --> database
            # current variation --> product_variation
            # item_id --> database
            existing_variation_list=[]
            id=[]
            for item in cart_item:
                item_variation = item.variations.all()
                existing_variation_list.append(list(item_variation))
                id.append(item.id)

            if product_variation in existing_variation_list:
                ind = existing_variation_list.index(product_variation)
                item_id = id[ind]
                item = CartItem.objects.get(product=product,id=item_id)
                item.quantity+=1
                item.save()
            else:
                item = CartItem.objects.create(product=product,quantity=1,cart=cart)
                if len(product_variation)>0:
                    item.variations.clear()
                    item.variations.add(*product_variation)

                item.save()
        else:
            cart_item = CartItem.objects.create(
            cart = cart,
            product = product,
            quantity = 1,
            )

            if len(product_variation)>0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)

            cart_item.save()
        return redirect('cart')

def remove_cart(request, product_id, cart_item_id):
    current_user = request.user
    if current_user.is_authenticated:
        try:
            #cart = Cart.objects.get(cart_id=_cart_id(request))
            product = get_object_or_404(Product,id=product_id)
            cart_item = CartItem.objects.get(user=current_user,product=product,id=cart_item_id)

            if cart_item.quantity>1:
                cart_item.quantity-=1
                cart_item.save()
            else:
                cart_item.delete()
        except:
            pass

        return redirect('cart')
    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            product = get_object_or_404(Product,id=product_id)
            cart_item = CartItem.objects.get(cart=cart,product=product,id=cart_item_id)

            if cart_item.quantity>1:
                cart_item.quantity-=1
                cart_item.save()
            else:
                cart_item.delete()
        except:
            pass

        return redirect('cart')

def remove_cart_item(request,product_id,cart_item_id):
    current_user = request.user
    if current_user.is_authenticated:
        try:
            #cart = Cart.objects.get(cart_id=_cart_id(request))
            product = get_object_or_404(Product,id=product_id)
            cart_item = CartItem.objects.get(user=current_user,product=product,id=cart_item_id)

            if cart_item:
                cart_item.delete()

        except:
            pass

        return redirect('cart')
    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            product = get_object_or_404(Product,id=product_id)
            cart_item = CartItem.objects.get(cart=cart,product=product,id=cart_item_id)

            if cart_item:
                cart_item.delete()

        except:
            pass

        return redirect('cart')

def cart(request,total=0,quantity=0,cart_items=None):
    try:
        gst = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.all().filter(user=request.user,is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart,is_active=True)
        for item in cart_items:
            total += (item.product.price*item.quantity)
            quantity += item.quantity
        gst = round(total*0.01,2)
        grand_total = round(total + gst,2)
    except ObjectDoesNotExist:
        pass
    context = {
      'total':total,
      'quantity':quantity,
      'cart_items':cart_items,
      'gst':gst,
      'grand_total':grand_total
    }
    return render(request,'store/cart.html',context)

@login_required(login_url='login')
def checkout(request,total=0,quantity=0,cart_items=None):
    try:
        gst = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.all().filter(user=request.user,is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart,is_active=True)
        for item in cart_items:
            total += (item.product.price*item.quantity)
            quantity += item.quantity
        gst = round(total*0.01,2)
        grand_total = round(total + gst,2)
    except ObjectDoesNotExist:
        pass
    context = {
      'total':total,
      'quantity':quantity,
      'cart_items':cart_items,
      'gst':gst,
      'grand_total':grand_total
    }
    return render(request,'store/checkout.html',context)
