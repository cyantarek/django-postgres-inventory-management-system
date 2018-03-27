"""inventory URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
	path('admin/', admin.site.urls),
	path('', views.index),
	path('login/', views.login_view),
	path('logout/', views.logout_view),
	path('profile/', views.user_profile),

	path('category/', views.category_management),
	path('category/status_change/<id>/', views.status_change_category),
	path('category/add/', views.add_category),

	path('user/', views.user_management),
	path('user/status_change/<id>/', views.status_change_user),
	path('user/add/', views.add_user),

	path('brand/', views.brand_management),
	path('brand/status_change/<id>/', views.status_change_brand),
	path('brand/add/', views.add_brand),

	path('product/', views.product_management),
	path('product/status_change/<id>/', views.status_change_product),
	path('product/add/', views.add_product),

	path('order/', views.order_management),
	path('order/add/', views.add_order),
	path('order/status_change/<id>/', views.status_change_order),
	path('invoice/<id>/', views.invoce_maker),
]
