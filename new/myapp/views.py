from django.shortcuts import render,HttpResponse
from .forms import NameForm
from .Black_Scholes import FinancialDataProcessor
# Create your views here.
def index(request):   
    return render(request,"index.html") #renders the index page 


def home(request):
    if request.method == "POST":
        form = NameForm(request.POST)

        if form.is_valid():
            cleaned_data = form.cleaned_data
            obj = FinancialDataProcessor(cleaned_data=cleaned_data)
            res = obj.result()
            return HttpResponse(f"Option Price is: {res}")
    else:
        form = NameForm()        

    return render(request,"Home.html",{'form':form}) #renders the home page 
