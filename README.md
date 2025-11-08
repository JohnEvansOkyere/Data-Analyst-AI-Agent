# 🤖 VexaAI Data Analyst Pro

**Professional Data Science Platform with MLOps Practices**

A comprehensive, production-ready data analysis application with advanced preprocessing, feature engineering, AI-powered insights, and persistent storage.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🚀 Features

### 🧹 **Advanced Data Cleaning**
- **9 Missing Data Strategies**: Drop, fill (mean/median/mode), forward/backward fill, interpolation
- **3 Outlier Detection Methods**: IQR, Z-score, Isolation Forest
- **Duplicate Removal**: Flexible duplicate handling
- **Text Cleaning**: Lowercase, whitespace, special character removal
- **Data Type Conversion**: Automated and manual type conversion

### ⚙️ **Feature Engineering**
- **Polynomial Features**: Create higher-order features
- **Interaction Features**: Generate feature interactions (multiply, divide, add, subtract)
- **Mathematical Transformations**: Log, sqrt, power transforms
- **Binning**: Quantile and uniform binning strategies
- **Date Feature Extraction**: Year, month, day, quarter, day of week, etc.
- **Aggregation Features**: Group-by aggregations
- **Rolling Window Features**: Time-series rolling statistics

### 📈 **Advanced Analytics**
- **Statistical Tests**: T-tests, ANOVA, Chi-square, normality tests
- **Correlation Analysis**: Pearson, Spearman, Kendall correlations
- **Multicollinearity Detection**: VIF calculations
- **Summary Statistics**: Comprehensive data profiling

### 🤖 **AI-Powered Insights**
- **Natural Language Queries**: Ask questions in plain English
- **Automatic SQL Generation**: Powered by Grok AI
- **Intelligent Insights**: AI-generated interpretations
- **Multiple AI Models**: Grok-4, Grok-2, Grok-Beta, Grok-Vision

### 💾 **Data Management (Supabase)**
- **Dataset Versioning**: Track all data transformations
- **Analysis History**: Save and retrieve past analyses
- **Audit Logging**: Complete activity tracking
- **Data Quality Reports**: Automated quality assessments
- **Multi-format Export**: CSV, Excel, Parquet, JSON, Feather

### 📊 **Interactive Visualizations**
- **Auto-generated Charts**: Histograms, scatter plots, box plots, heatmaps
- **Custom Visualizations**: Build your own charts
- **Interactive Plots**: Powered by Plotly
- **Export Capabilities**: Download charts and reports

### 🔐 **Security & Authentication**
- **User Management**: Admin panel for user control
- **Role-based Access**: Admin and user roles
- **Password Protection**: SHA-256 hashed passwords
- **Session Management**: Secure session handling
- **Audit Trails**: Complete activity logging

### 📊 **MLOps Features**
- **Comprehensive Logging**: Application, error, performance, audit logs
- **Performance Monitoring**: Track operation durations
- **Data Versioning**: Version control for datasets
- **Quality Metrics**: Automated data quality scoring
- **Error Tracking**: Detailed error logging and reporting

---

## 📁 Project Structure

```
VexaAI_Data_Analyst_Pro/
├── Home.py                          # Main application entry point
├── pages/                           # Streamlit pages
│   ├── 1_📂_Data_Upload.py         # Data upload and preview
│   ├── 2_🧹_Data_Cleaning.py       # Data cleaning and preprocessing
│   ├── 3_📈_Analysis_Insights.py   # Statistical analysis and AI queries
│   ├── 4_📊_Visualizations.py      # Interactive visualizations
│   ├── 5_🎛️_Dashboard.py           # Comprehensive dashboard
│   ├── 6_📁_Data_History.py        # Dataset history and versioning
│   └── 7_🔐_Admin_Panel.py         # User management
├── core/                            # Core business logic
│   ├── ml_engine.py                 # Grok AI integration
│   ├── auth.py                      # Authentication system
│   ├── data_cleaning.py             # Data cleaning operations
│   ├── feature_engineering.py       # Feature engineering
│   └── data_analysis.py             # Statistical analysis
├── database/                        # Database integration
│   └── supabase_manager.py          # Supabase operations
├── utils/                           # Utility functions
│   ├── logger.py                    # Logging system
│   └── helpers.py                   # Helper functions
├── config/                          # Configuration
│   └── settings.py                  # Application settings
├── logs/                            # Application logs
├── docs/                            # Documentation
├── tests/                           # Unit tests
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
├── .gitignore                       # Git ignore rules
└── README.md                        # This file
```

