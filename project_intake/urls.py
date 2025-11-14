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
from django.conf import settings
from django.conf.urls.static import static

# Build CAS-specific URL patterns only when CAS is enabled
cas_urlpatterns: list = []
if getattr(settings, "ENABLE_CAS", False):
    from cas import views as cas_views  # type: ignore

    cas_urlpatterns += [
        path('cas-login/', cas_views.login, name='cas_login'),
        path('cas-logout/', cas_views.logout, name='cas_logout'),
        # Override admin auth views to use CAS
        path('admin/login/', cas_views.login, name='admin_login'),
        path('admin/logout/', cas_views.logout, name='admin_logout'),
    ]

core_urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', include('projects.urls')),
]

if getattr(settings, "ENABLE_AZURE_AD", False):
    core_urlpatterns.insert(3, path('accounts/', include('allauth.urls')))

urlpatterns = cas_urlpatterns + core_urlpatterns
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)