# PuniBOT
Bot otomatis untuk platform Puni/Uniquid yang membantu menyelesaikan tugas harian dan menjawab kuis secara otomatis.

## 🎯 Daftar Puni/Uniquid
Silahkan klik link dibawah ini untuk mendaftar:
[PuniBOT](https://t.me/uniquidpunibot/uniquid?startapp=900266905)

## 🚀 Fitur
- Login otomatis menggunakan Telegram initData
- Menyelesaikan tugas harian secara otomatis
- Menjawab kuis dengan jawaban acak
- Sistem token management
- Mendukung multiple akun
- Colorized output di console
- Auto refresh setiap 1 Jam

## 📋 Persyaratan
- Python 3.7+
- Package yang tercantum di `requirements.txt`

## 🔧 Instalasi
1. Clone repository ini
```bash
git clone https://github.com/syns4033/PuniBOT.git
cd PuniBOT
```

2. Install dependencies yang dibutuhkan
```bash
pip install -r requirements.txt
```

3. Buat file `data.txt` 
```
query_id=
user=
```

## 🎮 Penggunaan
1. Pastikan file `data.txt` sudah berisi initData yang valid
2. Jalankan script dengan perintah:
```bash
python bot.py
```

## 📝 Format data.txt
File `data.txt` harus berisi initData dari Telegram bot dalam format:
```
query_id=
user=
```
Setiap baris mewakili satu akun. Anda bisa menambahkan multiple akun dengan format yang sama di baris baru.

## ⚙️ Konfigurasi
Bot akan secara otomatis:
- Menyimpan token di file `token.json`
- Refresh setiap 1 Jam
- Menunggu 1-3 detik antara setiap request
- Selalu memilih jawaban pertama untuk kuis

## 📊 Output
Bot akan menampilkan informasi seperti:
- Status login
- Progress tugas
- Point yang didapat
- Hasil kuis
- Peringkat
- Point bulanan

## ⚠️ Disclaimer
Script ini dibuat untuk tujuan edukasi. Penggunaan bot mungkin melanggar Terms of Service dari platform. Gunakan dengan risiko sendiri.

## 🤝 Kontribusi
Kontribusi selalu diterima. Untuk perubahan besar, harap buka issue terlebih dahulu untuk mendiskusikan apa yang ingin Anda ubah.

## 💝 Donasi
Jika Anda merasa terbantu dengan bot ini, Anda bisa memberikan donasi ke:

USDT (TRC20): `TA6RvgjTaJRy6birB78gyJ9abiEhcPurGL`

## 📄 Lisensi
[MIT](https://choosealicense.com/licenses/mit/)