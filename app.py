from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
from datetime import datetime, timedelta
from email_fetcher import EmailFetcher
from email_analyzer import EmailAnalyzer
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this')

email_fetcher = EmailFetcher()
email_analyzer = EmailAnalyzer()


@app.route('/')
def index():
    if 'credentials' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/authorize')
def authorize():
    """Start Gmail OAuth flow"""
    try:
        auth_url = email_fetcher.get_authorization_url()
        return redirect(auth_url)
    except Exception as e:
        return f"Error: {str(e)}", 500


@app.route('/oauth2callback')
def oauth2callback():
    """Handle OAuth callback"""
    try:
        code = request.args.get('code')
        credentials = email_fetcher.handle_callback(code)
        session['credentials'] = credentials
        return redirect(url_for('index'))
    except Exception as e:
        return f"Authorization failed: {str(e)}", 500


@app.route('/api/fetch-emails')
def fetch_emails():
    """Fetch and analyze emails from last 24 hours"""
    try:
        if 'credentials' not in session:
            return jsonify({'error': 'Not authenticated'}), 401

        # Fetch emails from last 24 hours
        emails = email_fetcher.fetch_recent_emails(
            credentials=session['credentials'],
            hours=24
        )

        # Analyze and categorize each email
        analyzed_emails = []
        for email in emails:
            analysis = email_analyzer.analyze_email(email)
            analyzed_emails.append(analysis)

        # Sort by priority score (highest first)
        analyzed_emails.sort(key=lambda x: x['priority_score'], reverse=True)

        return jsonify({
            'success': True,
            'total_emails': len(analyzed_emails),
            'emails': analyzed_emails,
            'stats': email_analyzer.get_statistics(analyzed_emails)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/reclassify', methods=['POST'])
def reclassify_email():
    """Allow user to correct email classification"""
    data = request.json
    email_id = data.get('email_id')
    new_category = data.get('category')

    # In a real app, save this for model improvement
    return jsonify({'success': True, 'message': 'Classification updated'})


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
