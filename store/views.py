from django.shortcuts import render, get_object_or_404
from .models import Product
from category.models import Category

# Create your views here.
def store(request, category_slug=None):
    all_products = None

    if category_slug:
        try:
            category_name = Category.objects.get(slug=category_slug)
            all_products = Product.objects.all().filter(category=category_name ,is_available=True)
        except:
            return render(request, '404.html')
    else:
        all_products = Product.objects.all().filter(is_available=True)
    
    category_list = Category.objects.all()

    context = {
        'all_products': all_products,
        'category_list': category_list
    }
    return render(request, 'store/store.html', context)

def productDetail(request, category_slug, prod_slug):
    try:
        product = Product.objects.get(category__slug=category_slug, slug=prod_slug)
        context = {
            'product':product
        }
        return render(request, 'store/product-detail.html', context)
    except:
        return render(request, '404.html')