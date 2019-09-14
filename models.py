from django.db import models
from django.conf import settings
from django_countries.fields import CountryField
CATEGORY_CHOICES=(
    ('S','Shirt'),
    ('SW', 'Sport Wear'),
    ('OW', 'OutWear')
)
LABEL_CHOICES=(
    ('P','primary'),
    ('S', 'secondary'),
    ('D', 'danger')
)
ADDRESS_CHOICES=(
    ('B','Billing'),
    ('S','Shipping'),
)
class Item(models.Model):
    title=models.CharField(max_length=100)
    price=models.FloatField()
    discountprice = models.FloatField(blank=True,null=True)
    category=models.CharField(choices=CATEGORY_CHOICES,max_length=2)
    label=models.CharField(choices=LABEL_CHOICES,max_length=1)
    description=models.TextField()
    quantity=models.IntegerField(default=1)
    image=models.ImageField()
    def __str__(self):
        return self.title

class OrderItem(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    ordered=models.BooleanField(default=False)
    item=models.ForeignKey(Item,on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    def __str__(self):
        return f"{self.quantity} of {self.item.title}"
    def get_total_item_price(self):
        return self.quantity*self.item.price
    def get_discount_price(self):
        return self.quantity*self.item.discountprice
    def get_save(self):
        return self.get_total_item_price()-self.get_discount_price()
    def get_final_price(self):
        if self.item.discountprice:
            return self.get_discount_price()
        else:
            return self.get_total_item_price()
#Like a Shopping cart
class Order(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    items=models.ManyToManyField(OrderItem)
    start_date=models.DateTimeField(auto_now_add=True)
    ordered_date=models.DateTimeField()
    ordered=models.BooleanField(default=False)
    billing=models.ForeignKey('BillingAddress',on_delete=models.SET_NULL,blank=True,null=True,related_name='biiling_address')
    shipping=models.ForeignKey('BillingAddress',on_delete=models.SET_NULL,blank=True,null=True,related_name='shipping_adress')
    coupon=models.ForeignKey('Coupon',on_delete=models.SET_NULL,blank=True,null=True)
    def __str__(self):
        return self.user.username

    def total(self):
        total=0
        for order_item in self.items.all():
            total=total+order_item.get_final_price()
        if self.coupon:
            total-=self.coupon.amount
        return total

class BillingAddress(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    Address=models.CharField(max_length=100)
    apartment_add=models.CharField(max_length=100)
    country=CountryField(multiple=False)
    zip=models.CharField(max_length=100)
    address_type=models.CharField(max_length=1,choices=ADDRESS_CHOICES,null=True,blank=True)
    default=models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class Coupon(models.Model):
    code=models.CharField(max_length=20)
    amount=models.FloatField()
    def __str__(self):
        return self.code
