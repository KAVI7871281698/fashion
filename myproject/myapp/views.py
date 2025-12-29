from django.shortcuts import render, redirect, get_object_or_404
from .models import Register, product, add_to_cart, Order, home, Coupon, UsedCoupon
from django.contrib import messages
import razorpay
from django.conf import settings
from django.http import HttpResponse
from django.db.models import Count,Q
from django.utils import timezone
from decimal import Decimal
from django.db.models import Sum
from django.utils import timezone


# ================= BASIC PAGES =================

def base(request):
    return render(request,'base.html')

def landing(request):
    return render(request, 'landing_page.html')

def index(request):
    banner = home.objects.all()

    coupons = Coupon.objects.filter(
        is_active=True,
        expiry_date__gte=timezone.now().date()
    )

    return render(request, 'index.html', {
        'banner': banner,
        'coupons': coupons
    })

def collection(request):
    return render(request, 'collection.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def signature_collect(request):
    query = request.GET.get('q')

    products = product.objects.filter(
        product_Categorie__iexact='signature_collection'
    )

    if query:
        products = products.filter(
            Q(product_name__icontains=query) |
            Q(product_des__icontains=query)
        )

    return render(request, 'signature_collection.html', {
        'products': products
    })


def special_services(request):
    query = request.GET.get('q')

    products = product.objects.filter(product_Categorie__iexact='Special Services')

    if query:
        products = products.filter(
            Q(product_name__icontains=query) |
            Q(product_des__icontains=query)
        )

    return render(request, 'special_services.html', {'products': products})



def permium_wear(request):
    query = request.GET.get('q')

    products = product.objects.filter(product_Categorie__iexact='Premium Wear')

    if query:
        products = products.filter(
            Q(product_name__icontains=query) |
            Q(product_des__icontains=query)
        )

    return render(request, 'permium_wear.html', {'products': products})

def limited_edition_collection(request):
    query = request.GET.get('q')

    products = product.objects.filter(product_Categorie__iexact='Limited Edition')

    if query:
        products = products.filter(
            Q(product_name__icontains=query) |
            Q(product_des__icontains=query)
        )

    return render(request, 'limited_edition_collection.html', {'products': products})

def accessories(request):
    query = request.GET.get('q')

    products = product.objects.filter(product_Categorie__iexact='Accessories')

    if query:
        products = products.filter(
            Q(product_name__icontains=query) |
            Q(product_des__icontains=query)
        )

    return render(request, 'accessories.html', {'products': products})

def cinephile_tees(request):
    query = request.GET.get('q')

    products = product.objects.filter(product_Categorie__iexact='Cinephile Tees')

    if query:
        products = products.filter(
            Q(product_name__icontains=query) |
            Q(product_des__icontains=query)
        )

    return render(request, 'cinephile_tees.html', {'products': products})


def fqa(request):
    return render(request, 'FQA.html')


def order_details(request):
    email = request.session.get('email')
    if not email:
        return redirect('login')
    user = Register.objects.get(email=email)
    shipping_info = Order.objects.filter(user=user)

    return render(request, 'order_details.html', {
        'shipping_info': shipping_info
    })
    
    
def logout_view(request):
    request.session.flush()
    return redirect('login') 


# ================= AUTH =================

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = Register.objects.get(email=email)
            if user.password == password:
                request.session['email'] = email
                request.session['is_logged_in'] = True

                pending_product_id = request.session.pop('pending_cart_product', None)
                return_url = request.session.pop('return_url', '/')

                if pending_product_id:
                    return redirect('add_to_cart', pending_product_id)

                return redirect(return_url)
            else:
                messages.error(request, 'Incorrect Password')
        except Register.DoesNotExist:
            messages.error(request, 'Incorrect Email')

    return render(request, 'login.html')


def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_pass')

        if password != confirm_password:
            messages.error(request, 'Password does not match')
            return redirect('register')

        if Register.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('login')

        Register.objects.create(
            name=name,
            email=email,
            phone=phone,
            password=password,
            confirm_password=confirm_password
        )

        messages.success(request, 'Registered Successfully')
        return redirect('login')

    return render(request, 'register.html')


def logout(request):
    request.session.flush()
    return redirect('login')


# ================= CATEGORIES =================

def categories(request):
    selected_category = request.GET.get('category')
    search_query = request.GET.get('q')  

    view_product = product.objects.all()
    
    if selected_category:
        view_product = view_product.filter(product_Categorie=selected_category)

    if search_query:
        view_product = view_product.filter(
            Q(product_name__icontains=search_query) |
            Q(product_des__icontains=search_query)
        )

    raw_counts = product.objects.values('product_Categorie').annotate(count=Count('id'))

    category_counts = {
        item['product_Categorie'].replace(" ", "_").lower(): item['count']
        for item in raw_counts
    }

    return render(request, 'categories.html', {
        'view_product': view_product,
        'selected_category': selected_category,
        'search_query': search_query,
        'category_counts': category_counts,
        'total_count': product.objects.count()
    })


# ================= ADD TO CART =================

def cart(request, id):
    email = request.session.get('email')

    if not email:
        request.session['pending_cart_product'] = id
        request.session['return_url'] = request.META.get('HTTP_REFERER', '/')
        return redirect('login')

    user = get_object_or_404(Register, email=email)
    product_obj = get_object_or_404(product, id=id)

    cart_item, created = add_to_cart.objects.get_or_create(
        user=user,
        add_to_cart_product=product_obj
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect(request.META.get('HTTP_REFERER', '/'))


# ================= CART =================

def view_cart(request):
    email = request.session.get('email')
    if not email:
        return redirect('login')

    user = Register.objects.get(email=email)
    cart_items = add_to_cart.objects.filter(user=user)
    total_amount = sum(item.total_price for item in cart_items)

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_amount': total_amount
    })


