from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from ..models import Paket, TrackingHistory

def cek_resi(request):
    paket_id = request.GET.get('id')
    
    context = {}

    if paket_id:
        try:
            paket = Paket.objects.get(id=paket_id)
            riwayat = paket.history.all().order_by('-timestamp')
            context['paket'] = paket
            context['riwayat'] = riwayat
        except Paket.DoesNotExist:
            context['error'] = "Paket dengan nomor resi tersebut tidak ditemukan."

    return render(request, 'tracking/cek_resi.html', context)

def cek_resi_api(request, paket_id):
    paket = get_object_or_404(Paket, id=paket_id)
    return JsonResponse({
        "id": str(paket.id),
        "status": paket.status,
        "pengirim": paket.pengirim.nama,
        "penerima": paket.penerima
    })