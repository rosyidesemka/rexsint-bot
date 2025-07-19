# 🔍 RexSint OSINT Bot

RexSint adalah bot Telegram OSINT (Open Source Intelligence) terdepan yang menyediakan akses cepat, akurat, dan mudah dipahami ke database kebocoran data. Bot ini dirancang dengan pengalaman pengguna premium, memanfaatkan AI untuk meringkas informasi kompleks, dan memiliki model bisnis berkelanjutan.

## 🌟 Fitur Utama

### 🔎 Pencarian Data
- **Email Search**: Cari berdasarkan alamat email
- **Name Search**: Cari berdasarkan nama lengkap
- **Password Search**: Cari berdasarkan kata sandi
- **IP Search**: Cari berdasarkan alamat IP (Premium)
- **Bulk Search**: Upload file untuk pencarian massal (Premium)
- **Combined Search**: Kombinasi multiple query

### 🤖 AI-Powered Features
- **AI Summary**: Ringkasan hasil pencarian menggunakan Google Gemini
- **Smart Analysis**: Analisis otomatis tingkat risiko
- **Contextual Insights**: Rekomendasi tindakan berdasarkan hasil

### 💎 Premium Features
- **Unlimited Searches**: Pencarian tanpa batas
- **Priority Support**: Dukungan prioritas
- **Advanced Analytics**: Analisis mendalam
- **Custom Reports**: Laporan kustom dalam format HTML

### 🛡️ Keamanan & Privasi
- **Encrypted Storage**: Penyimpanan data terenkripsi
- **Audit Trail**: Log aktivitas lengkap
- **Secure API**: Komunikasi API yang aman
- **Privacy First**: Tidak menyimpan data pencarian

## 📋 Persyaratan Sistem

### Software Requirements
- Python 3.9 atau lebih tinggi
- SQLite 3.x
- Git (untuk cloning repository)

### API Requirements
- Telegram Bot Token (dari @BotFather)
- LeakOSINT API Token
- Google Gemini API Key

### Hardware Requirements
- RAM: Minimal 512MB (Recommended 1GB+)
- Storage: Minimal 1GB free space
- Network: Koneksi internet stabil

## 🚀 Instalasi

### 1. Clone Repository
```bash
git clone https://github.com/your-username/rexsint-bot.git
cd rexsint-bot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Konfigurasi Bot
```bash
# Copy configuration template
cp config.ini.example config.ini

# Edit configuration dengan text editor
nano config.ini
```

### 4. Konfigurasi File
Edit file `config.ini` dengan informasi berikut:

```ini
[Telegram]
bot_token = YOUR_BOT_TOKEN_HERE

[APIs]
initial_leakosint_api_token = YOUR_LEAKOSINT_TOKEN_HERE
gemini_api_key = YOUR_GEMINI_API_KEY_HERE

[Admin]
admin_chat_id = YOUR_ADMIN_CHAT_ID_HERE

[Channel]
channel_id = @YOUR_CHANNEL_USERNAME
```

### 5. Inisialisasi Database
```bash
python -c "from core.database import DatabaseManager; dm = DatabaseManager('rex_sint_bot.db'); dm.init_db()"
```

### 6. Jalankan Bot
```bash
python main.py
```

## 🔧 Konfigurasi Detail

### Telegram Bot Setup
1. Buka [@BotFather](https://t.me/BotFather) di Telegram
2. Ketik `/newbot` dan ikuti instruksi
3. Salin Bot Token yang diberikan
4. Masukkan token ke `config.ini`

### LeakOSINT API Setup
1. Daftar di [LeakOSINT](https://leakosint.com/)
2. Dapatkan API token
3. Masukkan token ke `config.ini`

### Google Gemini API Setup
1. Buka [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Buat API key baru
3. Masukkan API key ke `config.ini`

### Channel Setup
1. Buat channel Telegram untuk bot
2. Dapatkan username atau ID channel
3. Masukkan ke `config.ini`

## 📁 Struktur Proyek

```
RexSint/
├── main.py                    # Entry point utama
├── config.ini                 # File konfigurasi
├── requirements.txt           # Dependencies
├── README.md                  # Dokumentasi
├── .gitignore                 # Git ignore rules
├── 
├── core/                      # Core components
│   ├── __init__.py
│   ├── database.py           # Database manager
│   ├── api_manager.py        # API integration
│   ├── auth.py               # Authentication
│   └── utils.py              # Utility functions
├── 
├── handlers/                  # Message handlers
│   ├── __init__.py
│   ├── start.py              # Start command
│   ├── search.py             # Search features
│   ├── admin.py              # Admin panel
│   ├── shop.py               # Payment system
│   └── settings.py           # User settings
├── 
├── models/                    # Data models
│   ├── __init__.py
│   ├── user.py               # User model
│   └── bot_status.py         # Bot status model
├── 
├── locales/                   # Multi-language support
│   ├── __init__.py
│   ├── localization.py       # Localization engine
│   ├── id.json               # Indonesian
│   └── en.json               # English
├── 
├── assets/                    # Static assets
│   ├── qris.png              # Payment QR code
│   ├── database_list.html    # Database catalog
│   └── log_history.json      # Activity logs
├── 
├── logs/                      # Log files
├── temp/                      # Temporary files
├── reports/                   # Generated reports
└── backups/                   # Database backups
```

## 🎯 Penggunaan Bot

### User Commands
- `/start` - Mulai menggunakan bot
- `/help` - Panduan penggunaan

### Admin Commands
- `/admin` - Panel admin
- `/activatetrial <user_id>` - Aktivasi trial
- `/generate <user_id>` - Generate token user
- `/setnewapi <token>` - Set API token baru

### Menu Navigation
- 🔎 **Fitur Pencarian Data** - Akses fitur pencarian
- ℹ️ **Informasi** - Lihat info akun dan statistik
- 🛒 **Toko** - Berlangganan dan aktivasi
- ⚙️ **Pengaturan** - Konfigurasi personal
- 📖 **Menu** - Panduan dan FAQ

## 🔐 Keamanan

### Best Practices
- Gunakan environment variables untuk API keys
- Aktifkan SSL/TLS untuk komunikasi
- Regularly update dependencies
- Monitor bot activity
- Backup database secara berkala

### Security Features
- Encrypted API communication
- Rate limiting protection
- User authentication
- Admin authorization
- Activity logging

## 🛠️ Development

### Setup Development Environment
```bash
# Clone dengan development branch
git clone -b development https://github.com/your-username/rexsint-bot.git