def increase_quantity(request, id):
    user = Register.objects.get(email=request.session.get('email'))
    item = get_object_or_404(add_to_cart, id=id, user=user)
    item.quantity += 1
    item.save()
    return redirect('view_cart')


def decrease_quantity(request, id):
    user = Register.objects.get(email=request.session.get('email'))
    item = get_object_or_404(add_to_cart, id=id, user=user)

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect('view_cart')


def remove_cart_item(request, id):
    user = Register.objects.get(email=request.session.get('email'))
    item = get_object_or_404(add_to_cart, id=id, user=user)
    item.delete()
    return redirect('view_cart')


# ================= ORDER PAGE =================

def order_now_page(request):
    user = Register.objects.get(email=request.session.get('email'))
    cart_items = add_to_cart.objects.filter(user=user)

    total_amount = sum(item.total_price for item in cart_items)

    used_coupon_ids = UsedCoupon.objects.filter(user=user).values_list('coupon_id', flat=True)

    coupons = Coupon.objects.filter(
        is_active=True,
        expiry_date__gte=timezone.now().date(),
        min_order_amount__lte=total_amount
    ).exclude(id__in=used_coupon_ids)

    return render(request, 'order_now.html', {
        'cart_items': cart_items,
        'total_amount': total_amount,
        'coupons': coupons
    })


