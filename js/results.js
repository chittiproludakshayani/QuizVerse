document.addEventListener('DOMContentLoaded', () => {
    const currentUser = checkAuth();
    if (!currentUser) return;

    displayResults();
    setupCelebration();
    updateUserInfo();
    
    // Set up periodic leaderboard updates (only update when quizResults changed)
    setInterval(checkForNewResults, 2000); // Check for updates every 2 seconds
});

function displayResults() {
    const results = JSON.parse(localStorage.getItem('lastQuizResults')) || {
        score: 0,
        total: 0,
        timeSpent: 0
    };

    const scoreElement = document.getElementById('score');
    const totalElement = document.getElementById('total');
    const percentageElement = document.getElementById('percentage');
    const timeSpentElement = document.getElementById('timeSpent');
    const accuracyElement = document.getElementById('accuracy');

    scoreElement.textContent = results.score;
    totalElement.textContent = results.total;
    
    const percentage = results.total ? Math.round((results.score / results.total) * 100) : 0;
    if (percentageElement) percentageElement.textContent = percentage;
    if (accuracyElement) accuracyElement.textContent = `${percentage}%`;

    // Format time spent
    const minutes = Math.floor(results.timeSpent / 60);
    const seconds = results.timeSpent % 60;
    if (timeSpentElement) timeSpentElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;

    updateLeaderboard(results);
}

function updateLeaderboard(currentResults) {
    const leaderboard = document.getElementById('leaderboard');
    if (!leaderboard) return; // Exit if leaderboard element doesn't exist
    
    const results = JSON.parse(localStorage.getItem('quizResults') || '[]');
    const currentUser = JSON.parse(localStorage.getItem('currentUser'));
    
    // Add current result if not already added and it's a new result
    if (currentUser && currentResults && !results.some(r => 
        r.username === currentUser.username && 
        r.score === currentResults.score && 
        r.timestamp === currentResults.timestamp)) {
        results.push({
            username: currentUser.username,
            score: currentResults.score,
            totalQuestions: currentResults.total,
            timestamp: Date.now(),
            difficulty: localStorage.getItem('currentQuizDifficulty') || 'medium',
            timeSpent: currentResults.timeSpent || 0,
            userType: currentUser.type
        });

        // Sort by score percentage, difficulty, and time spent
        results.sort((a, b) => {
            const aPercentage = (a.score / a.totalQuestions) * 100;
            const bPercentage = (b.score / b.totalQuestions) * 100;
            
            // First compare by percentage
            if (bPercentage !== aPercentage) {
                return bPercentage - aPercentage;
            }
            
            // If percentages are equal, compare by difficulty
            const difficultyWeight = { 'hard': 3, 'medium': 2, 'easy': 1 };
            const diffComparison = difficultyWeight[b.difficulty] - difficultyWeight[a.difficulty];
            if (diffComparison !== 0) {
                return diffComparison;
            }
            
            // If difficulty is equal, faster time wins
            return a.timeSpent - b.timeSpent;
        });

        localStorage.setItem('quizResults', JSON.stringify(results));
    }

    // Update ranking
    const rankingElement = document.getElementById('ranking');
    const userRank = results.findIndex(entry => entry.username === currentUser.username) + 1;
    rankingElement.textContent = userRank > 0 ? `#${userRank}` : '-';

    // Group results by difficulty for the leaderboard
    const difficultySections = {
        hard: results.filter(r => r.difficulty === 'hard'),
        medium: results.filter(r => r.difficulty === 'medium'),
        easy: results.filter(r => r.difficulty === 'easy')
    };

    // Display leaderboard with sections
    leaderboard.innerHTML = Object.entries(difficultySections)
        .filter(([_, items]) => items.length > 0) // Only show difficulties with entries
        .map(([difficulty, items]) => `
            <div class="difficulty-section animate-in">
                <h3 class="difficulty-header">${difficulty.toUpperCase()} Level</h3>
                ${items.slice(0, 5).map((result, index) => `
                    <div class="leaderboard-entry ${result.username === currentUser.username ? 'current-user' : ''}" 
                         style="animation-delay: ${0.1 * index}s">
                        <div class="leaderboard-rank">${index + 1}</div>
                        <div class="user-info">
                            <span class="username">${result.username}</span>
                            <span class="user-type ${result.userType}">${result.userType === 'teacher' ? '👨‍🏫' : '👨‍🎓'}</span>
                        </div>
                        <div class="score-info">
                            <div class="score-percentage">${Math.round((result.score / result.totalQuestions) * 100)}%</div>
                            <div class="time-taken">${formatTime(result.timeSpent)}</div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `).join('');
}

function formatTime(seconds) {
    if (!seconds) return '--:--';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function updateUserInfo() {
    const currentUser = JSON.parse(localStorage.getItem('currentUser'));
    if (currentUser) {
        const usernameElement = document.getElementById('userName');
        const avatarElement = document.getElementById('userAvatar');
        if (usernameElement) usernameElement.textContent = currentUser.username;
        if (avatarElement) avatarElement.textContent = currentUser.username.charAt(0).toUpperCase();
    }
}

// Function to check for new results
function checkForNewResults() {
    const lastUpdate = localStorage.getItem('lastLeaderboardUpdate');
    const currentResults = JSON.parse(localStorage.getItem('quizResults') || '[]');
    
    if (!lastUpdate || JSON.stringify(currentResults) !== lastUpdate) {
        updateLeaderboard(JSON.parse(localStorage.getItem('lastQuizResults')));
        localStorage.setItem('lastLeaderboardUpdate', JSON.stringify(currentResults));
    }
}

function setupCelebration() {
    const results = JSON.parse(localStorage.getItem('lastQuizResults')) || { score: 0, total: 0 };
    const percentage = (results.score / results.total) * 100;
    
    if (percentage >= 70) {
        createConfetti();
    }
}

function createConfetti() {
    const colors = ['#1e3c72', '#4CAF50', '#2a5298', '#ffd700'];
    const celebrationContainer = document.getElementById('celebration');

    for (let i = 0; i < 100; i++) {
        const confetti = document.createElement('div');
        confetti.style.cssText = `
            position: absolute;
            width: 10px;
            height: 10px;
            background-color: ${colors[Math.floor(Math.random() * colors.length)]};
            left: ${Math.random() * 100}vw;
            top: -10px;
            opacity: 0;
            transform: translateY(0);
            animation: fall ${Math.random() * 3 + 2}s linear forwards;
        `;

        celebrationContainer.appendChild(confetti);

        // Remove confetti after animation
        confetti.addEventListener('animationend', () => {
            confetti.remove();
        });
    }
}

// Add CSS animation for confetti
const style = document.createElement('style');
style.textContent = `
    @keyframes fall {
        from {
            opacity: 1;
            transform: translateY(0) rotate(0deg);
        }
        to {
            opacity: 0;
            transform: translateY(100vh) rotate(360deg);
        }
    }
`;
document.head.appendChild(style);