---

## 🛠️ Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager
- xAI API key (from [console.x.ai](https://console.x.ai))
- Supabase account (optional, from [supabase.com](https://supabase.com))

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/vexaai-data-analyst-pro.git
cd vexaai-data-analyst-pro
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
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your credentials
# - XAI_API_KEY: Your xAI API key
# - SUPABASE_URL: Your Supabase project URL (optional)
# - SUPABASE_ANON_KEY: Your Supabase anonymous key (optional)
```

### Step 5: Set Up Supabase (Optional)
If you want to use persistent storage and data versioning:

1. Create a free account at [supabase.com](https://supabase.com)
2. Create a new project
3. Run the SQL schema from `docs/supabase_schema.sql` in the SQL editor
4. Copy your project URL and anon key to `.env`

### Step 6: Run the Application
```bash
streamlit run Home.py
```

The application will open in your default browser at `http://localhost:8501`

---

## 🎯 Quick Start Guide

### 1. **First Login**
- Default credentials:
  - Username: `admin`
  - Password: `admin123`
- **⚠️ Change the password immediately after first login!**

### 2. **Configure API Keys**
- Navigate to any page
- In the sidebar, enter your xAI API key
- (Optional) Configure Supabase credentials

### 3. **Upload Data**
- Go to "📂 Data Upload" page
- Upload CSV or Excel file (up to 200MB)
- View data preview and quality metrics

### 4. **Clean Your Data**
- Navigate to "🧹 Data Cleaning" page
- Choose preprocessing operations:
  - Handle missing values
  - Remove duplicates and outliers
  - Scale features
  - Encode categories
  - Engineer new features

### 5. **Analyze & Visualize**
- Use "📈 Analysis & Insights" for:
  - AI-powered natural language queries
  - Statistical tests
  - Correlation analysis
- Explore "📊 Visualizations" for:
  - Interactive charts
  - Custom visualizations
  - Data distributions

### 6. **Export Results**
- Download cleaned datasets
- Export visualizations
- Save analysis reports
- Export in multiple formats (CSV, Excel, Parquet, JSON)

---

## 📖 User Guide

### Data Upload
1. Click "Browse files" or drag and drop
2. Supported formats: CSV, XLSX, XLS
3. Maximum file size: 200MB
4. Automatic data type detection
5. View data preview and quality score

### Data Cleaning Operations

#### Missing Data Handling
- **Drop Rows**: Remove rows with missing values
- **Drop Columns**: Remove columns exceeding missing threshold
- **Fill Mean/Median/Mode**: Fill with statistical measures
- **Fill Constant**: Fill with specific value
- **Forward/Backward Fill**: Propagate values
- **Interpolate**: Linear interpolation

#### Outlier Removal
- **IQR Method**: Interquartile range (recommended)
- **Z-Score**: Standard deviations from mean
- **Isolation Forest**: ML-based detection

#### Feature Scaling
- **Standard Scaler**: Mean=0, Std=1
- **Min-Max Scaler**: Scale to [0, 1]
- **Robust Scaler**: Robust to outliers
- **Max Abs Scaler**: Scale to [-1, 1]

#### Category Encoding
- **Label Encoding**: Convert to integers
- **One-Hot Encoding**: Create binary columns
- **Frequency Encoding**: Use value frequencies

### Feature Engineering

#### Polynomial Features
Create polynomial and interaction features up to specified degree.

#### Mathematical Transformations
- **Log Transform**: Natural log, log10, log2
- **Square Root**: Sqrt transformation
- **Power Transform**: Custom power exponents

#### Date Features
Automatically extract:
- Year, month, day
- Quarter, week
- Day of week
- Is weekend
- Is month start/end

### AI-Powered Queries

Ask questions in natural language:
- "What are the top 10 products by revenue?"
- "Show me monthly sales trends"
- "How many customers by region?"
- "Which products have low inventory?"
- "What's the average order value per customer segment?"

The system will:
1. Convert your question to SQL
2. Execute the query
3. Generate AI-powered insights
4. Visualize results

### Statistical Analysis

#### Available Tests
- **T-Test**: Compare means of two groups
- **ANOVA**: Compare means of multiple groups
- **Chi-Square**: Test independence of categorical variables
- **Normality Test**: Test if data is normally distributed
- **Correlation**: Measure relationship strength

---

## 🔧 Configuration

### Application Settings
Edit `config/settings.py` to customize:
- File size limits
- Supported file types
- Logging levels
- Cache settings
- Feature flags

### Environment Variables
Set in `.env` file:
```env
XAI_API_KEY=your_xai_key
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_key
APP_ENV=production
LOG_LEVEL=INFO
```

---

## 📊 Data Quality Scoring

The system automatically calculates a data quality score based on:
- **Completeness** (60% weight): Percentage of non-missing values
- **Uniqueness** (40% weight): Percentage of non-duplicate rows

**Score Interpretation:**
- **90-100%**: Excellent quality
- **80-89%**: Good quality
- **70-79%**: Fair quality
- **<70%**: Needs improvement

---

## 🔐 User Management

### Admin Functions
- Add new users
- Remove users (except admin)
- Change passwords
- View all users
- Deactivate/activate accounts

### User Roles
- **Admin**: Full access, user management
- **User**: Standard access, no admin functions

---

## 📝 Logging

The application maintains comprehensive logs:

### Log Types
1. **Application Log** (`logs/app.log`): General application events
2. **Error Log** (`logs/error.log`): Errors and exceptions
3. **Performance Log** (`logs/performance.log`): Operation timings
4. **Audit Log** (`logs/audit.log`): User activities and data access

### Log Rotation
- Maximum file size: 10MB
- Backup count: 5 files
- Automatic rotation and cleanup

---

## 🚀 Deployment

### Local Development
```bash
streamlit run Home.py
```

### Production Deployment

#### Streamlit Cloud
1. Push code to GitHub
2. Connect to Streamlit Cloud
3. Add secrets in dashboard
4. Deploy

#### Docker (Coming Soon)
```bash
docker build -t vexaai-analyst .
docker run -p 8501:8501 vexaai-analyst
```

#### Cloud Platforms
- AWS EC2/ECS
- Google Cloud Run
- Azure App Service
- Heroku

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**John Evans Okyere**
- Company: VexaAI
- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/yourprofile)

---

## 🙏 Acknowledgments

- **Streamlit**: For the amazing web framework
- **xAI**: For the powerful Grok AI models
- **Supabase**: For the excellent backend platform
- **Plotly**: For interactive visualizations
- **scikit-learn**: For machine learning tools
- **pandas**: For data manipulation

---

## 📞 Support

For issues, questions, or feature requests:
- 📧 Email: support@vexaai.com
- 🐛 GitHub Issues: [Report a bug](https://github.com/yourusername/vexaai-data-analyst-pro/issues)
- 💬 Discussions: [Join the discussion](https://github.com/yourusername/vexaai-data-analyst-pro/discussions)

---

## 🗺️ Roadmap

### Version 2.1 (Coming Soon)
- [ ] Real-time data streaming
- [ ] Scheduled reports
- [ ] Email notifications
- [ ] Advanced AutoML
- [ ] Custom model training
- [ ] API endpoints for integration

### Version 2.2
- [ ] Collaboration features
- [ ] Team workspaces
- [ ] Shared dashboards
- [ ] Comment system
- [ ] Version comparison

### Version 3.0
- [ ] Mobile app
- [ ] Real-time collaboration
- [ ] Advanced security features
- [ ] Enterprise features
- [ ] White-label options

---

**Built with ❤️ by VexaAI | © 2025**

⚡ Lightning fast • 🔒 Privacy first • 🧠 AI-powered • 📊 MLOps-ready
