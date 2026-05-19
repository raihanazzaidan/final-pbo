from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Customer, Kurir, TipeLayanan, Gudang, Paket, TrackingHistory

admin.site.register(User, UserAdmin)
admin.site.register(Customer)
admin.site.register(Kurir)
admin.site.register(TipeLayanan)
admin.site.register(Gudang)

@admin.register(Paket)
class PaketAdmin(admin.ModelAdmin):
    list_display = ('id', 'pengirim', 'penerima', 'status', 'created_at')
    list_filter = ('status', 'tipeLayanan')
    search_fields = ('id', 'penerima', 'resi')

@admin.register(TrackingHistory)
class TrackingHistoryAdmin(admin.ModelAdmin):
    list_display = ('paket', 'status', 'lokasi', 'timestamp')
    list_filter = ('status',)