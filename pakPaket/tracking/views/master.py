from urllib import request

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..models import Paket, TrackingHistory, TipeLayanan, Gudang, User

@login_required(login_url='login')
def getAllUser(request):
    if request.user.role != 'ADMIN':
        messages.error(request, "Akses ditolak! Khusus Admin.")
        return redirect('index')
    
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'tracking/master/user_list.html', {'users': users})

@login_required(login_url='login')
def addUser(request):
    if request.user.role != 'ADMIN':
        return redirect('index')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        no_hp = request.POST.get('noHp')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, f"Gagal! Username '{username}' sudah digunakan.")
            return redirect('add_user')
            
        User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role,
            noHp=no_hp
        )
        messages.success(request, f"User {username} berhasil ditambahkan!")
        return redirect('get_all_user')
        
    return render(request, 'tracking/master/addUser.html', {'action': 'add'})

@login_required(login_url='login')
def editUser(request, user_id):
    if request.user.role != 'ADMIN':
        return redirect('index')
        
    target_user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        target_user.username = request.POST.get('username')
        target_user.email = request.POST.get('email')
        target_user.role = request.POST.get('role')
        target_user.noHp = request.POST.get('noHp')
        
        new_password = request.POST.get('password')
        if new_password:
            target_user.set_password(new_password)
            
        target_user.save()
        messages.success(request, f"Data user {target_user.username} berhasil diperbarui!")
        return redirect('get_all_user')
        
    return render(request, 'tracking/master/addUser.html', {
        'action': 'edit', 
        'target_user': target_user
    })

@login_required(login_url='login')
def deleteUser(request, user_id):
    if request.user.role != 'ADMIN':
        return redirect('index')
        
    target_user = get_object_or_404(User, id=user_id)
    
    if target_user == request.user:
        messages.error(request, "Anda tidak bisa menghapus akun Anda sendiri!")
    else:
        target_user.delete()
        messages.success(request, "User berhasil dihapus dari sistem.")
        
    return redirect('get_all_user')

def index(request):
    return render(request, 'tracking/master/index.html')

@login_required(login_url='login')
def addTipeLayanan(request):
    """Controller untuk menambah Tipe Layanan Baru (Khusus ADMIN)"""
    
    if request.user.role != 'ADMIN':
        messages.error(request, "Akses ditolak! Hanya Admin yang diizinkan menambah layanan.")
        return redirect('index') 

    if request.method == 'POST':
        nama_layanan = request.POST.get('namaLayanan')
        harga = request.POST.get('hargaPerKg')
        estimasi = request.POST.get('estHari')

        if TipeLayanan.objects.filter(namaLayanan__iexact=nama_layanan).exists():
            messages.error(request, f"Gagal! Layanan dengan nama '{nama_layanan}' sudah ada.")
            return render(request, 'tracking/master/layanan_form.html', {'form_data': request.POST})

        try:
            TipeLayanan.objects.create(
                namaLayanan=nama_layanan,
                hargaPerKg=float(harga),
                estHari=int(estimasi)
            )
            messages.success(request, f"Layanan '{nama_layanan}' berhasil ditambahkan!")
            
            # TODO:
            return redirect('index') 
            
        except ValueError:
            messages.error(request, "Pastikan format Harga dan Estimasi Hari berupa angka yang valid!")
            return render(request, 'tracking/master/layanan_form.html', {'form_data': request.POST})

    return render(request, 'tracking/master/addLayanan.html')

@login_required(login_url='login')
def dasborAdmin(request):
    if request.user.role != 'ADMIN':
        messages.error(request, "Akses ditolak! Hanya admin yang dapat mengakses dasbor ini.")
        return redirect('index')
    
    total_paket = Paket.objects.count()
    paket_dikemas = Paket.objects.filter(status='DIKEMAS').count()
    paket_dikirim = Paket.objects.filter(status='DIKIRIM').count()
    paket_diterima = Paket.objects.filter(status='DITERIMA').count()

    paket_terbaru = Paket.objects.all().order_by('-id')[:5]


    return render(request, 'tracking/master/adminDasbor.html', {
        'total_paket': total_paket,
        'paket_dikemas': paket_dikemas,
        'paket_dikirim': paket_dikirim,
        'paket_diterima': paket_diterima,
        'paket_terbaru': paket_terbaru
    })