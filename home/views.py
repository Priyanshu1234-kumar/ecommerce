
from django.shortcuts import render
from home.models import Product,Contact,Order,OrderUpdate
from django.contrib import messages
from math import ceil
import json
from django.views.decorators.csrf import csrf_exempt
from PayTm import Checksum
MERCHANT_KEY = 'kbzk1DSbJiV_O3p5';

from django.http import HttpResponse

# Create your views here.
def index(request):
    #products=Product.objects.all()
    #print(products)
    #params={ 'no_of_slides':nSlides, 'range':range(1,nSlides), 'product':products }
    #allProds=[[products,range(1,nSlides),nSlides],
     #        [products,range(1,nSlides),nSlides]]

    allProds=[]
    catProds=Product.objects.values('category','id')
    cats={item['category'] for item in catProds}
    for cat in cats:
        prod=Product.objects.filter(category=cat)
        n=len(prod)
        nSlides= n//4 + ceil((n/4)-(n//4))
        allProds.append([prod,range(1,nSlides),nSlides])

    params={'allProds':allProds}
    messages.success(request, 'Welcome Everyone, I am very glad to present this website which has so many amazing features !!')
    return render(request, 'index.html',params)

def base(request):
    return render(request, 'base.html')

def about(request):
    return render(request, 'about.html')

def tracker(request):
    if request.method=="POST":
        orderId=request.POST.get('orderId','')
        email=request.POST.get('email','')
        try:
            order=Order.objects.filter(order_id=orderId,email=email)
            if len(order)>0:
                update=OrderUpdate.objects.filter(order_id=orderId)
                updates=[]
                for item in update:
                    updates.append({'text':item.update_desc, 'time':item.timestamp})
                    response = json.dumps({"status":"success","updates": updates,"itemsJson": order[0].items_json},default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noItem"}')

        except Exception as e:
           return HttpResponse('{"status":"error"}')

    return render(request, 'tracker.html')

def contact(request):
    if request.method=="POST":
        username=request.POST.get('username','')
        email=request.POST.get('email','')
        phone=request.POST.get('phone','')
        desc=request.POST.get('desc','')
        contact=Contact(username=username,email=email,phone=phone,desc=desc)
        contact.save()
        messages.success(request, 'Your Details Submitted Successfully !! We Will Try Our Best to Solve Your Problems !!')
    return render(request, 'contact.html')

def checkout(request):
    if request.method=="POST":
        items_json=request.POST.get('itemsJson','')
        amount=request.POST.get('amount','')
        username=request.POST.get('username','')
        email=request.POST.get('email','')
        phone=request.POST.get('phone','')
        address=request.POST.get('address','')
        address_2=request.POST.get('address_2','')
        zip_code=request.POST.get('zip_code','')
        city=request.POST.get('city','')
        state=request.POST.get('state','')
        order=Order(amount=amount,items_json=items_json,username=username,email=email,phone=phone,address=address,address_2=address_2,zip_code=zip_code,city=city,state=state)
        order.save()
        update=OrderUpdate(order_id=order.order_id,update_desc="The order has been placed")
        update.save()
        thank=True
        id=order.order_id
        param_dict={
            'MID':'WorldP64425807474247',
            'ORDER_ID':str(order.order_id),
            'TXN_AMOUNT':str(amount),
            'CUST_ID':email,
            'INDUSTRY_TYPE_ID':'Retail',
            'WEBSITE':'WEBSTAGING',
            'CHANNEL_ID':'WEB',
	        'CALLBACK_URL':'http://127.0.0.1:8000/handlerequest',
        }
        param_dict['CHECKSUMHASH']=Checksum.generate_checksum(param_dict,MERCHANT_KEY)
        return render(request,'paytm.html',{'param_dict':param_dict})
        #return render(request, 'checkout.html',{'thank': thank,'id': id})
        # Request paytm to accept the amount and transfer into your bank after payment done by user


    return render(request, 'checkout.html')

def productView(request,myid):
    #fetch the product using the id
    product=Product.objects.filter(id=myid)
    return render(request, 'productView.html',{'product':product[0]})

@csrf_exempt
def handlerequest(request):
     # paytm will send you post request here
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
   return render(request, 'paymentstatus.html', {'response': response_dict})

def searchMatch(query,item):
    #"return true only if query matches the item"
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
       return False
def search(request):
    query=request.GET.get('search')
    allProds=[]
    catProds=Product.objects.values('category','id')
    cats={item['category'] for item in catProds}
    for cat in cats:
        prodtemp=Product.objects.filter(category=cat)
        prod=[item for item in prodtemp if searchMatch(query,item)]
        n=len(prod)
        nSlides= n//4 + ceil((n/4)-(n//4))
        if len(prod)!=0:
            allProds.append([prod,range(1,nSlides),nSlides])

    params={'allProds':allProds,'msg':""}
    if len(allProds)==0 or len(query)<3:
        params={'msg':'Please make sure to enter relevant search query!!'}
    messages.success(request, 'Welcome Everyone, I am very glad to present this website which has so many amazing features !!')
    return render(request, 'search.html',params)