from django.shortcuts import render, redirect
from .models import OrderProduct, Order, Payment
from django.http import HttpResponse, JsonResponse
from carts.models import CartItem
from store.models import Product
from .forms import OrderForm
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
import datetime
import json

# Create your views here.
def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    # Store transaction details inside Payment model
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move cart items or Order Product table
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()

        # Reduce the quantity of the sold Products
        product = Product.objects.get(id=item.product_id)
        product.stock-=item.quantity
        product.save()
    # clear the cart
    CartItem.objects.filter(user=request.user).delete()

    # Send order received email to the customer

    mail_subject = 'Thank you for the order!'
    message = render_to_string('orders/order_received_email.html', {
        'user': request.user,
        'order':order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()
    # send order number and transaction id back to senData method via json response
    data = {
    'order_number':order.order_number,
    'trans_id':payment.payment_id,
    }
    return JsonResponse(data)

def place_order(request,total=0,quantity=0):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()

    if cart_count<=0:
        return redirect('store')
    gst = 0
    grand_total = 0
    for item in cart_items:
        total += (item.product.price*item.quantity)
        quantity += item.quantity
    gst = round(total*0.01,2)
    grand_total = round(total + gst,2)

    if request.method=='POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the billing information inside Order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.tax = gst
            data.order_total = grand_total
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            # order no
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number=order_number
            data.save()
            order = Order.objects.get(user=current_user,order_number=order_number,is_ordered=False)
            context={
                'total':total,
                'gst':gst,
                'grand_total':grand_total,
                'cart_items':cart_items,
                'total':total,
                'order':order,
            }
            return render(request,'orders/payments.html',context)
        else:
            return redirect('checkout')

def order_complete(request):

    try:
        order_number = request.GET.get('order_number')
        trans_id = request.GET.get('payment_id')
        #print(f'{order_number} and {trans_id}')
        total = 0
        gst = 0
        grand_total = 0
        order = Order.objects.get(order_number=order_number,is_ordered=True)
        payment = Payment.objects.get(payment_id=trans_id)
        order_item = OrderProduct.objects.filter(order=order)
        for item in order_item:
            total += (item.product.price*item.quantity)
        gst = round(total*0.01,2)
        grand_total = round(total + gst,2)

        context={
           'order_number':order_number,
           'trans_id':trans_id,
           'total':total,
           'gst':gst,
           'grand_total':grand_total,
           'order':order,
           'order_item':order_item,
           'payment':payment,
        }
        return render(request,'orders/order_complete.html',context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')
