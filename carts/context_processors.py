from .models import Cart, CartItem
from .views import _user_session_id

def cartCounter(request):
    if 'admin' in request.path:
        return {}
    
    try:
        cart = Cart.objects.get(cart_id=_user_session_id(request))
        cart_items_count = CartItem.objects.filter(cart=cart).count()
    except:
        cart_items_count = 0
    return dict(cart_counter = cart_items_count)