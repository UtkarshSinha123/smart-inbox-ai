# SmartInbox AI - Intelligent Email Management

AI-powered email management system that automatically categorizes, prioritizes, and summarizes emails to boost productivity.

## Features

- 🔐 Secure Gmail integration
- 🤖 AI-powered email categorization
- ⚡ Urgency detection
- 📊 Smart summaries
- ✅ Action item detection
- 📈 Email analytics dashboard

## Setup Instructions

### 1. Clone Repository

git clone https://github.com/yourusername/smart-inbox-ai.git
cd smart-inbox-ai

text

### 2. Install Dependencies

pip install -r requirements.txt

text

### 3. Setup Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download credentials and save as `credentials.json` in project root
6. Add `http://localhost:5000/oauth2callback` to authorized redirect URIs

### 4. Configure Environment

cp .env.example .env

Edit .env with your settings
text

### 5. Run Application

python app.py

text

Visit `http://localhost:5000`

## Deployment

### Deploy to Render

1. Push code to GitHub
2. Create new Web Service on Render
3. Connect your repository
4. Add environment variables
5. Deploy!

### Deploy to Railway

1. Push code to GitHub
2. Create new project on Railway
3. Connect repository
4. Add environment variables
5. Deploy!

## Technologies

- **Backend**: Python, Flask
- **Email**: Gmail API
- **AI/ML**: scikit-learn, TextBlob
- **Frontend**: HTML, CSS, JavaScript

## License

MIT