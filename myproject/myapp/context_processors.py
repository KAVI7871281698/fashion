from .models import add_to_cart, Register
from django.core.exceptions import ValidationError

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

# def validate_file_size_10mb(file):
#     max_size = 10 * 1024 * 1024  # 10 MB
#     if file.size > max_size:
#         raise ValidationError("File size must be under 10 MB")
