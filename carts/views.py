
import decimal
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from store.models import Product, ProductVariation
from carts.models import Cart, CartItem
from django.contrib.auth.decorators import login_required

# Create your views here.
def _user_session_id(request):
    user_sessionId = request.session.session_key
    if not user_sessionId:
        user_sessionId = request.session.create()
    return user_sessionId

def _get_cart(request):
    if request.user.is_authenticated:
        cart = Cart.objects.get(cart_id=request.user.email)
    else:
        cart = Cart.objects.get(cart_id=_user_session_id(request))
    return cart

def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    product_variation_list = []
    if request.method == 'POST':
        for key in request.POST:
            value = request.POST[key]
            
            try:
                variation = ProductVariation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                product_variation_list.append(variation)
            except:
                pass
    try:
        # cart = Cart.objects.get(cart_id=_user_session_id(request))
        cart = _get_cart(request)
    except Cart.DoesNotExist:
        if request.user.is_authenticated:
            cart = Cart.objects.create(cart_id=request.user.email)
        else:
            cart = Cart.objects.create(cart_id=_user_session_id(request))
        #cart = Cart.objects.create(cart_id=_user_session_id(request))
        cart.save()
    
    try:
        cart_items = CartItem.objects.filter(product=product ,cart=cart)
        VariationNotFound = True
        for i in cart_items:
            if set(i.variations.all()) == set(product_variation_list):
                VariationNotFound = False
                cart_item = i
                cart_item.quantity += 1
                break
        
        if VariationNotFound:
            cart_item = CartItem.objects.create(
                product = product,
                cart = cart,
                quantity = 1,
            )
            for item in product_variation_list:
                cart_item.variations.add(item)

    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product = product,
            cart = cart,
            quantity = 1,
        )
        for item in product_variation_list:
            cart_item.variations.add(item)
    cart_item.save()

    return redirect('cart')

# def remove_cart(request, product_id):
#     cart = Cart.objects.get(cart_id=_user_session_id(request))
#     product = get_object_or_404(Product, id=product_id)
#     cart_item = CartItem.objects.get(product=product, cart=cart)
#     if cart_item.quantity > 1:
#         cart_item.quantity -= 1
#         cart_item.save()
#     else:
#         cart_item.delete()
#     return redirect('cart')

def increment_cart_item(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('cart')

def decrement_cart_item(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')

# def remove_cart_item(request, product_id):
#     cart = Cart.objects.get(cart_id=_user_session_id(request))
#     product = get_object_or_404(Product, id=product_id)
#     cart_item = CartItem.objects.filter(product=product, cart=cart)
#     cart_item.delete()
#     return redirect('cart')
def remove_cart_item(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

def cart(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    try:
        # cart = Cart.objects.get(cart_id=_user_session_id(request))
        cart = _get_cart(request)
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = round(total *  decimal.Decimal(0.18),2)
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass

    context = {
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax': tax,
        'grand_total': grand_total
    }
    
    return render(request, 'store/cart.html', context)

@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    try:
        # cart = Cart.objects.get(cart_id=_user_session_id(request))
        cart = _get_cart(request)
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = round(total *  decimal.Decimal(0.18),2)
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass

    context = {
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax': tax,
        'grand_total': grand_total
    }
    return render(request, 'store/place-order.html', context)

def order_processing(request):
    return HttpResponse("order_processing")
