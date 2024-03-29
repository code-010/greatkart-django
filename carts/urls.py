from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart, name='cart'),
    path('add_cart/<int:product_id>/', views.add_cart, name='add_cart'),
    path('increment_cart/<int:cart_item_id>/', views.increment_cart_item, name='increment_cart_item'),
    path('decrement_cart/<int:cart_item_id>/', views.decrement_cart_item, name='decrement_cart_item'),
    # path('remove_cart/<int:product_id>/', views.remove_cart, name='remove_cart'),
    path('remove_cart_item/<int:cart_item_id>/', views.remove_cart_item, name='remove_cart_item'),
    # path('remove_cart_item/<int:product_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('checkout/', views.checkout, name='checkout'),
    path('order_processing', views.order_processing, name='order_processing')
]