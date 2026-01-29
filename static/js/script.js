document.addEventListener('DOMContentLoaded', () => {
    const streamContainer = document.getElementById('events-stream');
    
    // Poll every 15 seconds (15000 ms)
    setInterval(fetchEvents, 15000);
    
    // Initial fetch
    fetchEvents();

    async function fetchEvents() {
        try {
            const response = await fetch('/api/events');
            if (!response.ok) {
                console.error('Network response was not ok');
                return;
            }
            const events = await response.json();
            renderEvents(events);
        } catch (error) {
            console.error('Error fetching events:', error);
            streamContainer.innerHTML = '<div class="loading">Error loading events. Is the backend running?</div>';
        }
    }

    function renderEvents(events) {
        if (events.length === 0) {
            streamContainer.innerHTML = '<div class="loading">No events found yet.</div>';
            return;
        }

        streamContainer.innerHTML = ''; // Clear current listing (simple approach)

        events.forEach((event, index) => {
            const card = createEventCard(event);
            // Stagger animation
            card.style.animationDelay = `${index * 0.1}s`;
            streamContainer.appendChild(card);
        });
    }

    function createEventCard(event) {
        const card = document.createElement('div');
        card.className = `event-card event-${event.action}`;

        let icon = '';
        let messageHtml = '';

        // Safely escape basic HTML to prevent XSS (basic implementation)
        const author = escapeHtml(event.author);
        const toBranch = escapeHtml(event.to_branch);
        const fromBranch = escapeHtml(event.from_branch);
        const timestamp = escapeHtml(event.timestamp);

        if (event.action === 'PUSH') {
            icon = '➝'; // Simple arrow or use SVG
            // Format: "{author} pushed to {to_branch} on {timestamp}"
            messageHtml = `<span class="highlight">${author}</span> pushed to <span class="highlight">${toBranch}</span>`;
        } else if (event.action === 'PULL_REQUEST') {
            icon = '⚡';
            // Format: "{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}"
            messageHtml = `<span class="highlight">${author}</span> submitted a pull request from <span class="highlight">${fromBranch}</span> to <span class="highlight">${toBranch}</span>`;
        } else if (event.action === 'MERGE') {
            icon = '⚓';
            // Format: "{author} merged branch {from_branch} to {to_branch} on {timestamp}"
            messageHtml = `<span class="highlight">${author}</span> merged branch <span class="highlight">${fromBranch}</span> to <span class="highlight">${toBranch}</span>`;
        } else {
            icon = '?';
            messageHtml = `Unknown action by ${author}`;
        }

        card.innerHTML = `
            <div class="event-icon-container">
                ${icon}
            </div>
            <div class="event-content">
                <div class="event-text">${messageHtml}</div>
                <div class="event-time">on ${timestamp}</div>
            </div>
        `;

        return card;
    }

    function escapeHtml(text) {
        if (!text) return '';
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});
