from django.views import View
from django.shortcuts import render,get_object_or_404,redirect
from .models import Item,OrderItem,Order,BillingAddress,Coupon
from django.utils import timezone
from django.contrib import messages
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import Checkoutform,CouponForm
from django.core.exceptions import ObjectDoesNotExist
from Paytm import Checksum
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
MERCHANT_KEY='vJ_E9WthxQ#Iig!N'
class ItemList(ListView):
    model = Item
    paginate_by = 10
    template_name = "app/home-page.html"
class ProductPage(View):
    def get(self,request,*args,**kwargs):

        item=Item.objects.get(pk=kwargs['yo'])
        return render(request,'app/product-page.html',{'item':item})
class CheckoutPage(View):
    def get(self,request):
        try:
            order = Order.objects.get(user=request.user, ordered=False)
            form = Checkoutform()
            return render(request, 'app/checkout-page.html', {'form': form,'order':order,'coupon':CouponForm()})
        except ObjectDoesNotExist:
            messages.info("You do not have any current order!")
            return redirect("app:checkout")
    def post(self,request):
        form=Checkoutform(request.POST or None)
        try:
            order_qs=Order.objects.get(user=request.user,ordered=False)
            if form.is_valid():
                Address=form.cleaned_data.get('Address')
                apartment_add=form.cleaned_data.get('apartment_add')
                country=form.cleaned_data.get('country')
                zip=form.cleaned_data.get('zip')
                #Add functionality to these fields
                #same_bill_add=form.cleaned_data.get['same_bill_add']
                #save_info=form.cleaned_data.get['save_info']
                #payment_option=form.cleaned_data.get['payment_option']
                billingaddress=BillingAddress(user=request.user,Address=Address,apartment_add=apartment_add,country=country,zip=zip)
                billingaddress.save()
                order_qs.billing=billingaddress
                order_qs.ordered=True
                order_qs.save()
                param_dict = {
                    'MID': 'MuoTsy79388780301387',
                    'ORDER_ID': str(order_qs.id+100),
                    'TXN_AMOUNT':str(order_qs.total()),
                    'CUST_ID': request.user.username,
                    'INDUSTRY_TYPE_ID': 'Retail',
                    'WEBSITE': 'WEBSTAGING',
                    'CHANNEL_ID': 'WEB',
                    'CALLBACK_URL': 'http://127.0.0.1:8000/handlerequest/',
                }
                param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
                return render(request, 'app/paytm.html', {'param_dict': param_dict})
            messages.info(request,"Failed checkout")
            return redirect("app:checkout")
        except ObjectDoesNotExist:
            messages.info(request,"You do not have any active order")
            return redirect("app:order")
class add_to_cart(LoginRequiredMixin,View):
    def get(self,request,*args,**kwargs):
        item=get_object_or_404(Item,pk=kwargs['yo'])
        order_item,created=OrderItem.objects.get_or_create(item=item,user=request.user,ordered=False)
        order_qs=Order.objects.filter(user=request.user,ordered=False)
        if order_qs.exists():
            order=order_qs[0]
            if order.items.filter(item=kwargs['yo']).exists():
                order_item.quantity=order_item.quantity+1
                order_item.save()
                messages.info(request,"This item quantity was updated!")
                return redirect('app:order')
            else:
                order.items.add(order_item)
                messages.info(request,"This item was added to your cart!")
                return redirect('app:order')
        else:
            ordered_data=timezone.now()
            order=Order.objects.create(user=request.user,ordered_date=ordered_data,)
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart!")

        return redirect('app:order')
class remove_from_cart(View,LoginRequiredMixin):
    def get(self, request, *args, **kwargs):
        item = get_object_or_404(Item, pk=kwargs['rem'])

        order_qs=Order.objects.filter(user=request.user,ordered=False)
        if order_qs.exists():
            order=order_qs[0]
            if order.items.filter(item=kwargs['rem']).exists():
                order_item = OrderItem.objects.filter(
                    item=item,
                    user=request.user,
                    ordered=False
                )[0]

                order_item.delete()
                messages.info(request,"This item quantity was removed your cart!")
                return redirect('app:product', item.id)

            else:
                messages.info(request,"This item was not in your card!")
                return redirect("app:product",item.id)
        else:
            messages.info(request, "You do not have an active order!")

            return redirect("app:product", item.id)

