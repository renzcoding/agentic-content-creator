# Milestone M02 — Local LLM Service dengan Ollama

## 1. Tujuan

Membangun layanan Python yang menghubungkan aplikasi dengan Ollama
sehingga agent dapat menggunakan Large Language Model (LLM) lokal.

## 2. Arsitektur

Alur komunikasi:

Aplikasi → generate_response() → HTTP Request → Ollama API
→ Model LLM → HTTP Response → Hasil teks

Endpoint:
http://localhost:11434/api/generate

Model dikonfigurasi melalui config/settings.py.

## 3. Implementasi

File utama: app/services/ollama_service.py

### Import

- json: mengubah data Python menjadi JSON dan membaca respons JSON.
- URLError: menangani kegagalan koneksi jaringan.
- Request dan urlopen: membuat serta menjalankan HTTP request.
- OLLAMA_MODEL: mengambil nama model dari konfigurasi aplikasi.

### Konstanta OLLAMA_URL

Menyimpan alamat endpoint Ollama agar alamat API tidak perlu ditulis
berulang kali di dalam fungsi.

### Fungsi generate_response(prompt: str) -> str

Tujuan:
Mengirim prompt ke Ollama dan mengembalikan hasil generasi sebagai teks.

Parameter:
- prompt (str): instruksi atau pertanyaan untuk model.

Return:
- str: teks yang dihasilkan model setelah spasi di awal dan akhir dihapus.

Alur eksekusi:

1. Memastikan prompt tidak kosong.
2. Membentuk payload JSON yang berisi model, prompt, dan stream=False.
3. Mengubah payload menjadi byte UTF-8 untuk dikirim melalui HTTP.
4. Membuat HTTP POST request dengan header Content-Type: application/json.
5. Mengirim request dengan timeout 120 detik.
6. Membaca respons dan mengubah JSON menjadi objek Python.
7. Mengubah URLError atau TimeoutError menjadi RuntimeError.
8. Mengembalikan teks dari field response.

Catatan:
Timeout 120 detik memberi waktu bagi model lokal untuk menghasilkan jawaban.
Jika Ollama tidak aktif atau koneksi gagal, fungsi menghasilkan RuntimeError.
Respons yang tidak memiliki field response dapat memunculkan KeyError;
penanganan respons tidak valid dapat ditambahkan pada milestone berikutnya.

## 4. Unit Testing

File: tests/test_ollama_service.py

Jalankan pengujian:

    python -m unittest tests.test_ollama_service -v

Hasil aktual:

    Ran 3 tests
    OK

### Test 1 — Prompt kosong

Memastikan prompt yang hanya berisi spasi ditolak menggunakan ValueError.

### Test 2 — Respons berhasil

Memalsukan respons HTTP dengan unittest.mock agar test tidak memerlukan
model Ollama yang berjalan. Test memastikan teks hasil dikembalikan
dengan spasi di awal dan akhir dihapus.

### Test 3 — Kegagalan koneksi

Memalsukan URLError dan memastikan fungsi mengubahnya menjadi RuntimeError
dengan pesan yang dapat dipahami.

## 5. Mengapa menggunakan mock?

Mock memungkinkan unit test memeriksa logika program secara cepat dan
konsisten tanpa bergantung pada server atau model AI sungguhan.

Mock tidak membuktikan bahwa seluruh integrasi Ollama selalu berhasil.
Pengujian integrasi nyata tetap diperlukan secara terpisah.

## 6. Troubleshooting

Jika test gagal:

1. Pastikan virtual environment aktif.
2. Jalankan test dari direktori utama repository.
3. Periksa pesan error dan baris kode yang disebutkan.
4. Pastikan mock sesuai dengan cara fungsi menggunakan urlopen.
5. Ulangi test setelah perbaikan.

Untuk memeriksa Ollama secara langsung:

    curl -s http://localhost:11434/api/tags

## 7. Kriteria Penyelesaian

- [x] Service dapat mengirim prompt ke Ollama.
- [x] Prompt kosong ditolak.
- [x] Respons teks dapat diekstrak.
- [x] Kegagalan koneksi ditangani.
- [x] Tiga unit test berhasil.
- [x] Catatan milestone dibuat.

## 8. Pengembangan Berikutnya

- Menambahkan validasi respons JSON yang tidak sesuai.
- Menambahkan konfigurasi timeout.
- Mengintegrasikan service dengan BaseAgent dan ProductManagerAgent.
- Menambahkan pengujian integrasi Ollama yang terpisah.


## 9. Regression Testing

Tanggal pengujian: 28 Oktober 2026

Perintah:

    python -m unittest discover -s tests -v

Hasil aktual:

    Ran 36 tests in 2.360s
    OK

Status: LULUS — seluruh 36 test berhasil.

Regression testing memastikan perubahan terbaru tidak menyebabkan
kegagalan pada fitur yang sudah memiliki unit test.

Catatan:
Hasil ini membuktikan seluruh test yang ditemukan berhasil dijalankan.
Hasil tersebut tidak otomatis menjamin semua skenario produksi telah
teruji; pengujian integrasi dan end-to-end tetap diperlukan.
