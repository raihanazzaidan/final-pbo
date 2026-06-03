from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..models import Paket, TrackingHistory, TipeLayanan
from django.db.models import Q

@login_required(login_url='login')
def kirimPaket(request):    
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
            status='DIKEMAS'
        )

        TrackingHistory.objects.create(
            paket=paket_baru,
            status='DIKEMAS',
            lokasi=pengirim.kota,
            notes="Paket telah didaftarkan ke sistem dan sedang dikemas oleh pengirim."
        )

        messages.success(request, f"Berhasil! Paket Anda telah terdaftar dengan resi: {paket_baru.resi}")
        
        return redirect(f"/paket/all/?id={request.user.id}")

    daftar_layanan = TipeLayanan.objects.all()
    return render(request, 'tracking/paket/kirim_paket.html', {
        'daftar_layanan': daftar_layanan
    })