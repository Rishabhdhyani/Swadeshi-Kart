from django.shortcuts import render
from store.models import Product, ReviewRating

def func(k):
    return k[0]

def home(request):
    products = Product.objects.all().filter(is_available=True).order_by('created_date')
    list_product = []
    for product in products:
        temp = []
        temp.append(product.averageReview())
        temp.append(product)
        list_product.append(temp)

    list_product.sort(reverse=True,key=func)
    list_product = list_product[0:8]
    #print(list_product)
    ans_list=[]
    print(list_product)
    for i in list_product:
        ans_list.append(i[1])
    context = {
       'products':products,
       'ans_list':ans_list
    }
    return render(request,"home.html",context)
