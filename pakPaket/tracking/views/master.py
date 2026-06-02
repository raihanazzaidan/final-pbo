from urllib import request
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from ..models import Paket, TrackingHistory, TipeLayanan, Gudang, User

@login_required(login_url='login')
def getAllUser(request):
    if request.user.role != 'ADMIN':
        messages.error(request, "Akses ditolak! Khusus Admin.")
        return redirect('index')
    
    role_filter = request.GET.get('role', 'all')
    
    if role_filter == 'KURIR':
        users = User.objects.filter(role='KURIR').order_by('-date_joined')
    elif role_filter == 'CUSTOMER':
        users = User.objects.filter(role='CUSTOMER').order_by('-date_joined')
    else:
        users = User.objects.exclude(role='ADMIN') \
                            .exclude(is_superuser=True) \
                            .exclude(username='superadmin') \
                            .order_by('-date_joined')

    context = {
        'users': users,
        'current_filter': role_filter,
    }
    return render(request, 'tracking/master/user_list.html', context)

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
def getAllGudang(request):
    if request.user.role != 'ADMIN':
        messages.error(request, "Akses ditolak! Hanya Admin yang diizinkan melihat gudang.")
        return redirect('index') 

    gudang_list = Gudang.objects.all().order_by('namaGudang')
    context = {
        'gudang_list': gudang_list,
    }
    return render(request, 'tracking/master/getGudang.html', context)

@login_required(login_url='login')
def addGudang(request):
    if request.user.role != 'ADMIN':
        return redirect('index')
        
    if request.method == 'POST':
        nama_gudang = request.POST.get('namaGudang')
        alamat = request.POST.get('alamat')
        kota = request.POST.get('kota')
        
        if Gudang.objects.filter(namaGudang=nama_gudang).exists():
            messages.error(request, f"Gudang dengan nama '{nama_gudang}' sudah ada.")
            return render(request, 'tracking/master/addGudang.html', {'form_data': request.POST})
            
        Gudang.objects.create(
            namaGudang=nama_gudang,
            alamat=alamat,
            kota=kota
        )
        messages.success(request, f"Gudang '{nama_gudang}' berhasil ditambahkan!")
        return redirect('admin_dashboard')
    
    return render(request, 'tracking/master/addGudang.html')

@login_required(login_url='login')
def adminDashboard(request):
    paket_dikirim = Paket.objects.count()
    paket_diterima = Paket.objects.filter(status='DITERIMA').count()
    paket_dikembalikan = Paket.objects.filter(status='DIKEMBALIKAN').count()
    
    keberhasilan_global = 0
    total_selesai_global = paket_diterima + paket_dikembalikan
    if total_selesai_global > 0:
        keberhasilan_global = round((paket_diterima / total_selesai_global) * 100, 1)

    paket_sukses = Paket.objects.filter(status='DITERIMA', updated_at__isnull=False)  
    total_hari_semua = 0
    for p in paket_sukses:
        selisih = p.updated_at - p.created_at
        total_hari_semua += selisih.total_seconds() / 86400 
        
    rata_waktu_global = 0
    if paket_sukses.count() > 0:
        rata_waktu_global = round(total_hari_semua / paket_sukses.count(), 1)

    paket_terbaru = Paket.objects.all().order_by('-created_at')[:5]
    aktivitas_terbaru = TrackingHistory.objects.select_related('paket').all().order_by('-created_at')[:5]

    labels_chart = []
    data_paket_dikirim = []
    data_paket_diterima = []
    data_paket_dikembalikan = []
    data_keberhasilan_chart = []
    data_waktu_chart = []

    hari_ini = timezone.now().date()
    
    for i in range(5, -1, -1): 
        tanggal_loop = hari_ini - timedelta(days=i)
        
        labels_chart.append(tanggal_loop.strftime("%d %b")) 
 
        paket_harian = Paket.objects.filter(created_at__date=tanggal_loop) 
        
        jml_dikirim = paket_harian.all().count()
        jml_diterima = paket_harian.filter(status='DITERIMA').count()
        jml_dikembalikan = paket_harian.filter(status='DIKEMBALIKAN').count()
        
        data_paket_dikirim.append(jml_dikirim)
        data_paket_diterima.append(jml_diterima)
        data_paket_dikembalikan.append(jml_dikembalikan)

        paket_diterima_harian = paket_harian.filter(status='DITERIMA', updated_at__isnull=False)
        
        total_hari_harian = 0
        for p in paket_diterima_harian:
            selisih = p.updated_at - p.created_at
            total_hari_harian += selisih.total_seconds() / 86400
            
        rata_harian = 0
        if paket_diterima_harian.count() > 0:
            rata_harian = round(total_hari_harian / paket_diterima_harian.count(), 1)
            
        data_waktu_chart.append(rata_harian)

        total_selesai_harian = jml_diterima + jml_dikembalikan
        if total_selesai_harian > 0:
            persentase = (jml_diterima / total_selesai_harian) * 100
        else:
            persentase = 100 if jml_diterima > 0 else 0
        data_keberhasilan_chart.append(round(persentase, 1))


    context = {
        'paket_dikirim': paket_dikirim,
        'paket_diterima': paket_diterima,
        'paket_dikembalikan': paket_dikembalikan,
        'paket_terbaru': paket_terbaru,
        'labels_chart': labels_chart,
        'data_paket_dikirim': data_paket_dikirim,
        'data_paket_diterima': data_paket_diterima,
        'data_paket_dikembalikan': data_paket_dikembalikan,
        'keberhasilan_global': keberhasilan_global,
        'data_waktu_chart': data_waktu_chart,
        'data_keberhasilan_chart': data_keberhasilan_chart,
        'rata_waktu_global': rata_waktu_global,
        'aktivitas_terbaru': aktivitas_terbaru,
    }
    return render(request, 'tracking/master/adminDashboard.html', context)