# ================= APPLY COUPON & PAY =================
def order_now(request):
    user = Register.objects.get(email=request.session.get('email'))
    cart_items = add_to_cart.objects.filter(user=user)

    if not cart_items.exists():
        return redirect('view_cart')

    delivery_address = request.POST.get('delivery_address')
    delivery_date = request.POST.get('delivery_date')
    coupon_code = request.POST.get('coupon_code')

    total_amount = sum(item.total_price for item in cart_items)
    discount = Decimal('0')
    coupon_obj = None

    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code, is_active=True)

            if not coupon.is_valid():
                messages.error(request, 'Coupon expired or inactive')
                return redirect('order_now_page')

            if UsedCoupon.objects.filter(user=user, coupon=coupon).exists():
                messages.error(request, 'Coupon already used')
                return redirect('order_now_page')

            if total_amount < Decimal(coupon.min_order_amount):
                messages.error(request, 'Minimum order amount not met')
                return redirect('order_now_page')

            # ✅ calculate discount
            if coupon.discount_type == 'flat':
                discount = Decimal(coupon.discount_value)
            else:
                discount = (Decimal(coupon.discount_value) / Decimal('100')) * total_amount

            # ✅ CAP discount (same as frontend)
            if discount >= total_amount:
                discount = total_amount - Decimal('1.00')

            coupon_obj = coupon

        except Coupon.DoesNotExist:
            messages.error(request, 'Invalid coupon')
            return redirect('order_now_page')

    final_amount = total_amount - discount

    # Razorpay minimum ₹1 safeguard
    if final_amount < Decimal('1.00'):
        final_amount = Decimal('1.00')

    final_amount = final_amount.quantize(Decimal('0.01'))
    amount_paise = int(final_amount * Decimal('100'))

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    razorpay_order = client.order.create({
        "amount": amount_paise,
        "currency": "INR",
        "payment_capture": 1
    })

    # store session data
    request.session['delivery_address'] = delivery_address
    request.session['delivery_date'] = delivery_date
    request.session['coupon_id'] = coupon_obj.id if coupon_obj else None
    request.session['discount'] = str(discount)

    # ✅ NOW IT WILL GO TO PAYMENT PAGE
    return render(request, "razorpay_payment.html", {
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "order_id": razorpay_order['id'],
        "amount": amount_paise,
        "final_amount": final_amount
    })

# ================= PAYMENT SUCCESS =================
def payment_success(request):
    email = request.session.get('email')
    if not email:
        return redirect('login')

    user = Register.objects.get(email=email)
    cart_items = add_to_cart.objects.filter(user=user)

    total_amount = sum(item.total_price for item in cart_items)

    # ✅ FIX: convert session discount (string) → Decimal
    discount = Decimal(request.session.get('discount', '0'))

    final_amount = total_amount - discount

    # Razorpay safety (just in case)
    if final_amount < Decimal('1.00'):
        final_amount = Decimal('1.00')

    order = Order.objects.create(
        user=user,
        total_amount=final_amount,
        delivery_address=request.session.get('delivery_address'),
        delivery_date=request.session.get('delivery_date'),
        payment_status="Paid",
        status="Confirmed"
    )

    coupon_id = request.session.get('coupon_id')
    if coupon_id:
        coupon = Coupon.objects.get(id=coupon_id)
        UsedCoupon.objects.create(user=user, coupon=coupon)

        coupon.used_count += 1
        coupon.save()

    cart_items.delete()
    request.session.flush()

    return redirect('order_success')



def order_success(request):
    return render(request, 'order_success.html')

def dashboard(request):
    # Total counts
    total_orders = Order.objects.count()
    total_users = Register.objects.count()
    total_products = product.objects.count()

    # Total revenue (only PAID orders)
    total_revenue = (
        Order.objects
        .filter(payment_status='Paid')
        .aggregate(total=Sum('total_amount'))['total']
        or 0
    )

    context = {
        'total_orders': total_orders,
        'total_users': total_users,
        'total_products': total_products,
        'total_revenue': total_revenue,
    }

    return render(request, 'dashboard.html', context)

def order_dashboard(request):
    orders = Order.objects.all()
    return render(request, "order_dashboard.html", {"orders": orders})

def product_dashboard(request):
    products = product.objects.all()

    return render(request, "product_dashboard.html", {
        "products": products
    })

def categorizes_dashboard(request):
    categories = ["Wedding", "Fashion", "Film Shoot", "Accessories"]
    return render(request, "categorizes_dashboard.html", {"categories": categories})

def user_dashboard(request):
    users = Register.objects.all()

    return render(request, "user_dashboard.html", {
        "users": users
    })

def dashboard_report(request):
    today = timezone.now().date()

    # Monthly sales (paid orders only)
    monthly_sales = (
        Order.objects
        .filter(
            payment_status='Paid',
            created_at__month=today.month,
            created_at__year=today.year
        )
        .aggregate(total=Sum('total_amount'))['total']
        or 0
    )

    # Orders completed
    orders_completed = Order.objects.filter(status='Delivered').count()

    # New users this month
    new_users = Register.objects.filter(
        id__isnull=False
    ).count()

    context = {
        "monthly_sales": monthly_sales,
        "orders_completed": orders_completed,
        "new_users": new_users,
    }

    return render(request, "dashboard_report.html", context)