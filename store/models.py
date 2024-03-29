from django.db import models
from django.urls import reverse
from category.models import Category

# Create your models here.
class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True)
    price =  models.DecimalField(max_digits=10, decimal_places=2)
    images = models.ImageField(upload_to='photos/products', blank=True)
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('product-detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name

class ProductVariationManager(models.Manager):
    def colors(self):
        return super(ProductVariationManager, self).filter(variation_category='Color', is_active=True)
    def sizes(self):
        return super(ProductVariationManager, self).filter(variation_category='Size', is_active=True)
    
variation_category_choice = (
    ('Color', 'color'),
    ('Size', 'size')
)

class ProductVariation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices=variation_category_choice)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    objects = ProductVariationManager()

    def __str__(self):
        return " ".join((self.product.product_name, self.variation_category, self.variation_value))

