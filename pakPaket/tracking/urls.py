from django.urls import path
from .views import paket, master, auth

urlpatterns = [
    # URL Paket
    path('cek-resi/', paket.cek_resi, name='cek_resi_publik'),
    path('api/paket/<uuid:paket_id>/', paket.cek_resi_api, name='api_paket'),

    # URL Auth
    path('login/', auth.login, name='login'),
    path('logout/', auth.logout, name='logout'),
    path('register/', auth.customerRegister, name='register'),
]