# accounts/decorators.py
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from functools import wraps

def _check_admin(user):
    return user.is_authenticated and user.is_admin

def _check_staff_or_admin(user):
    return user.is_authenticated and (user.is_admin or user.is_staff_user)

def admin_required(view_func):
    """
    Decorator: only allow users with role 'admin' (or superuser).
    Use on function views.
    """
    return user_passes_test(_check_admin)(view_func)

def staff_or_admin_required(view_func):
    """
    Decorator: allow 'staff' and 'admin' roles.
    Use on function views.
    """
    return user_passes_test(_check_staff_or_admin)(view_func)


# Helper for CBV (method decorator usage)
from django.utils.decorators import method_decorator

def admin_required_cbv(cls):
    return method_decorator(user_passes_test(_check_admin), name='dispatch')(cls)

def staff_or_admin_required_cbv(cls):
    return method_decorator(user_passes_test(_check_staff_or_admin), name='dispatch')(cls)
