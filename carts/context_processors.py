
from . models import Cart, CartItem
from .views import _cart_id

def cart_total(request):
    if 'admin' in request.path:
        return {}
    else:
        cart = Cart.objects.filter(cart_id=_cart_id(request))
        if request.user.is_authenticated:
            cart_item = CartItem.objects.all().filter(user=request.user)
        else:
            cart_item = CartItem.objects.all().filter(cart=cart[:1])
        cart_total_len = 0
        for item in cart_item:
            cart_total_len+=item.quantity
        return dict(cart_total_len=cart_total_len)
