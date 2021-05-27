from django.shortcuts import render
from store.models import Product, ReviewRating
from surprise import SVD # Matrix Factorization Based Algorithm
from surprise import Dataset
from surprise.model_selection import cross_validate
from surprise.reader import Reader
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)


def func(k):
    return k[0]

def home(request):
    if request.user.is_authenticated:
        products = Product.objects.all().filter(is_available=True).order_by('created_date')
        flag = 1
        current_user = request.user
        user_ratings = ReviewRating.objects.filter(user=current_user)
        list_product = []
        if user_ratings:
            # Recommender System
            all_user_rating = ReviewRating.objects.all()
            df_list=[]
            for review in all_user_rating:
                li=[]
                li.append(review.user.id)
                li.append(review.product.id)
                li.append(review.rating)
                df_list.append(li)
            df_arr = np.array(df_list)
            df = pd.DataFrame(df_arr,columns=['userId','productId','rating'])
            reader= Reader()
            svd = SVD()
            data = Dataset.load_from_df(df[['userId','productId','rating']],reader)
            trainset = data.build_full_trainset()
            svd.fit(trainset)
            for product in products:
                is_user_purchase = ReviewRating.objects.filter(user=current_user,product=product).exists()
                is_product_review = ReviewRating.objects.filter(product=product).exists()

                if (is_user_purchase==False) and (is_product_review==True):
                    pred = svd.predict(uid=current_user.id, iid=product.id, r_ui=None).est
                    temp=[]
                    temp.append(pred)
                    temp.append(product)
                    list_product.append(temp)

            list_product.sort(reverse=True,key=func)
            list_product = list_product[0:8]
            #print(list_product)
            ans_list=[]
            #print(list_product)
            for i in list_product:
                ans_list.append(i[1])
            context = {
               'ans_list':ans_list,
               'flag':flag,
            }
            return render(request,"home.html",context)
        else:
            flag=0
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
            #print(list_product)
            for i in list_product:
                ans_list.append(i[1])
            context = {
               'products':products,
               'ans_list':ans_list,
               'flag':flag,
            }
            return render(request,"home.html",context)

    else:
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
        flag=0
        ans_list=[]
        #print(list_product)
        for i in list_product:
            ans_list.append(i[1])
        context = {
           'products':products,
           'ans_list':ans_list,
           'flag':flag,
        }
        return render(request,"home.html",context)
