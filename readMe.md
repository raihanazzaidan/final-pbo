# 📦 pakPaket - Sistem Manajemen Logistik & Tracking

pakPaket adalah sebuah aplikasi web sistem manajemen logistik dan pelacakan (*tracking*) pengiriman barang berbasis Django. Aplikasi ini dirancang untuk memfasilitasi tiga peran pengguna utama: **Customer**, **Kurir**, dan **Admin** dengan alur kerja yang terintegrasi secara *real-time*.

Proyek ini dikembangkan sebagai pemenuhan Tugas Akhir Mata Kuliah Pemrograman Berorientasi Objek (PBO) di Program Studi Teknik Informatika, Universitas Negeri Surabaya.

---

## 👥 Anggota Kelompok 
* Velanisa Lutfiana (25051204025)
* Afnan Bagus Kurniawan (25051204078)
* Muhammad Raihan Azzaidan (25051204170)
* Any Aulia Putri (25051204228)

## ✨ Fitur Utama

* **Multi-Role Authentication:** Sistem *login* dan *register* kustom yang membedakan hak akses dan *dashboard* untuk Admin, Kurir, dan Pelanggan.
* **Smart Resi Generator:** Pembuatan nomor resi secara otomatis (contoh: `SBY-A4F89K2P`) berdasarkan kota tujuan pengiriman saat paket didaftarkan.
* **Kalkulator Ongkir:** Penghitungan otomatis ongkos kirim berdasarkan berat fisik dan harga tipe layanan/kg.
* **Real-time Tracking Timeline:** Pelacakan riwayat perjalanan paket dengan visualisasi *timeline* yang responsif.
* **Kurir Task Management:** Kurir dapat mengambil (*pick-up*) paket yang siap dikirim, menyelesaikan pesanan (konfirmasi penerimaan), maupun mengembalikan pesanan (retur paket).

## 🛠️ Teknologi yang Digunakan

* **Backend:** Django
* **Frontend:** HTML5, Tailwind CSS
* **Database:** MySQL

---

## 🎯 Implementasi 4 Konsep PBO

Proyek ini dirancang dengan arsitektur yang sangat berpegang teguh pada prinsip PBO murni, yang diwujudkan secara tegas di dalam struktur *Model* data:

1. **Abstraksi (Abstraction)**
   * Sistem menggunakan *Abstract Base Class* bernama `BaseModel` (`class Meta: abstract = True`). Class ini berfungsi sebagai cetak biru (*blueprint*) fundamental yang tidak pernah dibuat wujud objeknya secara langsung.
   * Menerapkan pemaksaan implementasi metode melalui *exception* `NotImplementedError` pada fungsi `get_info()`, memastikan semua class turunan memiliki standar fungsionalitas yang sama.

2. **Pewarisan (Inheritance)**
   * Menerapkan prinsip *Don't Repeat Yourself* (DRY). Seluruh entitas utama sistem seperti `Customer`, `Kurir`, `Paket`, dan `Gudang` adalah *Child Class* yang mewarisi langsung atribut dasar `id` (UUID), `created_at`, dan `updated_at` dari *Parent Class* (`BaseModel`).
   * *Class* `User` mewarisi seluruh kemampuan sistem autentikasi (*password hashing*, *session*, dll) dari `AbstractUser` bawaan Django.

3. **Enkapsulasi (Encapsulation)**
   * Mencegah modifikasi data sembarangan dari luar dengan menggunakan variabel tersembunyi (*private variable*) seperti `_berat` pada `Paket` dan `_hargaPerKg` pada `TipeLayanan`.
   * Akses dan modifikasi variabel tersebut dijembatani dengan ketat menggunakan *Decorator* **Getter** (`@property`) dan **Setter** (`@<variable>.setter`). Setter ini bertugas memvalidasi data, contohnya menolak *input* berat atau harga yang bernilai negatif sebelum diizinkan masuk ke *database*.

4. **Polimorfisme (Polymorphism)**
   * **Method Overriding (Data String):** Fungsi `get_info()` yang diwajibkan oleh class abstrak ditimpa (*override*) oleh masing-masing class turunan untuk menghasilkan *output* string yang spesifik menyesuaikan informasi identitas entitas tersebut.
   * **Method Overriding (Business Logic):** Menimpa fungsi bawaan `save()` pada *class* `Paket` untuk menyisipkan perilaku bentuk baru, yaitu logika pembuatan resi otomatis dan pembaruan pencatatan `edited_at` sebelum data secara permanen disimpan ke *database* (`super().save()`).

---

## 🚀 Cara Menjalankan Proyek Secara Lokal

Ikuti langkah-langkah di bawah ini untuk menjalankan aplikasi pakPaket:

**1. Clone repositori**
```bash
git clone https://github.com/raihanazzaidan/final-pbo
cd final-pbo
```

**2. Buat Virtual Environment (venv)**

```bash
python -m venv env
```

**3. Aktifkan venv**

* Untuk Mac/Linux:
```bash
source env/bin/activate
```


* Untuk Windows:
```bash
.\env\Scripts\activate
```



**4. Install Dependencies**

```bash
pip install -r requirements.txt
```

**5. Konfigurasi Database**

* Buka file `pakPaket/settings.py`.
* Pada bagian `DATABASES`, sesuaikan `USER` dan `PASSWORD` dengan konfigurasi MySQL milikmu.
* Buat database baru (kosong) di MySQL dengan nama `pakPaket`.
* Lakukan migrasi database dengan menjalankan perintah berikut:
```bash
python manage.py makemigrations
python manage.py migrate
```



**6. Buat Akun Superuser**
Ketik perintah di bawah ini dan ikuti instruksi yang muncul di terminal (disarankan menggunakan username: `superadmin`):

```bash
python manage.py createsuperuser
```

**7. Jalankan Server & Tambah Akun Admin**

```bash
python manage.py runserver
```

* Buka browser dan akses `http://127.0.0.1:8000/login`.
* Login menggunakan akun `superadmin` yang baru saja dibuat.
* Akses url `http://127.0.0.1:8000/adm/register` untuk mendaftarkan User baru dengan *role* **Admin**.

**8. Setup Data Master**

* Login sebagai **Admin** yang baru saja didaftarkan.
* Tambahkan data **Gudang**, **Tipe Layanan**, dan daftarkan akun **Kurir** melalui menu yang tersedia di Dashboard Admin.

**9. Skenario Penggunaan**

* **Customer:** Kembali ke halaman Login, klik "Daftar Sekarang" untuk membuat akun pelanggan, lalu login untuk mulai mengirim paket.
* **Kurir:** Login menggunakan akun kurir (yang telah dibuat oleh Admin) untuk melihat daftar paket dan memperbarui status pelacakan paket.

## 📸 Screenshots Program

Proyek ini memiliki 3 alur penggunaan, yakni sebagai customer, kurir, dan admin

1. **Admin**
   * 
   * 
   * 

2. **Customer**
   * 
   * 
   * 

3. **Kurir**
   * 
   * 
   * 