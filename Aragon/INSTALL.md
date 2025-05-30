# 🚀 Installation Guide - Telegram Excel Bot
Complete installation guide for **Telegram Excel 
Management Bot**.
## 📋 Table of Contents
- [Quick Start](#-quick-start) - [Manual 
Installation](#-manual-installation) - 
[Platform-Specific 
Instructions](#-platform-specific-instructions) - 
[Configuration](#-configuration) - 
[Troubleshooting](#-troubleshooting)
## ⚡ Quick Start
### 🎯 One-Command Setup (Linux/Mac)
```bash git clone 
https://github.com/mohsen9090/telegram-excel-bot.git 
&& cd telegram-excel-bot && chmod +x 
launch_bot.sh && ./launch_bot.sh ```
### 🎯 One-Command Setup (Windows)
```cmd git clone 
https://github.com/mohsen9090/telegram-excel-bot.git 
&& cd telegram-excel-bot && launch_bot.bat ```
## 📦 Manual Installation
### Step 1: Clone Repository
```bash git clone 
https://github.com/mohsen9090/telegram-excel-bot.git 
cd telegram-excel-bot ```
### Step 2: Create Virtual Environment
```bash
# Linux/Mac
python3 -m venv venv source venv/bin/activate
# Windows
python -m venv venv venv\Scripts\activate ```
### Step 3: Install Dependencies
```bash
# From requirements.txt (recommended)
pip install -r requirements.txt
# Manual installation
pip install python-telegram-bot>=20.0 
pandas>=1.5.0 openpyxl>=3.0.0 xlrd>=2.0.0 
requests>=2.28.0 ```
### Step 4: Configure Bot Token
Edit `config.py`: ```python TOKEN = 
"1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ" # Your 
actual bot token ```
### Step 5: Run the Bot
```bash python run_bot.py ```
## 🖥️ Platform-Specific Instructions
### 🐧 Linux (Ubuntu/Debian)
```bash
# Update system packages
sudo apt update sudo apt install python3 
python3-pip python3-venv git
# Clone and setup
git clone 
https://github.com/mohsen9090/telegram-excel-bot.git 
cd telegram-excel-bot chmod +x launch_bot.sh 
./launch_bot.sh ```
### 🍎 macOS
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL 
https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
# Install Python and Git
brew install python git
# Clone and setup
git clone 
https://github.com/mohsen9090/telegram-excel-bot.git 
cd telegram-excel-bot chmod +x launch_bot.sh 
./launch_bot.sh ```
### 🪟 Windows
```cmd REM Install Python from https://python.org 
(3.8+ required) REM Install Git from 
https://git-scm.com REM Clone and setup git clone 
https://github.com/mohsen9090/telegram-excel-bot.git 
cd telegram-excel-bot launch_bot.bat ```
### 🐳 Docker (Optional)
```bash
# Build Docker image
docker build -t telegram-excel-bot .
# Run container
docker run -d --name excel-bot telegram-excel-bot 
```
## ⚙️ Configuration
### 🤖 Getting Bot Token
1. Open Telegram and search for `@BotFather` 2. 
Start chat and send `/newbot` 3. Follow 
instructions to create your bot 4. Copy the token 
and paste it in `config.py`
### 📝 Environment Variables (Optional)
```bash
# Copy example file
cp .env.example .env
# Edit .env file
nano .env # Linux/Mac notepad .env # Windows ```
### 🎨 Default Configuration
```python
# File paths
EXCEL_FILE = "data.xlsx" FIELDS_FILE = 
"fields.json" LOG_FILE = "bot.log"
# Display limits
MAX_DISPLAY_RECORDS = 10 MAX_SEARCH_RESULTS = 5
# Default theme
DEFAULT_THEME = "blue" ```
## 🛠️ Development Setup
### 📚 Install Development Dependencies
```bash pip install -r requirements-dev.txt ```
### 🧪 Run Tests
```bash pytest tests/ ```
### 📝 Code Formatting
```bash black . isort . flake8 . ```
## 🔧 Troubleshooting
### ❌ Common Issues
#### Python Not Found
```bash
# Linux/Mac
sudo apt install python3 # Ubuntu/Debian brew 
install python # macOS
# Windows Download from https://python.org
```
#### Permission Denied (Linux/Mac)
```bash chmod +x launch_bot.sh sudo chown 
$USER:$USER -R . ```
#### Virtual Environment Issues
```bash
# Remove and recreate
rm -rf venv python3 -m venv venv source 
venv/bin/activate pip install -r requirements.txt 
```
#### Import Errors
```bash
# Upgrade pip and reinstall
pip install --upgrade pip pip install 
--force-reinstall -r requirements.txt ```
#### Bot Token Issues
- Verify token is correct (no extra spaces) - 
Check if bot is active in BotFather - Ensure 
token is properly set in config.py
### 📊 System Requirements
#### Minimum Requirements
- **OS**: Linux, macOS, Windows 10+ - **Python**: 
3.8+ - **RAM**: 512 MB - **Storage**: 100 MB - 
**Network**: Internet connection
#### Recommended Requirements
- **OS**: Latest version - **Python**: 3.10+ - 
**RAM**: 1 GB+ - **Storage**: 1 GB+ - 
**Network**: Stable internet
### 📱 Testing Installation
#### Quick Test
```bash python3 -c "import telegram, pandas, 
openpyxl; print('✅ All imports successful')" ```
#### Bot Connectivity Test
```bash python3 -c " from telegram import Bot bot 
= Bot('YOUR_TOKEN_HERE') print(f'✅ Bot 
connected: {bot.get_me().first_name}') " ```
## 🆘 Getting Help
### 📖 Documentation
- [README.md](README.md) - Project overview - 
[API Documentation](docs/api.md) - Technical 
details - [User Guide](docs/user_guide.md) - 
Usage instructions
### 💬 Community Support
- **GitHub Issues**: [Report 
bugs](https://github.com/mohsen9090/telegram-excel-bot/issues) 
- **GitHub Discussions**: [Ask 
questions](https://github.com/mohsen9090/telegram-excel-bot/discussions) 
- **Email**: mohsen9090@gmail.com
### 🔍 Debug Mode
```python
# Enable debug logging in config.py
LOG_LEVEL = "DEBUG" ```
### 📋 Log Analysis
```bash
# View recent logs
tail -f bot.log
# Search for errors
grep "ERROR" bot.log ```
## 🚀 Production Deployment
### 🌐 VPS Deployment
```bash
# Install as service (Linux)
sudo cp telegram-excel-bot.service 
/etc/systemd/system/ sudo systemctl enable 
telegram-excel-bot sudo systemctl start 
telegram-excel-bot ```
### ☁️ Cloud Deployment
- **Heroku**: See `Procfile` and `runtime.txt` - 
**Railway**: Auto-deploy from GitHub - 
**DigitalOcean**: Use Docker container - **AWS**: 
EC2 or Lambda deployment
### 🔒 Security Considerations
- Keep bot token secure - Use environment 
variables in production - Enable logging for 
monitoring - Regular backups of data files - 
Firewall configuration for VPS --- **🎉 
Installation Complete!** Your Telegram Excel Bot 
is ready to use. Start by sending `/start` to 
your bot in Telegram.
For more help, visit: [GitHub Repository](https://github.com/mohsen9090/telegram-excel-bot)
