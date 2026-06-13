## Anggota Kelompok

| Nama Lengkap | NRP |
| --- | --- |
| Mahendra Agung Darmawan | 5053251032 |
| Umi Lailatul Khotimah | 5025241062 |
| Nashwa Aulia Putri Diansyah | 5025241064 |

## Link Youtube (Unlisted)
Link ditaruh di bawah ini
```
https://youtu.be/m-o_zk4wI5s
```

## Penjelasan Program

## Screenshot Hasil


**Deskripsi Pembagian Tugas:**
- **Mahendra (Backend & Networking):** Bertanggung jawab membangun server TCP Socket dari nol, mengimplementasikan protokol *WebSocket Handshake*, mengatur *multithreading* klien, serta sistem sinkronisasi/penyebaran data gambar dan obrolan secara *real-time*.
- **Umi (Frontend & UI/UX):** Merancang dan membuat antarmuka web (HTML/CSS/JS) bertema *Glassmorphism*, mengimplementasikan fungsi Core kanvas interaktif untuk menggambar, serta mendesain navigasi dan peringatan visual yang nyaman untuk pemain.
- **Nashwa (Game Logic & Integration):** Mengembangkan mesin dan alur permainan (mekanisme ronde, *timer*, bank kata), mengatur pembagian peran otomatis (*Drawer/Guesser*), kalkulasi papan skor, serta mengintegrasikan *state* data dari *backend* agar dieksekusi dengan tepat di layar klien.

## Deskripsi Game
Nge-nebakYuk adalah sebuah game *multiplayer online* berbasis web yang terinspirasi dari game populer Skribbl.io. Dalam game ini, para pemain akan bergiliran menjadi **Penggambar (Drawer)** dan **Penebak (Guesser)**. Penggambar harus memvisualisasikan sebuah kata benda secara *real-time* di kanvas yang disediakan, sementara Penebak berlomba-lomba menebak kata tersebut melalui kolom obrolan (chat).

Game ini dirancang murni menggunakan arsitektur *Client-Server* dengan **Raw TCP Sockets** dari sisi server, yang mana komunikasi jaringannya diterjemahkan secara manual menjadi *WebSocket Handshake* agar dapat diakses langsung tanpa hambatan melalui browser web klien.

## Fitur Utama
* **Global Room System (Min. 2 Pemain):** Game hanya akan dimulai jika ada minimal 2 pemain yang bergabung. Jika pemain terputus dan menyisakan 1 orang, permainan akan dijeda secara otomatis.
* **Real-Time Drawing & Chatting:** Coretan gambar dan tebakan disinkronisasikan secara langsung (real-time) ke seluruh ruangan.
* **Auto Role Assignment:** Rotasi giliran peran (Drawer/Guesser) otomatis ketika kata berhasil ditebak atau waktu habis.
* **Dynamic Scoreboard:** Papan peringkat yang akan terurut otomatis berdasarkan poin terbanyak setiap kali ada yang menjawab benar.
* **Ping / Latency Indicator:** Tampilan latensi koneksi jaringan (*ping*) secara langsung di pojok layar pemain.
* **Reconnect Handling:** Pemain yang terputus (disconnect) dapat masuk kembali dengan nama yang sama tanpa kehilangan skor poin mereka.

## Teknologi Stack
* **Backend:** Python 3 (Native Modules: `socket`, `threading`, `json`, `hashlib`, `base64`, `logging`)
* **Frontend:** HTML5 Canvas, CSS3 (Glassmorphism), Vanilla JavaScript (WebSockets API)
* **Protokol:** TCP Socket dengan *manual framing* ke protokol WebSocket (RFC 6455).

