from django.urls import path,include

from .views import ItemList,ProductPage,CheckoutPage,add_to_cart,remove_from_cart,OrderSummary,remove_from_order,add_to_order,delete_now,handlerequest,CoupenCode


app_name="app"
urlpatterns=[
    path('',ItemList.as_view(),name='item_list'),
    path('products/<int:yo>',ProductPage.as_view(),name='product'),
    path('checkout/',CheckoutPage.as_view(),name='checkout'),
    path('order-summary/', OrderSummary.as_view(), name='order'),

    path('add/<int:yo>', add_to_cart.as_view(), name='add'),
    path('remove/<int:rem>', remove_from_cart.as_view(), name='remove'),
    path('remove-from-order/<int:rem>', remove_from_order.as_view(), name='remove1'),
    path('added-to-order/<int:rem>', add_to_order.as_view(), name='add1'),
    path('added-to-order/<int:rem>', add_to_order.as_view(), name='add1'),
    path('delete/<int:rem>', delete_now.as_view(), name='delete'),
    path('handlerequest/', handlerequest.as_view(), name='handlerequest'),
    path('coupon/',CoupenCode.as_view(),name="coupon")

]