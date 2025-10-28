let allEmails = [];

async function fetchEmails() {
    const loadingEl = document.getElementById('loading');
    const statsEl = document.getElementById('stats');
    const emailsContainer = document.getElementById('emailsContainer');
    const refreshBtn = document.getElementById('refreshBtn');

    // Show loading
    loadingEl.classList.remove('hidden');
    statsEl.classList.add('hidden');
    emailsContainer.innerHTML = '';
    refreshBtn.disabled = true;
    refreshBtn.textContent = '⏳ Loading...';

    try {
        const response = await fetch('/api/fetch-emails');
        const data = await response.json();

        if (data.success) {
            allEmails = data.emails;
            displayStats(data.stats);
            displayEmails(data.emails);
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Failed to fetch emails: ' + error.message);
    } finally {
        loadingEl.classList.add('hidden');
        refreshBtn.disabled = false;
        refreshBtn.textContent = '🔄 Refresh Emails';
    }
}

function displayStats(stats) {
    document.getElementById('totalEmails').textContent = stats.total || 0;
    document.getElementById('urgentEmails').textContent = stats.urgent || 0;
    document.getElementById('actionEmails').textContent = stats.action_needed || 0;
    document.getElementById('estimatedTime').textContent = stats.estimated_time || 0;

    document.getElementById('stats').classList.remove('hidden');
}

function displayEmails(emails) {
    const container = document.getElementById('emailsContainer');

    if (emails.length === 0) {
        container.innerHTML = '<div class="email-card">No emails found in the last 24 hours.</div>';
        return;
    }

    // Group by category
    const groups = {
        'urgent': [],
        'work-high': [],
        'work-medium': [],
        'work-low': [],
        'promotion': [],
        'social': [],
        'spam': []
    };

    emails.forEach(email => {
        if (email.urgency_score >= 7) {
            groups.urgent.push(email);
        } else {
            groups[email.category].push(email);
        }
    });

    // Display groups
    const groupTitles = {
        'urgent': '🔴 URGENT',
        'work-high': '🟠 HIGH PRIORITY',
        'work-medium': '🟡 MEDIUM PRIORITY',
        'work-low': '🟢 LOW PRIORITY',
        'promotion': '📧 PROMOTIONS',
        'social': '👥 SOCIAL',
        'spam': '🗑️ SPAM'
    };

    Object.keys(groups).forEach(category => {
        if (groups[category].length > 0) {
            const header = document.createElement('div');
            header.className = 'category-header';
            header.innerHTML = `<h2 style="color: white; margin: 20px 0 10px 0;">${groupTitles[category]} (${groups[category].length})</h2>`;
            container.appendChild(header);

            groups[category].forEach(email => {
                container.appendChild(createEmailCard(email));
            });
        }
    });
}

function createEmailCard(email) {
    const card = document.createElement('div');
    card.className = `email-card ${email.category}`;
    if (email.urgency_score >= 7) {
        card.classList.add('urgent');
    }

    const badgesHTML = email.badges.map(badge =>
        `<span class="badge ${badge.type}">${badge.text}</span>`
    ).join('');

    card.innerHTML = `
        <div class="email-header">
            <div>
                <div class="email-sender">${escapeHtml(email.sender)}</div>
                <span class="email-category category-${email.category}">${email.category.replace('-', ' ')}</span>
            </div>
            <div class="email-time">${email.date}</div>
        </div>
        <div class="email-subject">${escapeHtml(email.subject)}</div>
        <div class="email-badges">${badgesHTML}</div>
        <div class="email-summary">${escapeHtml(email.summary)}</div>
        <div style="font-size: 12px; color: #999;">
            Priority Score: ${email.priority_score}/100 | Urgency: ${email.urgency_score}/10
        </div>
    `;

    return card;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Auto-fetch on page load
window.addEventListener('load', () => {
    // Check if we should auto-fetch
    if (document.getElementById('emailsContainer')) {
        // Give user option to start
        document.getElementById('emailsContainer').innerHTML = `
            <div class="email-card" style="text-align: center;">
                <h3>Welcome to SmartInbox AI! 👋</h3>
                <p style="margin: 15px 0;">Click "Refresh Emails" to analyze your last 24 hours of emails.</p>
                <p style="color: #666; font-size: 14px;">We'll categorize them by priority and highlight urgent items.</p>
            </div>
        `;
    }
});
