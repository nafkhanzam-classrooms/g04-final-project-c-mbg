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

- **protocol.py** – Implementasi protokol WebSocket (handshake, framing) serta logika permainan (penugasan peran, timer).
- **game.py** – Refaktor `protocol.py` dengan penambahan callback ketika timer habis.
- **words.py** – Memuat kamus kata dari `words.txt` dan menyediakan `get_random_word()` untuk pemilihan kata acak.
- **client_handler.py** – Menangani tiap koneksi klien: verifikasi nama, menerima & mengirim pesan JSON, mengatur alur permainan per pemain.
- **network.py** – Helper untuk broadcasting state (gambar, chat, timer) ke semua klien secara thread‑safe.
- **players.py** – Struktur data pemain dan fungsi manajemen skor serta status.
- **main.py** – Entry‑point server: membuat socket, menerima klien, mem‑spawn thread handler, menginisialisasi ronde pertama.
- **web/** – Frontend berbasis HTML, CSS & JavaScript yang membuka WebSocket ke server, menampilkan kanvas gambar, chat, timer, dan scoreboard.
- **words.txt** – Daftar kata default bila file tidak tersedia.

## Screenshot Hasil
<img width="878" height="277" alt="WhatsApp Image 2026-06-13 at 22 06 12" src="https://github.com/user-attachments/assets/72f53cd2-513c-462e-887a-b6188a22faa7" />
<img width="1600" height="698" alt="WhatsApp Image 2026-06-13 at 22 21 03" src="https://github.com/user-attachments/assets/8d650e78-556b-4a45-a5f9-d9b75467f9f9" />
<img width="959" height="458" alt="Screenshot 2026-06-13 220526" src="https://github.com/user-attachments/assets/809337c2-8e91-4537-9583-a4abc0ced65f" />
<img width="959" height="464" alt="Screenshot 2026-06-13 220851" src="https://github.com/user-attachments/assets/58775639-2c09-4aa1-8bb8-11cb56467ab0" />
<img width="956" height="466" alt="Screenshot 2026-06-13 222246" src="https://github.com/user-attachments/assets/4409bce9-d875-4236-becd-1534c92db77f" />
<img width="958" height="461" alt="Screenshot 2026-06-13 222537" src="https://github.com/user-attachments/assets/440358f8-182c-4963-8976-30719d3d8d70" />
<img width="1093" height="396" alt="WhatsApp Image 2026-06-13 at 22 24 10" src="https://github.com/user-attachments/assets/30d1db67-a87b-4c30-a83d-00e1f45a5572" />


