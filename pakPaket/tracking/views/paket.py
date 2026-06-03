from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..models import Paket, TrackingHistory
from django.db.models import Q

def cekResi(request):
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


def getAllPaket(request):
    if request.user.role == 'KURIR':
        if hasattr(request.user, 'kurir_profile'):
            profil_kurir = request.user.kurir_profile
            paket_list = Paket.objects.select_related('tipeLayanan').filter(
                Q(status='DIKEMAS') | Q(status='DIKIRIM', kurir=profil_kurir)
            ).order_by('created_at')
        else:
            paket_list = Paket.objects.none()
            
    elif request.user.role == 'CUSTOMER':
        if hasattr(request.user, 'customer_profile'):
            paket_list = Paket.objects.select_related('tipeLayanan').filter(pengirim=request.user.customer_profile).order_by('-created_at')
        else:
            paket_list = Paket.objects.none()
            
    elif request.user.role == 'ADMIN':
        paket_list = Paket.objects.select_related('tipeLayanan').all().order_by('-created_at')
    else:
        paket_list = Paket.objects.none()

    return render(request, 'tracking/paket/list_paket.html', {
        'paket_list': paket_list
    })

def detailPaket(request, paket_id):
    paket = get_object_or_404(
        Paket.objects.select_related('pengirim', 'tipeLayanan', 'transitGudang', 'kurir'), 
        id=paket_id
    )
    
    riwayat = paket.history.all().order_by('-timestamp')
    
    context = {
        'paket': paket,
        'riwayat': riwayat,
    }
    return render(request, 'tracking/paket/detail_paket.html', context)

