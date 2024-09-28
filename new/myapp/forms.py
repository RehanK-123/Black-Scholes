from django import forms 

class NameForm(forms.Form):
    expiration = forms.CharField(max_length=10,min_length=0,label="Expiration")
    date = forms.CharField(max_length=10,min_length=0,label="Date")
    strike = forms.DecimalField(label='Strike')
    type = forms.CharField(max_length=4,min_length=3,label='Type')


    