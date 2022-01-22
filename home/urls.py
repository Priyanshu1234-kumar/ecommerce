from django.contrib import admin
from django.urls import path,include
from home import views
urlpatterns = [
    path('', views.index,name="home"),
    path('index', views.index,name="home"),
    path('base',views.base,name="base"),
    path('about',views.about,name="about"),
    path('tracker',views.tracker,name="tracker"),
    path('contact',views.contact,name="contact"),
    path('productView/<int:myid>',views.productView,name="ProductView"),
    path('checkout',views.checkout,name="checkout"),
    path('handlerequest',views.handlerequest,name="HandleRequest"),
     path('search',views.search,name="Search"),
]