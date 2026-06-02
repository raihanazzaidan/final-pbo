from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..models import User, Customer, Kurir

def loginView(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        username_input = request.POST.get('username')
        password_input = request.POST.get('password')

        user = authenticate(request, username=username_input, password=password_input)

        if user is not None:
            login(request, user)
            
            if user.role == 'ADMIN':
                return redirect('admin_dashboard')
            elif user.role == 'KURIR':
                return redirect('index')
            elif user.role == 'CUSTOMER':
                return redirect('index')
        else:
            messages.error(request, 'Username atau password salah. Silakan coba lagi.')
            return render(request, 'tracking/auth/login.html', {'username_value': username_input})
    return render(request, 'tracking/auth/login.html')


def customerRegister(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        username_input = request.POST.get('username')
        email_input = request.POST.get('email')
        password_input = request.POST.get('password')
        nama_input = request.POST.get('nama')
        alamat_input = request.POST.get('alamat')
        kota_input = request.POST.get('kota')
        noHp_input = request.POST.get('noHp')

        if User.objects.filter(username=username_input).exists():
            messages.error(request, 'Username sudah digunakan. Gunakan username lain.')
            return render(request, 'tracking/auth/register.html', {'form_data': request.POST})
        
        try:
            user = User.objects.create_user(
                username=username_input,
                email=email_input,
                password=password_input,
                noHp=noHp_input,
                role='CUSTOMER'
            )

            Customer.objects.create(
                user=user,
                nama=nama_input,
                alamat=alamat_input,
                kota=kota_input
            )

            messages.success(request, 'Registrasi berhasil! Silakan login.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan saat registrasi: {str(e)}')
            return render(request, 'tracking/auth/register.html', {'form_data': request.POST})
    return render(request, 'tracking/auth/register.html')

@login_required(login_url='login')
def logoutView(request):
    logout(request)
    messages.info(request, 'Anda telah berhasil logout.')
    return redirect('login')

@login_required(login_url='login')
def adminRegister(request):
    if request.user.username != 'superadmin':
        messages.error(request, 'Akses ditolak! Hanya superadmin yang dapat membuat akun admin baru.')
        return redirect('index')
    
    if request.method == 'POST':
        username_input = request.POST.get('username')
        email_input = request.POST.get('email')
        password_input = request.POST.get('password')

        if User.objects.filter(username=username_input).exists():
            messages.error(request, 'Username sudah digunakan. Gunakan username lain.')
            return render(request, 'tracking/auth/adminRegister.html', {'form_data': request.POST})
        
        try:
            user = User.objects.create_user(
                username=username_input,
                email=email_input,
                password=password_input,
                role='ADMIN'
            )

            messages.success(request, 'Registrasi berhasil! Silakan login.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan saat registrasi: {str(e)}')
            return render(request, 'tracking/auth/adminRegister.html', {'form_data': request.POST})
    return render(request, 'tracking/auth/adminRegister.html')

def kurirRegister(request):
    if request.user.username != 'superadmin' and request.user.role != 'ADMIN':
        messages.error(request, 'Akses ditolak! Hanya superadmin yang dapat membuat akun kurir baru.')
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        username_input = request.POST.get('username')
        email_input = request.POST.get('email')
        password_input = request.POST.get('password')
        nama_input = request.POST.get('nama')
        noHp_input = request.POST.get('noHp')

        if User.objects.filter(username=username_input).exists():
            messages.error(request, 'Username sudah digunakan. Gunakan username lain.')
            return render(request, 'tracking/auth/kurirRegister.html', {'form_data': request.POST})
        
        try:
            user = User.objects.create_user(
                username=username_input,
                email=email_input,
                password=password_input,
                noHp=noHp_input,
                role='KURIR'
            )

            Kurir.objects.create(
                user=user,
                nama=nama_input
            )

            messages.success(request, 'Registrasi berhasil! Silakan login.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan saat registrasi: {str(e)}')
            return render(request, 'tracking/auth/kurirRegister.html', {'form_data': request.POST})
    return render(request, 'tracking/auth/kurirRegister.html')