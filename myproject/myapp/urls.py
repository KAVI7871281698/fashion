from django.urls import path,include
from .import views

urlpatterns = [
    path('', views.index, name='index'),
    path('base', views.base, name='base'),
    path('categories', views.categories, name='categories'),
    path('collection', views.collection, name='collection'),
    path('about', views.about, name='about'),
    path('contact', views.contact, name='contact'),
    path('signature_collect', views.signature_collect, name='signature_collect'),
    path('special_services', views.special_services, name='special_services'),
    path('permium_wear', views.permium_wear, name='permium_wear'),
    path('limited_edition_collection', views.limited_edition_collection, name='limited_edition_collection'),
    path('accessories', views.accessories, name='accessories'),
    path('cinephile_tees', views.cinephile_tees, name='cinephile_tees'),
    path('fqa', views.fqa, name='fqa'),

    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logout_view, name='logout'),
    path('order_details', views.order_details, name='order_details'),
    path('add-to-cart/<int:id>/', views.cart, name='add_to_cart'),

    path('cart', views.view_cart, name='view_cart'),
    path('cart/increase/<int:id>/', views.increase_quantity, name='increase_quantity'),
    path('cart/decrease/<int:id>/', views.decrease_quantity, name='decrease_quantity'),
    path('cart/remove/<int:id>/', views.remove_cart_item, name='remove_cart_item'),

    path('order-now', views.order_now_page, name='order_now_page'),
    path('order-now-submit', views.order_now, name='order_now'),
    path('order-success', views.order_success, name='order_success'),
    path('payment-success/',views. payment_success, name='payment_success'),
    path('dashboard',views. dashboard, name='dashboard'),
    path('order_dashboard',views. order_dashboard, name='order_dashboard'),
    path('product_dashboard',views. product_dashboard, name='product_dashboard'),
    path('categorizes_dashboard',views. categorizes_dashboard, name='categorizes_dashboard'),
    path('user_dashboard',views. user_dashboard, name='user_dashboard'),
    path('dashboard_report',views. dashboard_report, name='dashboard_report'),
    # path('get-cart-count', views.get_cart_count, name='get_cart_count'),
]
