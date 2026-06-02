from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
import uuid
import random
import string

# Blok User
class User(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('KURIR', 'Kurir'),
        ('CUSTOMER', 'Customer'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    noHp = models.CharField(max_length=15, verbose_name="Nomor Telepon")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, verbose_name="Role")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Tanggal Bergabung")

class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    nama = models.CharField(max_length=100, verbose_name="Nama")
    alamat = models.CharField(max_length=255, verbose_name="Alamat")
    kota = models.CharField(max_length=20, verbose_name="Kota")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Tanggal Bergabung")

    def __str__(self):
        return self.nama

class Kurir(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='kurir_profile')
    idKurir = models.CharField(max_length=10, unique=True, verbose_name="ID Kurir")
    nama = models.CharField(max_length=100, verbose_name="Nama")
    kota = models.CharField(max_length=20, verbose_name="Kota")
    tipeKendaraan = models.CharField(max_length=20, verbose_name="Tipe Kendaraan")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Tanggal Bergabung")

    def __str__(self):
        return self.idKurir
    
# Blok Master Data
class TipeLayanan(models.Model):
    namaLayanan = models.CharField(max_length=50, unique=True, verbose_name="Nama Layanan")
    hargaPerKg = models.FloatField(verbose_name="Harga per Kg")
    estHari = models.IntegerField(verbose_name="Estimasi Hari")

    def __str__(self):
        return self.namaLayanan

class Gudang(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    namaGudang = models.CharField(max_length=50, unique=True, verbose_name="Nama Gudang")
    alamat = models.CharField(max_length=255, verbose_name="Alamat")
    kota = models.CharField(max_length=20, verbose_name="Kota")

    def __str__(self):
        return self.namaGudang

# Blok Paket
class Paket(models.Model):
    STATUS_CHOICES = [
        ('DIKEMAS', 'Dikemas'),
        ('DIKIRIM', 'Dikirim'),
        ('DITERIMA', 'Diterima'),
        ('DIBATALKAN', 'Dibatalkan'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    deskripsi = models.TextField(verbose_name="Deskripsi")
    berat = models.FloatField(verbose_name="Berat (kg)")
    dimensi = models.IntegerField(verbose_name="Dimensi (cm)")
    tipeLayanan = models.ForeignKey(TipeLayanan, on_delete=models.CASCADE, verbose_name="Tipe Layanan")
    ongkosKirim = models.FloatField(verbose_name="Ongkos Kirim")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DIKEMAS', verbose_name="Status")
    pengirim = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='paket_pengirim', verbose_name="Pengirim")
    penerima = models.CharField(max_length=100, verbose_name="Penerima")
    alamatPenerima = models.CharField(max_length=255, verbose_name="Alamat Penerima")
    kotaPenerima = models.CharField(max_length=20, verbose_name="Kota Penerima")
    noHpPenerima = models.CharField(max_length=15, verbose_name="Nomor Telepon Penerima")
    kurir = models.ForeignKey(Kurir, on_delete=models.SET_NULL, null=True, blank=True, related_name='paket_kurir', verbose_name="Kurir")
    transitGudang = models.ForeignKey(Gudang, on_delete=models.SET_NULL, null=True, blank=True, related_name='paket_gudang', verbose_name="Transit Gudang")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Tanggal Dibuat")
    edited_at = models.DateTimeField(null=True, verbose_name="Tanggal Diedit")
    resi = models.CharField(max_length=20, unique=True, blank=True, verbose_name="Nomor Resi")

    @property
    def estimasi_sampai(self):
        if self.created_at and self.tipeLayanan:
            return self.created_at + timedelta(days=self.tipeLayanan.estHari)
        return None

    def save(self, *args, **kwargs):
        if not self._state.adding:
            paket_lama = Paket.objects.get(pk=self.pk)
            
            if self.status != paket_lama.status and self.status in ['DIKIRIM', 'DITERIMA']:
                self.edited_at = timezone.now()
                
        if not self.resi:
            
            kota_input = self.kotaPenerima.upper().strip()
            
            kode_kota_map = {
                'JAKARTA': 'JKT',
                'SURABAYA': 'SBY',
                'MALANG': 'MLG',
                'BANDUNG': 'BDG',
                'SEMARANG': 'SMG',
                'YOGYAKARTA': 'JOG',
                'MEDAN': 'KNO',
                'MAKASSAR': 'UPG',
                'BALI': 'DPS',
                'BANJARMASIN': 'BJM',
            }

            kode_kota = kode_kota_map.get(kota_input)
            if not kode_kota:
                kota_bersih = kota_input.replace(" ", "")
                kode_kota = kota_bersih[:3] if len(kota_bersih) >= 3 else kota_bersih.ljust(3, 'X')

            kode_unik = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            self.resi = f"{kode_kota}-{kode_unik}"

        if not self.transitGudang and self.pengirim_id:
            kota_pengirim = self.pengirim.kota 
            
            if kota_pengirim:
                from .models import Gudang
                
                gudang_terdekat = Gudang.objects.filter(kota__iexact=kota_pengirim).first()
                
                if gudang_terdekat:
                    self.transitGudang = gudang_terdekat
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id} - {self.status}"
    
class TrackingHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    paket = models.ForeignKey(Paket, on_delete=models.CASCADE, related_name='history')
    kurir = models.ForeignKey(Kurir, on_delete=models.SET_NULL, null=True, blank=True, related_name='history_updates')

    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Waktu")
    lokasi = models.CharField(max_length=255, verbose_name="Lokasi")
    status = models.CharField(max_length=20, verbose_name="Status")
    notes = models.TextField(blank=True, null=True, verbose_name="Catatan")

    def __str__(self):
        return f"Update: {str(self.paket.id)[:8]} - {self.status}"