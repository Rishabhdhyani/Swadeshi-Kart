from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from store.models import Product
from .models import Cart, CartItem
# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
        cart_id = _cart_id(request)
        )
    cart.save()
    try:
        cart_item = CartItem.objects.get(product=product,cart=cart)
        cart_item.quantity+=1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
        cart = cart,
        product = product,
        quantity = 1,
        )
        cart_item.save()
    return redirect('cart')

def remove_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product,id=product_id)
    cart_item = CartItem.objects.get(cart=cart,product=product)

    if cart_item.quantity>1:
        cart_item.quantity-=1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('cart')

def remove_cart_item(request,product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product,id=product_id)
    cart_item = CartItem.objects.get(cart=cart,product=product)

    if cart_item:
        cart_item.delete()
    

    return redirect('cart')

def cart(request,total=0,quantity=0,cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart,is_active=True)
        for item in cart_items:
            total += (item.product.price*item.quantity)
            quantity += item.quantity
        gst = round(total*0.01,2)
        grand_total = round(total + gst,2)
    except ObjectNotExist:
        pass
    context = {
      'total':total,
      'quantity':quantity,
      'cart_items':cart_items,
      'gst':gst,
      'grand_total':grand_total
    }
    return render(request,'store/cart.html',context)