# Install development dependencies
pip install -r requirements-dev.txt

# Enable debug mode
export DEBUG=True

# Run with auto-reload
python main.py --debug
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Write comprehensive docstrings
- Add unit tests for new features

### Testing
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_handlers.py

# Run with coverage
python -m pytest --cov=core --cov=handlers
```

## 📊 Monitoring & Maintenance

### Health Checks
- Bot status monitoring
- API endpoint health
- Database performance
- Error rate tracking

### Maintenance Tasks
- Daily database cleanup
- Weekly backup creation
- Monthly security updates
- Quarterly performance review

### Logs
- Application logs: `logs/rexsint_bot.log`
- Error logs: `logs/errors.log`
- Activity logs: `assets/log_history.json`

## 🔧 Troubleshooting

### Common Issues

**Bot tidak merespons:**
- Periksa token bot di config.ini
- Pastikan bot aktif di @BotFather
- Cek koneksi internet

**API errors:**
- Verifikasi API tokens
- Cek kuota API
- Periksa format request

**Database errors:**
- Pastikan file database exist
- Cek permissions folder
- Jalankan database initialization

**Channel verification gagal:**
- Pastikan bot adalah admin di channel
- Verifikasi channel ID/username
- Cek visibility channel

### Debug Mode
```bash
# Aktifkan debug mode
export DEBUG=True
python main.py

# Atau edit config.ini
[Development]
debug_mode = true
```

## 🤝 Contributing

Kami welcome kontribusi dari community! Silakan:

1. Fork repository
2. Buat feature branch
3. Commit perubahan Anda
4. Push ke branch
5. Buat Pull Request

### Contribution Guidelines
- Ikuti code style yang ada
- Tambahkan tests untuk fitur baru
- Update dokumentasi
- Jelaskan perubahan di PR description

## 📝 License

Project ini dilisensikan di bawah MIT License - lihat file [LICENSE](LICENSE) untuk detail.

## 🙏 Acknowledgments

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram Bot API wrapper
- [LeakOSINT](https://leakosint.com/) - Data breach API provider
- [Google Gemini](https://deepmind.google/technologies/gemini/) - AI summarization
- [SQLite](https://sqlite.org/) - Database engine

## 📞 Support

Jika Anda mengalami masalah atau memiliki pertanyaan:

- 📧 Email: support@rexsint.com
- 💬 Telegram: @rexsint_support
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/rexsint-bot/issues)
- 📖 Wiki: [Project Wiki](https://github.com/your-username/rexsint-bot/wiki)

## 🚀 Deployment

### Production Deployment
1. Setup production server (Ubuntu/CentOS)
2. Install Python dan dependencies
3. Configure reverse proxy (Nginx)
4. Setup systemd service
5. Configure SSL certificate
6. Setup monitoring

### Docker Deployment
```bash
# Build image
docker build -t rexsint-bot .

# Run container
docker run -d --name rexsint-bot \
  -v ./config.ini:/app/config.ini \
  -v ./assets:/app/assets \
  rexsint-bot
```

### Environment Variables
```bash
export BOT_TOKEN="your_bot_token"
export LEAKOSINT_TOKEN="your_leakosint_token"
export GEMINI_API_KEY="your_gemini_key"
export ADMIN_CHAT_ID="your_admin_id"
export CHANNEL_ID="@your_channel"
```

---

**RexSint Bot** - Empowering OSINT Research with AI-Powered Intelligence 🔍✨