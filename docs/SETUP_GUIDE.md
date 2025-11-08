# 🚀 VexaAI Data Analyst Pro - Complete Setup Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [xAI API Setup](#xai-api-setup)
4. [Supabase Setup](#supabase-setup)
5. [Running the Application](#running-the-application)
6. [First-Time Setup](#first-time-setup)
7. [Testing](#testing)
8. [Deployment](#deployment)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- **Python 3.9+** - [Download Python](https://www.python.org/downloads/)
- **pip** (comes with Python)
- **Git** - [Download Git](https://git-scm.com/downloads)

### Required Accounts
- **xAI Account** - [Sign up at console.x.ai](https://console.x.ai)
- **Supabase Account** (Optional) - [Sign up at supabase.com](https://supabase.com)

---

## Installation

### Step 1: Clone the Repository

```bash
# Using Git
git clone https://github.com/yourusername/vexaai-data-analyst-pro.git
cd vexaai-data-analyst-pro

# Or download and extract ZIP file
# Then navigate to the folder
cd VexaAI_Data_Analyst_Pro
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note:** This may take a few minutes as it installs all dependencies.

---

## xAI API Setup

### Get Your xAI API Key

1. **Visit**: [https://console.x.ai](https://console.x.ai)
2. **Sign Up/Login**: Create an account or log in
3. **Navigate to API Keys**: Click on "API Keys" in the sidebar
4. **Create New Key**: Click "Create API Key"
5. **Copy Key**: Save the API key securely (starts with `xai-`)

### Add API Key to Application

**Option 1: Environment Variable (Recommended)**
```bash
# Create .env file
cp .env.example .env

# Edit .env and add your key
XAI_API_KEY=xai-your-actual-api-key-here
```

**Option 2: Enter in Application**
- Start the application
- Enter API key in the sidebar
- Will be saved in session (not persistent)

---

## Supabase Setup

### Create Supabase Project

1. **Visit**: [https://supabase.com](https://supabase.com)
2. **Sign Up/Login**: Create account or log in
3. **Create New Project**:
   - Click "New Project"
   - Choose organization
   - Enter project name
   - Set strong database password (save it!)
   - Choose region closest to your users
   - Click "Create new project"

4. **Wait**: Project creation takes 2-3 minutes

### Get Supabase Credentials

1. **Navigate to Settings**:
   - Click on project
   - Go to "Settings" → "API"

2. **Copy Credentials**:
   - **Project URL**: Copy the URL
   - **anon public key**: Copy the key

3. **Add to Environment**:
```bash
# Edit .env file
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
```

### Run Database Schema

1. **Navigate to SQL Editor**:
   - In Supabase dashboard
   - Click "SQL Editor" in sidebar
   - Click "New Query"

2. **Copy Schema**:
   - Open `docs/supabase_schema.sql`
   - Copy entire contents

3. **Execute Schema**:
   - Paste into SQL Editor
   - Click "Run" or press Ctrl+Enter
   - Wait for confirmation

4. **Verify Tables**:
   - Go to "Table Editor"
   - You should see 6 tables:
     - datasets
     - data_versions
     - analysis_history
     - audit_logs
     - data_quality_reports
     - users (optional)

---

## Running the Application

### Local Development

```bash
# Make sure virtual environment is activated
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Run Streamlit
streamlit run Home.py

# Application will open at http://localhost:8501
```

### Custom Port

```bash
streamlit run Home.py --server.port 8502
```

### Custom Host (for network access)

```bash
streamlit run Home.py --server.address 0.0.0.0
```

---

## First-Time Setup

### 1. Initial Login

**Default Credentials:**
- Username: `admin`
- Password: `admin123`

### 2. Change Admin Password

**IMPORTANT: Change immediately!**

1. After login, go to sidebar
2. Click "👨‍💼 Admin Panel"
3. Expand "🔐 Change Password"
4. Enter:
   - Current password: `admin123`
   - New password: (strong password)
   - Confirm new password
5. Click "Change Password"

### 3. Create Additional Users

1. In Admin Panel
2. Expand "➕ Add New User"
3. Enter:
   - Username
   - Password
   - Role (user or admin)
4. Click "Add User"

### 4. Configure API Keys

1. Go to any page
2. In sidebar, enter xAI API key
3. Select preferred AI model
4. (Optional) Configure Supabase

### 5. Test Upload

1. Go to "📂 Data Upload"
2. Upload a sample CSV file
3. Verify data loads correctly
4. Check data quality metrics

---

## Testing

### Quick Test

```python
# Test Supabase connection
python -c "from database.supabase_manager import get_supabase_manager; db = get_supabase_manager(); print('Connected!' if db.is_connected() else 'Not connected')"

# Test logging
python -c "from utils.logger import get_logger; logger = get_logger('test'); logger.info('Test log'); print('Logging works!')"
```

### Sample Data

Use these sample datasets to test:
- **Iris Dataset**: [Download here](https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data)
- **Titanic Dataset**: [Download from Kaggle](https://www.kaggle.com/c/titanic/data)

---

## Deployment

### Streamlit Cloud (Recommended)

1. **Push to GitHub**:
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Deploy to Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select repository and branch
   - Main file: `Home.py`
   - Click "Deploy"

3. **Add Secrets**:
   - In Streamlit Cloud dashboard
   - Go to "Settings" → "Secrets"
   - Add your environment variables:
```toml
XAI_API_KEY = "your-xai-key"
SUPABASE_URL = "your-supabase-url"
SUPABASE_ANON_KEY = "your-supabase-key"
```

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "Home.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t vexaai-analyst .
docker run -p 8501:8501 --env-file .env vexaai-analyst
```

### AWS EC2 Deployment

1. **Launch EC2 Instance**:
   - Amazon Linux 2 or Ubuntu
   - t2.medium or larger
   - Open port 8501

2. **Connect and Setup**:
```bash
ssh -i your-key.pem ec2-user@your-instance-ip

# Update system
sudo yum update -y  # Amazon Linux
# or
sudo apt update && sudo apt upgrade -y  # Ubuntu

# Install Python and Git
sudo yum install python3 git -y

# Clone and setup
git clone your-repo-url
cd VexaAI_Data_Analyst_Pro
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file with your credentials

# Run with nohup
nohup streamlit run Home.py --server.port 8501 --server.address 0.0.0.0 &
```

3. **Setup Nginx** (Optional, for custom domain):
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

---

## Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

#### 2. Supabase Connection Failed
- Verify URL and key in .env
- Check internet connection
- Verify Supabase project is active
- Check firewall/proxy settings

#### 3. xAI API Errors
- Verify API key is correct
- Check API quota/limits
- Ensure proper format (starts with xai-)

#### 4. Port Already in Use
```bash
# Use different port
streamlit run Home.py --server.port 8502
```

#### 5. Module Not Found
```bash
# Ensure virtual environment is activated
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

### Error Logs

Check logs for detailed error information:
```bash
# View application log
cat logs/app.log

# View error log
cat logs/error.log

# View last 50 lines
tail -n 50 logs/app.log
```

### Getting Help

1. **Check Logs**: `logs/` directory
2. **GitHub Issues**: [Report a bug](https://github.com/yourusername/vexaai-data-analyst-pro/issues)
3. **Email**: support@vexaai.com
4. **Documentation**: Read README.md

---

## Performance Optimization

### For Large Datasets

1. **Increase Memory**:
```bash
streamlit run Home.py --server.maxUploadSize 500
```

2. **Use Data Sampling**:
- Sample large datasets before processing
- Use pagination for display

3. **Enable Caching**:
```python
# In config/settings.py
ENABLE_CACHING = True
CACHE_TTL_SECONDS = 3600
```

### Database Optimization

1. **Index Creation**: Already included in schema
2. **Query Optimization**: Use appropriate filters
3. **Cleanup Old Data**: Regularly archive old records

---

## Security Best Practices

1. **Change Default Password**: Immediately!
2. **Use Strong Passwords**: Minimum 8 characters, mixed case, numbers, special chars
3. **Secure API Keys**: Never commit to Git
4. **Regular Updates**: Keep dependencies updated
5. **Enable HTTPS**: Use SSL/TLS in production
6. **Backup Database**: Regular Supabase backups
7. **Monitor Logs**: Check audit logs regularly

---

## Maintenance

### Regular Tasks

**Weekly:**
- Check error logs
- Review audit logs
- Monitor disk space

**Monthly:**
- Update dependencies
- Database cleanup
- Review user accounts

**Quarterly:**
- Security audit
- Performance review
- Feature updates

### Update Dependencies

```bash
pip list --outdated
pip install --upgrade package-name
```

### Backup

**Local Files:**
```bash
# Backup logs and data
tar -czf backup-$(date +%Y%m%d).tar.gz logs/ data/ authorized_users.json
```

**Supabase:**
- Automatic daily backups
- Manual backup from dashboard
- Export tables as CSV

---

## Next Steps

1. ✅ **Complete Setup**: Follow this guide
2. 📚 **Read Documentation**: Check README.md
3. 🧪 **Test Features**: Try all pages
4. 👥 **Add Users**: Create team accounts
5. 📊 **Upload Data**: Start analyzing
6. 🚀 **Deploy**: Move to production
7. 📈 **Monitor**: Track usage and performance

---

**Need Help?** Contact: support@vexaai.com

**Built with ❤️ by VexaAI | © 2025**
