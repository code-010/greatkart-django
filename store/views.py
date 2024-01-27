from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.db.models import Q # Django Q object for complex queries
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import math
from .models import Product, ProductVariation
from category.models import Category
from carts.models import CartItem
from carts.views import _user_session_id

# Create your views here.
def store(request, category_slug=None):
    all_products = None

    if category_slug:
        try:
            category_name = Category.objects.get(slug=category_slug)
            all_products = Product.objects.all().filter(category=category_name ,is_available=True).order_by('id')
        except:
            return render(request, '404.html')
    else:
        all_products = Product.objects.all().filter(is_available=True).order_by('id')
    
    paginator = Paginator(all_products, 3)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
        

    
    category_list = Category.objects.all()

    context = {
        'all_products': paged_products,
        'num_pages': range(1, paginator.num_pages+1),
        
        'product_count': all_products.count(),
        'category_list': category_list
    }
    return render(request, 'store/store.html', context)

def productDetail(request, category_slug, prod_slug):
    try:
        product = Product.objects.get(category__slug=category_slug, slug=prod_slug)
        isInCart = CartItem.objects.filter(cart__cart_id=_user_session_id(request), product=product).exists()


        product_variation = product.productvariation_set.colors()
        product_variation_set = []
        product_variation_len = math.ceil(len(product_variation)/6)
        for i in range(0, product_variation_len):
            product_variation_set.append(tuple(product_variation[i*6:(i+1)*6]))
        
        product_variation_set = tuple(product_variation_set)
        
        
        context = {
            'product':product,
            'isInCart':isInCart,
            'product_variation_set':product_variation_set
        }
        return render(request, 'store/product-detail.html', context)
    except:
        return render(request, '404.html')

def search(request):
    if 'q' in request.GET:
        keyword = request.GET['q']
        if not keyword:
            return redirect('home')
    
    page = request.GET.get('page')
    keyword = request.GET.get('q')
    search_products = Product.objects.filter(Q(product_name__icontains=keyword) | Q(category__category_name__icontains=keyword)).order_by('id')
    paginator = Paginator(search_products, 2)
    paged_products = paginator.get_page(page)
        
    
    category_list = Category.objects.all()

    context = {
        'all_products': paged_products,
        'num_pages': range(1, paginator.num_pages+1),
        'keyword': keyword,
        'product_count': search_products.count(),
        'category_list': category_list
    }
    return render(request, 'store/store.html', context)