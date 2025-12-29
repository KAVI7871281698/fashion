from .models import add_to_cart, Register

def cart_count(request):
    email = request.session.get('email')
    count = 0

    if email:
        try:
            user = Register.objects.get(email=email)
            count = add_to_cart.objects.filter(user=user).count()
        except Register.DoesNotExist:
            pass

    return {'cart_count': count}


def logged_in_user(request):
    user = None
    email = request.session.get('email')

    if email:
        try:
            user = Register.objects.get(email=email)
        except Register.DoesNotExist:
            pass

    return {'logged_user': user}
