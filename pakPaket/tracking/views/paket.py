from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..models import Paket, TrackingHistory, TipeLayanan
from django.db.models import Q

def cek_resi(request):
    resi = request.GET.get('resi')
    
    context = {}

    if resi:
        try:
            paket = Paket.objects.get(resi=resi)
            riwayat = paket.history.all().order_by('-timestamp')
            context['paket'] = paket
            context['riwayat'] = riwayat
        except Paket.DoesNotExist:
            context['error'] = "Paket dengan nomor resi tersebut tidak ditemukan."

    return render(request, 'tracking/paket/cek_resi.html', context)

def cek_resi_api(request, resi):
    paket = get_object_or_404(Paket, resi=resi)
    return ({
        "id": str(paket.id),
        "status": paket.status,
        "resi": paket.resi,
        "pengirim": paket.pengirim.nama,
        "penerima": paket.penerima
    })

@login_required(login_url='login')
def kirim_paket(request):    
    if request.user.role != 'CUSTOMER':
        messages.error(request, "Hanya akun Pelanggan yang dapat membuat kiriman.")
        return redirect('index')
    
    pengirim = request.user.customer_profile

    if request.method == 'POST':
        deskripsi = request.POST.get('deskripsi')
        berat = float(request.POST.get('berat'))
        dimensi = int(request.POST.get('dimensi'))
        layanan_id = request.POST.get('tipeLayanan')
        
        penerima = request.POST.get('penerima')
        alamat = request.POST.get('alamatPenerima')
        kota = request.POST.get('kotaPenerima')
        no_hp = request.POST.get('noHpPenerima')

        tipe_layanan = get_object_or_404(TipeLayanan, id=layanan_id)
        berat_hitung = berat if berat >= 1.0 else 1.0
        ongkos_kirim = berat_hitung * tipe_layanan.hargaPerKg

        paket_baru = Paket.objects.create(
            deskripsi=deskripsi,
            berat=berat,
            dimensi=dimensi,
            tipeLayanan=tipe_layanan,
            ongkosKirim=ongkos_kirim,
            pengirim=pengirim,
            penerima=penerima,
            alamatPenerima=alamat,
            kotaPenerima=kota,
            noHpPenerima=no_hp,
            status='DIKEMAS' # Status awal
        )

        TrackingHistory.objects.create(
            paket=paket_baru,
            status='DIKEMAS',
            lokasi=pengirim.kota,
            notes="Paket telah didaftarkan ke sistem dan sedang dikemas oleh pengirim."
        )

        messages.success(request, f"Berhasil! Paket Anda telah terdaftar dengan resi: {paket_baru.resi}")
        
        return redirect(f"/paket/cek-resi/?id={paket_baru.id}")

    daftar_layanan = TipeLayanan.objects.all()
    return render(request, 'tracking/paket/kirim_paket.html', {
        'daftar_layanan': daftar_layanan
    })

def getAllPaket(request):
    if request.user.role == 'KURIR':
        # Perbaikan: Cek profil menggunakan 'kurir_profile'
        if hasattr(request.user, 'kurir_profile'):
            profil_kurir = request.user.kurir_profile
            # Perbaikan Logika: Kurir HANYA melihat paket DIKEMAS atau paket DIKIRIM yang dibawa oleh dirinya sendiri
            paket_list = Paket.objects.filter(
                Q(status='DIKEMAS') | Q(status='DIKIRIM', kurir=profil_kurir)
            ).order_by('created_at')
        else:
            paket_list = Paket.objects.none()
            
    elif request.user.role == 'CUSTOMER':
        # Ini sudah benar menggunakan 'customer_profile'
        if hasattr(request.user, 'customer_profile'):
            paket_list = Paket.objects.filter(pengirim=request.user.customer_profile).order_by('-created_at')
        else:
            paket_list = Paket.objects.none()
            
    elif request.user.role == 'ADMIN':
        paket_list = Paket.objects.all().order_by('-created_at')
    else:
        paket_list = Paket.objects.none()

    return render(request, 'tracking/paket/list_paket.html', {
        'paket_list': paket_list
    })


@login_required(login_url='login')
def antar_paket(request, paket_id):
    """Fungsi agar Kurir mengambil paket dan mulai mengirimkannya"""
    
    # PERBAIKAN: Gunakan 'kurir_profile'
    if request.user.role != 'KURIR' or not hasattr(request.user, 'kurir_profile'):
        messages.error(request, "Akses ditolak! Profil kurir tidak ditemukan.")
        return redirect('all_paket') 

    paket = get_object_or_404(Paket, id=paket_id)
    
    # Update Status dan assign Kurir menggunakan 'kurir_profile'
    paket.status = 'DIKIRIM'
    paket.kurir = request.user.kurir_profile
    paket.save()

    # Catat ke History
    TrackingHistory.objects.create(
        paket=paket,
        status='DIKIRIM',
        lokasi='Diperjalanan',
        notes=f"Paket telah dibawa oleh kurir {request.user.kurir_profile.nama} menuju lokasi tujuan."
    )
    
    messages.success(request, f"Berhasil! Paket {paket.resi} sedang Anda kirim.")
    return redirect('all_paket')


@login_required(login_url='login')
def terima_paket(request, paket_id):
    """Fungsi agar Kurir mengonfirmasi paket telah sampai ke pelanggan"""
    
    # PERBAIKAN: Gunakan 'kurir_profile'
    if request.user.role != 'KURIR' or not hasattr(request.user, 'kurir_profile'):
        messages.error(request, "Akses ditolak!")
        return redirect('all_paket')

    paket = get_object_or_404(Paket, id=paket_id)
    
    # Update Status menjadi Diterima
    paket.status = 'DITERIMA'
    paket.save()

    # Catat ke History (Lokasi menggunakan kota penerima)
    TrackingHistory.objects.create(
        paket=paket,
        status='DITERIMA',
        lokasi=paket.kotaPenerima,
        notes="Paket telah berhasil diserahkan kepada penerima yang bersangkutan."
    )
    
    messages.success(request, f"Selesai! Paket {paket.resi} telah berhasil dikirim.")
    return redirect('all_paket')