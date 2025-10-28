import re
from datetime import datetime
from textblob import TextBlob
import numpy as np


class EmailAnalyzer:
    def __init__(self):
        # Keywords for categorization
        self.urgent_keywords = [
            'urgent', 'asap', 'immediate', 'critical', 'emergency',
            'deadline', 'today', 'now', 'important', 'priority'
        ]

        self.work_keywords = [
            'meeting', 'project', 'task', 'deadline', 'report',
            'review', 'approval', 'budget', 'client', 'team'
        ]

        self.promotion_keywords = [
            'sale', 'discount', 'offer', 'deal', 'promotion',
            'subscribe', 'unsubscribe', 'marketing', 'newsletter'
        ]

        self.spam_indicators = [
            'winner', 'congratulations', 'claim', 'prize',
            'click here', 'act now', 'limited time', 'free money'
        ]

    def analyze_email(self, email):
        """Analyze single email and return categorized result"""
        subject = email.get('subject', '').lower()
        body = email.get('body', '').lower()
        sender = email.get('sender', '').lower()
        snippet = email.get('snippet', '').lower()

        text = f"{subject} {snippet} {body[:500]}"

        # Calculate various scores
        urgency_score = self._calculate_urgency(text)
        category = self._categorize_email(text, sender)
        sentiment = self._analyze_sentiment(text)
        has_action_items = self._detect_action_items(text)
        priority_score = self._calculate_priority(
            urgency_score, category, has_action_items, sender
        )

        # Generate summary
        summary = self._generate_summary(subject, snippet, body)

        return {
            'id': email['id'],
            'sender': email.get('sender', 'Unknown'),
            'subject': email.get('subject', 'No Subject'),
            'snippet': email.get('snippet', ''),
            'timestamp': email.get('timestamp', datetime.now().timestamp()),
            'date': datetime.fromtimestamp(
                email.get('timestamp', datetime.now().timestamp())
            ).strftime('%Y-%m-%d %H:%M'),
            'category': category,
            'priority_score': priority_score,
            'urgency_score': urgency_score,
            'sentiment': sentiment,
            'has_action_items': has_action_items,
            'summary': summary,
            'badges': self._generate_badges(
                urgency_score, has_action_items, text
            )
        }

    def _calculate_urgency(self, text):
        """Calculate urgency score 0-10"""
        score = 0
        for keyword in self.urgent_keywords:
            if keyword in text:
                score += 2

        # Check for time-sensitive patterns
        if re.search(r'\b(today|tonight|eod|end of day)\b', text):
            score += 3
        if re.search(r'\b(tomorrow|asap)\b', text):
            score += 2
        if re.search(r'\b(this week)\b', text):
            score += 1

        return min(score, 10)

    def _categorize_email(self, text, sender):
        """Categorize email into main categories"""
        # Check for spam first
        spam_count = sum(1 for keyword in self.spam_indicators if keyword in text)
        if spam_count >= 2:
            return 'spam'

        # Check for promotions
        promo_count = sum(1 for keyword in self.promotion_keywords if keyword in text)
        if promo_count >= 2 or 'unsubscribe' in text:
            return 'promotion'

        # Check for work-related
        work_count = sum(1 for keyword in self.work_keywords if keyword in text)
        if work_count >= 2:
            return 'work-high'
        elif work_count >= 1:
            return 'work-medium'

        # Check sender domain
        if any(domain in sender for domain in ['linkedin', 'facebook', 'twitter', 'instagram']):
            return 'social'

        return 'work-low'

    def _analyze_sentiment(self, text):
        """Analyze sentiment of email"""
        try:
            blob = TextBlob(text[:500])
            polarity = blob.sentiment.polarity

            if polarity > 0.3:
                return 'positive'
            elif polarity < -0.3:
                return 'negative'
            else:
                return 'neutral'
        except:
            return 'neutral'

    def _detect_action_items(self, text):
        """Detect if email requires action"""
        action_patterns = [
            r'\b(please|kindly|could you|can you)\b',
            r'\b(review|approve|sign|respond|reply|confirm)\b',
            r'\b(need|require|request)\b',
            r'\?',  # Questions often need responses
        ]

        for pattern in action_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        return False

    def _calculate_priority(self, urgency, category, has_action, sender):
        """Calculate overall priority score 0-100"""
        score = 0

        # Base score from urgency
        score += urgency * 5

        # Category weight
        category_weights = {
            'work-high': 30,
            'work-medium': 20,
            'work-low': 10,
            'promotion': 5,
            'social': 5,
            'spam': 0
        }
        score += category_weights.get(category, 10)

        # Action items add priority
        if has_action:
            score += 20

        # Important senders (simplified - you can customize)
        if any(domain in sender for domain in ['boss', 'ceo', 'director', 'manager']):
            score += 15

        return min(score, 100)

    def _generate_summary(self, subject, snippet, body):
        """Generate a simple summary"""
        # Use snippet if available, otherwise first 150 chars of body
        if snippet:
            summary = snippet[:150]
        else:
            summary = body[:150]

        # Clean up
        summary = re.sub(r'\s+', ' ', summary).strip()

        if len(summary) > 147:
            summary = summary[:147] + "..."

        return summary

    def _generate_badges(self, urgency, has_action, text):
        """Generate visual badges for email"""
        badges = []

        if urgency >= 7:
            badges.append({'type': 'urgent', 'text': '🔴 URGENT'})
        elif urgency >= 4:
            badges.append({'type': 'important', 'text': '🟠 Important'})

        if has_action:
            badges.append({'type': 'action', 'text': '✅ Action Needed'})

        # Check for deadlines
        if re.search(r'\b(deadline|due date|by \w+day)\b', text, re.IGNORECASE):
            badges.append({'type': 'deadline', 'text': '📅 Deadline'})

        # Check for attachments
        if 'attachment' in text or 'attached' in text:
            badges.append({'type': 'attachment', 'text': '📎 Attachment'})

        return badges

    def get_statistics(self, emails):
        """Calculate statistics for dashboard"""
        if not emails:
            return {}

        categories = {}
        urgent_count = 0
        action_needed = 0

        for email in emails:
            # Count by category
            cat = email['category']
            categories[cat] = categories.get(cat, 0) + 1

            # Count urgent
            if email['urgency_score'] >= 7:
                urgent_count += 1

            # Count action items
            if email['has_action_items']:
                action_needed += 1

        return {
            'total': len(emails),
            'urgent': urgent_count,
            'action_needed': action_needed,
            'by_category': categories,
            'estimated_time': action_needed * 5  # 5 min per action item
        }
