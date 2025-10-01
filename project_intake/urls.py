"""
URL configuration for project_intake project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
# import cas.views  # Temporarily disabled to test URL loading

# Simple test view to verify URL loading
def test_cas_status(request):
    try:
        import cas.views
        return HttpResponse("CAS module available - cas.views imported successfully")
    except ImportError as e:
        return HttpResponse(f"CAS module error: {e}")

urlpatterns = [
    # Test CAS availability
    path('test-cas/', test_cas_status, name='test_cas_status'),
    # Simple CAS login view for testing
    # path('cas-login/', cas.views.login, name='cas_login_simple'),  # Temporarily disabled
    # CAS login/logout must come BEFORE admin URLs to override them
    # path('admin/login/', cas.views.login, name='admin_login'),  # Temporarily disabled
    # path('admin/logout/', cas.views.logout, name='admin_logout'),  # Temporarily disabled
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/', include('allauth.urls')),
    # path('cas/', include('cas.urls')),  # Temporarily disabled - ModuleNotFoundError: No module named 'cas.urls'
    path('', include('projects.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)