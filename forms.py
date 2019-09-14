from django import forms
from django_countries.fields import CountryField
PAYMENT_CHOICES=(
    ('S','STRIPE'),
    ('P','PAYPAL')
)
class Checkoutform(forms.Form):
    Address=forms.CharField()
    apartment_add=forms.CharField(required=False)
    country=CountryField(blank_label='(select country)').formfield()
    zip=forms.CharField()
    save_billing=forms.BooleanField(widget=forms.CheckboxInput(),required=False)
    save_info=forms.BooleanField(widget=forms.CheckboxInput(),required=False)

class CouponForm(forms.Form):
    code=forms.CharField()