# accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth import logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy

from .forms import CardMarkerCreationForm, CardMarkerPasswordUpdateForm

User = get_user_model()

def admin_required(view_func):
    """Only allow authenticated users where `.is_admin` is True."""
    return user_passes_test(lambda u: u.is_authenticated and getattr(u, 'is_admin', False))(view_func)


# -------------------------
# Admin: Create Card Marker
# -------------------------
@admin_required
def admin_create_cardmarker(request):
    if request.method == 'POST':
        form = CardMarkerCreationForm(request.POST)
        if form.is_valid():
            # create user but enforce card marker role & flags
            user = form.save(commit=False)
            user.role = User.ROLE_STAFF
            user.is_staff = False    # card markers should NOT access Django admin
            user.is_superuser = False
            if 'password1' in form.cleaned_data:
                user.set_password(form.cleaned_data['password1'])
            user.save()
            messages.success(request, f"Card Marker '{user.username}' created.")
            return redirect('accounts:cardmarker_list')
    else:
        form = CardMarkerCreationForm()
    return render(request, 'accounts/create_cardmarker.html', {'form': form})


# -------------------------
# Admin: List Card Markers
# -------------------------
@admin_required
def cardmarker_list_view(request):
    markers = User.objects.filter(role=User.ROLE_STAFF).order_by('username')
    return render(request, 'accounts/cardmarker_list.html', {'markers': markers})


# -------------------------
# Admin: Change Card Marker Password
# -------------------------
@admin_required
def cardmarker_update_password(request, pk):
    marker = get_object_or_404(User, pk=pk, role=User.ROLE_STAFF)

    if request.method == "POST":
        form = CardMarkerPasswordUpdateForm(request.POST)
        if form.is_valid():
            marker.set_password(form.cleaned_data['password1'])
            marker.save()
            messages.success(request, "Password updated successfully.")
            return redirect('accounts:cardmarker_list')
    else:
        form = CardMarkerPasswordUpdateForm()

    return render(request, 'accounts/cardmarker_update_password.html', {'form': form, 'marker': marker})


# -------------------------
# Admin: Delete Card Marker (confirmation + POST)
# -------------------------
@admin_required
def cardmarker_delete(request, pk):
    marker = get_object_or_404(User, pk=pk, role=User.ROLE_STAFF)

    # Protect: admin cannot delete themselves
    if request.user.pk == marker.pk:
        messages.error(request, "You cannot delete your own account from here.")
        return redirect('accounts:cardmarker_list')

    if request.method == 'POST':
        username = marker.username
        marker.delete()
        messages.success(request, f"Card Marker '{username}' deleted.")
        return redirect('accounts:cardmarker_list')
    # GET -> render a confirmation page
    return render(request, 'accounts/cardmarker_confirm_delete.html', {'marker': marker})


# -------------------------
# Login Views
# -------------------------
class AdminLoginView(auth_views.LoginView):
    template_name = 'registration/login_admin.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        resp = super().form_valid(form)
        user = self.request.user

        if not getattr(user, 'is_admin', False):
            logout(self.request)
            messages.error(self.request, "This login is for admin only.")
            return redirect('accounts:login_cardmark')

        return resp


class CardMarkLoginView(auth_views.LoginView):
    template_name = 'registration/login_cardmark.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        resp = super().form_valid(form)
        user = self.request.user

        if getattr(user, 'role', None) != User.ROLE_STAFF:
            logout(self.request)
            messages.error(self.request, "Only Card Marker staff can log in here.")
            return redirect('accounts:login_admin')

        return resp


# Default login redirect (/accounts/login/)
def login_redirect(request):
    return redirect('accounts:login_cardmark')