## Prasyarat Instalasi
* Python 3.7 atau lebih tinggi terinstall di komputer Server.
* Web Browser modern (Google Chrome, Firefox, Edge).
* (Opsional) Aplikasi [Ngrok](https://ngrok.com/) untuk kemudahan bermain beda jaringan (online jarak jauh).

## Setup Environment
Proyek ini tidak memerlukan instalasi library eksternal (seperti `pip install ...`), karena sepenuhnya menggunakan modul bawaan Python.
1. *Clone* atau unduh repository proyek ini ke laptop Anda.
2. Pastikan letak file terjaga (file `.py` berada di *root*, dan file web berada di dalam folder `web/`).

## Cara Menjalankan Game
### 1. Menjalankan Server Backend
Buka terminal/command prompt di dalam folder proyek, lalu jalankan:
```bash
python main.py
```
*(Server akan otomatis berjalan di latar belakang pada port `9999`)*

### 2. Menyambungkan Klien Web
Pemain dapat masuk ke dalam game menggunakan file `web/index.html`. Ada beberapa skenario jaringan:
* **Bermain Sendiri (Localhost):** Buka file `index.html` di browser Anda, masukkan nama, dan biarkan IP server di kotak isian tetap `127.0.0.1`.
* **Bermain via WiFi yang Sama:** Bagikan folder `web` ke teman-teman Anda. Mereka harus memasukkan **IPv4 Address** laptop Server Anda (contoh: `192.168.1.5`) di kotak isian IP Server.
* **Bermain via Jaringan Berbeda (Internet):** Gunakan Ngrok. Jalankan perintah `ngrok tcp 9999` di laptop Server. Minta teman-teman Anda untuk memasukkan alamat URL yang diberikan Ngrok beserta port-nya (contoh: `0.tcp.ap.ngrok.io:12345`) di kotak isian IP Server.

## Alur Permainan
1. **Join Phase:** Pemain memasukkan username dan IP server.
2. **Waiting Phase:** Jika pemain kurang dari 2, UI menampilkan kanvas kosong dengan notifikasi chat "Menunggu pemain lain".
3. **Drawing Phase:** Ketika ada minimal 2 pemain, sistem memilih satu orang sebagai *Drawer* dan memberikan 1 rahasia kata benda (dari 1000 kata unik). Waktu 45 detik mulai menghitung mundur.
4. **Guessing Phase:** Para *Guesser* menebak lewat chat box. Jawaban yang salah dikirim sebagai chat biasa. Jawaban benar tidak akan dibocorkan di chat, melainkan akan memberi pemenang +10 poin dan mengakhiri ronde saat itu juga.
5. **Timeout:** Jika waktu habis tanpa ada yang menebak benar, sistem akan membocorkan jawabannya, merotasi giliran ke pemain berikutnya, dan memulai ronde baru.

## Arsitektur Sistem
Sistem ini menggunakan arsitektur **Client-Server Multithreading**:
- `main.py`: Entri poin aplikasi yang bertugas melakukan `server.accept()` secara konstan dan melahirkan (*spawn*) satu *Thread Daemon* baru untuk setiap pemain yang terhubung.
- `protocol.py`: Logika krusial yang mengurus *handshake* protokol WebSocket serta *masking/unmasking* payload data raw TCP ke string JSON.
- `client_handler.py`: Modul untuk menangani logika interaksi setiap pemain seperti verifikasi nama, `join`, proses tebak kata, dan penanganan saat koneksi terputus.
- `network.py`: Sistem distribusi (*Broadcaster*) untuk menyebarkan pembaruan state (seperti timer dan data coretan X,Y) ke semua klien yang terhubung secara independen menggunakan *Mutex Lock*.
- `game.py`: Mesin state permainan yang mengatur index giliran, pengambilan kata acak, dan jalannya benang waktu (*timer thread*).

## Fitur Visual
* **Glassmorphism UI:** Penggunaan elemen latar transparan (*backdrop-filter*) yang memberikan kesan aplikasi modern layaknya Web3.
* **Canvas Interactive:** Papan gambar dinamis dengan goresan berbasis vektor responsif (*lineCap round*) yang menyesuaikan ukuran resolusi layar pengguna.
* **Color-Coded Status:** Pembedaan identitas peran ("Menggambar" biru muda neon, "Menebak" abu-abu putih) untuk kemudahan navigasi mata pemain.
* **Dynamic Warning Timer:** Panel waktu akan otomatis berubah menjadi warna merah (Red-Alert) ketika sisa waktu menyentuh di bawah angka 10 detik.

## Monitoring & Logging
Modul `logging` bawaan Python ditanamkan di sisi backend. Semua aktivitas krusial ditampilkan ke *console* dan sekaligus direkam di dalam berkas log `server.log`. Hal ini memudahkan identifikasi masalah dan audit aktivitas:
- Log Pemain Masuk (`JOIN`) dan Keluar.
- Log Seluruh Pesan Obrolan (untuk memantau riwayat tebakan).
- Log Kesalahan (Error/Exception).

## Troubleshooting
* **Error "Terputus dari server":** Pastikan skrip `main.py` masih berjalan. Jika menggunakan Ngrok, periksa apakah sesi Ngrok Anda belum kadaluwarsa (berubah port).
* **Coretan tidak muncul di layar pemain lain:** Periksa apakah Windows Defender Firewall memblokir lalu lintas di Port `9999`. Anda mungkin perlu melakukan *Allow App through Firewall*.
* **Skor ter-reset ketika Reconnect:** Pastikan pemain bergabung kembali menggunakan nama karakter (`username`) yang **sama persis** seperti sebelum mereka terputus (termasuk kecocokan huruf besar dan kecil).

## Dokumentasi
Seluruh kodingan backend dan frontend telah dipisahkan ke dalam beberapa file (*Separation of Concerns*) untuk memudahkan perbaikan dan pengembangan (*maintainability*). Referensi penulisan format konversi raw socket TCP menjadi WebSocket sepenuhnya diadaptasi dari dokumen standar resmi *IETF RFC 6455*.

## Kesimpulan
Proyek *TebakKata* telah sukses mengimplementasikan esensi arsitektur jaringan secara mendalam. Dimulai dari membangun fondasi TCP Socket secara manual, menaklukkan kerumitan format data WebSocket agar dimengerti *Web Browser*, mengatur kompetisi data melalui *Locking Mutex Multithreading*, hingga membangun mekanisme rekoneksi canggih, stabilitas ronde, dan pelacakan ping *real-time*. Keseluruhan sistem membuktikan pemahaman konkrit terkait pemanfaatan **Pemrograman Jaringan** tingkat lanjut.