class OrderSummary(View,LoginRequiredMixin):
    def get(self,request,*args,**kwargs):
        qs=Order.objects.filter(user=request.user,ordered=False)
        if qs.exists():
            if qs[0].items.count()!=0:
                order=qs[0]
                return render(request, 'app/order.html', {'order': order})
            else:
                message="Sorry Your Cart is Empty!"
                return render(request,'app/order.html',{'message':message})
        else:
            messages.info(request,"You do not have any active order!")
            return redirect("app:item_list")

class remove_from_order(View,LoginRequiredMixin):
    def get(self, request, *args, **kwargs):
        item = get_object_or_404(Item, pk=kwargs['rem'])

        order_qs=Order.objects.filter(user=request.user,ordered=False)
        if order_qs.exists():
            order=order_qs[0]
            if order.items.filter(item=kwargs['rem']).exists():
                order_item = OrderItem.objects.filter(
                    item=item,
                    user=request.user,
                    ordered=False
                )[0]
                if order_item.quantity>1:
                    order_item.quantity-=1
                else:
                    order_item.delete()
                order_item.save()
                messages.info(request,"This item quantity was updated!")
                return redirect('app:order')

            else:
                messages.info(request,"This item was not in your card!")
                return redirect("app:order")
        else:
            messages.info(request, "You do not have an active order!")

            return redirect("app:order")
class add_to_order(View,LoginRequiredMixin):
    def get(self, request, *args, **kwargs):
        item = get_object_or_404(Item, pk=kwargs['rem'])

        order_qs=Order.objects.filter(user=request.user,ordered=False)
        if order_qs.exists():
            order=order_qs[0]
            if order.items.filter(item=kwargs['rem']).exists():
                order_item = OrderItem.objects.filter(
                    item=item,
                    user=request.user,
                    ordered=False
                )[0]

                order_item.quantity+=1
                order_item.save()
                messages.info(request,"This item quantity was updated!")
                return redirect('app:order')

            else:
                messages.info(request,"This item was not in your card!")
                return redirect("app:order")
        else:
            messages.info(request, "You do not have an active order!")

            return redirect("app:order")
class delete_now(View,LoginRequiredMixin):
    def get(self, request, *args, **kwargs):
        item = get_object_or_404(Item, pk=kwargs['rem'])

        order_qs=Order.objects.filter(user=request.user,ordered=False)
        if order_qs.exists():
            order=order_qs[0]
            if order.items.filter(item=kwargs['rem']).exists():
                order_item = OrderItem.objects.filter(
                    item=item,
                    user=request.user,
                    ordered=False
                )[0]

                order_item.delete()
                messages.info(request,"This item quantity was removed your cart!")
                return redirect('app:order')

            else:
                messages.info(request,"This item was not in your card!")
                return redirect("app:product",item.id)
        else:
            messages.info(request, "You do not have an active order!")

            return redirect("app:product", item.id)

@method_decorator(csrf_exempt,name='dispatch')
class handlerequest(View):
    def post(self,request):
        form = request.POST
        response_dict = {}
        for i in form.keys():
            response_dict[i] = form[i]
            if i == 'CHECKSUMHASH':
                checksum = form[i]

        verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
        if verify:
            if response_dict['RESPCODE'] == '01':

                print('order successful')
            else:
                print('order was not successful because' + response_dict['RESPMSG'])

        return render(request, 'app/paymentstatus.html', {'response': response_dict})


class CoupenCode(View):
    def post(self,request):
        form=CouponForm(request.POST or None)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                coupon=Coupon.objects.get(code=code)
                try:
                    order=Order.objects.get(user=request.user,ordered=False)
                    order.coupon=coupon
                    order.save()
                    messages.info(request,"Congratulations! Your coupon code has been successfully applied..")
                    return redirect("app:checkout")
                except ObjectDoesNotExist:
                    messages.info(request,"You do not have any current order!")
                    return redirect("app:checkout")
            except ObjectDoesNotExist:
                messages.info(request,"This coupon does not exist")
                return redirect("app:checkout")