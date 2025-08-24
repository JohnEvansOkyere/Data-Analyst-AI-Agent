# 🤖 VexaAI Data Analyst

A powerful data analysis application that allows you to query data using natural language, powered by Groq AI. The application features user authentication and is separated into modular components for better maintainability.

## 🚀 Features

- **🔐 User Authentication**: Secure login system with admin panel for user management
- **🤖 AI-Powered Queries**: Convert natural language questions into SQL queries using Groq AI
- **📊 Data Analysis**: Upload CSV/Excel files and get instant insights
- **📈 Interactive Visualizations**: Beautiful charts and data profiling
- **⚡ Lightning Fast**: Powered by Groq's ultra-fast AI models
- **🆓 Completely Free**: No credit card required, 14,400 requests/day free

## 📁 Project Structure

```
Data_Analysis_AI_Agent/
├── streamlit_app.py      # Main Streamlit UI application
├── ml_engine.py          # ML/AI logic and data processing
├── auth.py              # Authentication system
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── authorized_users.json # User database (created automatically)
```

### File Descriptions

- **`streamlit_app.py`**: Contains all the Streamlit UI components, styling, and user interface logic
- **`ml_engine.py`**: Contains the GroqClient class and all data processing functions
- **`auth.py`**: Handles user authentication, admin panel, and user management
- **`requirements.txt`**: Lists all required Python packages

## 🛠️ Installation

1. **Clone or download the project**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   streamlit run streamlit_app.py
   ```

## 🔐 Authentication

### Default Admin Credentials
- **Username**: `admin`
- **Password**: `admin123`

⚠️ **Important**: Change the default password after first login!

### Admin Features
- Add new users
- Remove users
- Change passwords
- View all users and their status

## 🎯 How to Use

### 1. Get Free Groq API Key
1. Visit [console.groq.com](https://console.groq.com)
2. Sign up with your email (completely free!)
3. Go to API Keys section
4. Click "Create API Key"
5. Copy the API key

### 2. Login to the Application
1. Use the default admin credentials or ask your admin for access
2. Enter your username and password
3. Click "Login"

### 3. Configure Groq API
1. Enter your Groq API key in the sidebar
2. Select your preferred AI model
3. The application will show "Ready to analyze"

### 4. Upload and Analyze Data
1. Upload a CSV or Excel file
2. View data preview and statistics
3. Ask questions in natural language
4. Get instant insights and visualizations

## 💡 Example Questions

Try these sample queries:
- "What are the top 10 products by sales?"
- "Show me monthly revenue trends"
- "How many customers by region?"
- "What's the average order value?"
- "Which products have low inventory?"

## 🔧 Technical Details

### AI Models Available
- **llama-3.3-70b-versatile**: Best overall performance (Meta's latest)
- **llama-3.1-8b-instant**: Fastest responses
- **gemma2-9b-it**: Efficient and accurate (Google)
- **deepseek-r1-distill-llama-70b**: Advanced reasoning capabilities
- **qwen/qwen3-32b**: Multilingual powerhouse

### Data Processing
- Automatic data type detection
- Column name cleaning
- Date parsing
- Missing value handling
- SQLite in-memory database for queries

### Security Features
- Password hashing with SHA-256
- Session management
- User role-based access
- Secure file handling

## 🎨 UI Features

- **Modern Design**: Beautiful gradient backgrounds and animations
- **Responsive Layout**: Works on desktop and mobile
- **Interactive Elements**: Hover effects and smooth transitions
- **Data Visualization**: Charts and metrics cards
- **User-Friendly**: Intuitive navigation and clear instructions

## 🔒 Privacy & Security

- **Local Processing**: Data is processed locally and never stored
- **Secure Authentication**: Passwords are hashed and stored securely
- **No Data Collection**: Your data never leaves your system
- **Free Forever**: No hidden costs or data selling

## 🚀 Performance

- **Lightning Fast**: Groq AI provides ultra-fast responses
- **Efficient Processing**: Optimized data handling
- **Scalable**: Handles large datasets efficiently
- **Real-time**: Instant query results and insights

## 🛠️ Development

### Adding New Features
1. **UI Changes**: Modify `streamlit_app.py`
2. **ML Logic**: Update `ml_engine.py`
3. **Authentication**: Edit `auth.py`

### Customization
- **Styling**: Modify the CSS in `streamlit_app.py`
- **AI Models**: Add new models in the model selection
- **Data Formats**: Extend file support in `ml_engine.py`

## 📞 Support

For issues or questions:
- Check the "How to Use" section in the app
- Review the example questions
- Ensure your Groq API key is valid

## 📄 License

Developed by John Evans Okyere | VexaAI © 2025

Built with ❤️ using Streamlit, Groq AI, and Modern Web Technologies

---

**🆓 Free forever • ⚡ Lightning fast • 🔒 Privacy first**
