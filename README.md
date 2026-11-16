# Autonomous Knowledge Synthesizer (Second Brain Engine)

Sistem agregasi dan sintesis intelijen teknis harian berbasis GitHub Actions dan GitHub Pages. Berjalan otomatis di cloud tanpa perlu menyalakan laptop, dan dapat diakses langsung dari browser HP.

## 🚀 Cara Menghubungkan ke GitHub (Sekali Saja)

1. **Inisialisasi Git Lokal**:
   Buka terminal di folder ini (`c:\Users\FIGRIAL\Downloads\produktif`), lalu jalankan:
   ```bash
   git init
   git add .
   git commit -m "feat: initial autonomous knowledge synthesizer"
   git branch -M main
   ```

2. **Buat Repository di GitHub**:
   - Buka [github.com/new](https://github.com/new).
   - Beri nama repository, misal: `produktif` (pilih **Public** agar GitHub Pages gratis).
   - Jangan centang "Add a README file".
   - Klik **Create repository**.

3. **Hubungkan & Push**:
   ```bash
   git remote add origin https://github.com/<USERNAME-KAMU>/produktif.git
   git push -u origin main
   ```

4. **Aktifkan GitHub Pages (1 Klik)**:
   - Buka repo di GitHub -> Masuk ke tab **Settings** -> menu **Pages** (di sidebar kiri).
   - Pada bagian **Build and deployment** -> **Source**, pilih **GitHub Actions**.

Selesai! Sistem akan otomatis:
- Menjalankan workflow tiap hari jam 08:00 WIB.
- Mengompilasi catatan Markdown ke `knowledge_synthesizer/vault/`.
- Mempublikasikan dashboard live ke URL: `https://<USERNAME-KAMU>.github.io/produktif/`.
- Buka URL tersebut di browser HP dan bookmark / simpan ke Home Screen.
