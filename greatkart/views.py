from django.shortcuts import HttpResponse, render
from store.models import Product

def home(request):
    all_products = Product.objects.all().filter(is_available=True)[:8]
    context = {
        'all_products': all_products
    }
    return render(request, 'home.html', context)