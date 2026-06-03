from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..models import Paket, TrackingHistory
from django.db.models import Q

@login_required(login_url='login')
def antarPaket(request, paket_id):
    if request.user.role != 'KURIR' or not hasattr(request.user, 'kurir_profile'):
        messages.error(request, "Akses ditolak! Profil kurir tidak ditemukan.")
        return redirect('all_paket') 

    paket = get_object_or_404(Paket, id=paket_id)
    
    paket.status = 'DIKIRIM'
    paket.kurir = request.user.kurir_profile
    paket.save()

    TrackingHistory.objects.create(
        paket=paket,
        status='DIKIRIM',
        lokasi='Diperjalanan',
        notes=f"Paket telah dibawa oleh kurir {request.user.kurir_profile.nama} menuju lokasi tujuan."
    )
    
    messages.success(request, f"Berhasil! Paket {paket.resi} sedang Anda kirim.")
    return redirect('all_paket')


@login_required(login_url='login')
def terimaPaket(request, paket_id):    
    if request.user.role != 'KURIR' or not hasattr(request.user, 'kurir_profile'):
        messages.error(request, "Akses ditolak!")
        return redirect('all_paket')

    paket = get_object_or_404(Paket, id=paket_id)
    
    paket.status = 'DITERIMA'
    paket.save()

    TrackingHistory.objects.create(
        paket=paket,
        status='DITERIMA',
        lokasi=paket.kotaPenerima,
        notes="Paket telah berhasil diserahkan kepada penerima yang bersangkutan."
    )
    
    messages.success(request, f"Selesai! Paket {paket.resi} telah berhasil dikirim.")
    return redirect('all_paket')

@login_required(login_url='login')
def returPaket(request, paket_id):
    if request.user.role != 'KURIR' or not hasattr(request.user, 'kurir_profile'):
        messages.error(request, "Akses ditolak!")
        return redirect('all_paket')

    paket = get_object_or_404(Paket, id=paket_id)
    
    paket.status = 'DIKEMBALIKAN'
    paket.save()

    TrackingHistory.objects.create(
        paket=paket,
        status='DIKEMBALIKAN',
        lokasi=paket.kotaPenerima,
        notes="Paket dikembalikan ke pengirim karena penerima tidak dapat dihubungi atau menolak menerima paket."
    )
    
    messages.success(request, f"Paket {paket.resi} telah dikembalikan ke pengirim.")
    return redirect('all_paket')