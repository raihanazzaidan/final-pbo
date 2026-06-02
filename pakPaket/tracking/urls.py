from django.urls import path
from .views import paket, master, auth

urlpatterns = [
    path('', master.index, name='index'),
    
    # CRUD User (Admin Only)
    path('panel/users/', master.getAllUser, name='get_all_user'),
    path('panel/users/add/', master.addUser, name='add_user'),
    path('panel/users/edit/<uuid:user_id>/', master.editUser, name='edit_user'),
    path('panel/users/hapus/<uuid:user_id>/', master.deleteUser, name='delete_user'),

    # URL Paket
    path('paket/cekResi/', paket.cekResi, name='cek_resi'),
    path('api/paket/<uuid:paket_id>/', paket.cek_resi_api, name='api_paket'),
    path('paket/all/', paket.getAllPaket, name='all_paket'),
    path('paket/<uuid:paket_id>/', paket.detailPaket, name='detail_paket'),
    path('paket/kirim/', paket.kirimPaket, name='kirim_paket'),

    # URL Auth
    path('login/', auth.loginView, name='login'),
    path('logout/', auth.logoutView, name='logout'),
    path('register/', auth.customerRegister, name='register'),
    path('adm/register/', auth.adminRegister, name='admin_register'),
    path('kurir/register/', auth.kurirRegister, name='kurir_register'),

    # URL Master 
    path('layanan/add/', master.addTipeLayanan, name='tambah_layanan'),
    path('adm/', master.adminDashboard, name='admin_dashboard'),

    # URL Kurir
    path('paket/kurir/antar/<uuid:paket_id>/', paket.antarPaket, name='antar_paket'),
    path('paket/kurir/terima/<uuid:paket_id>/', paket.terimaPaket, name='terima_paket'),
    path('paket/kurir/retur/<uuid:paket_id>/', paket.returPaket, name='retur_paket'),

]