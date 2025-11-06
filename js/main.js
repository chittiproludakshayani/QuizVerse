// Main JavaScript file
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is logged in on protected pages
    const protectedPages = ['quiz-selection.html', 'quiz.html', 'teacher-dashboard.html'];
    const currentPage = window.location.pathname.split('/').pop();
    
    if (protectedPages.includes(currentPage)) {
        checkAuth();
    }

    // Initialize anti-cheating system
    if (currentPage === 'quiz.html') {
        initAntiCheating();
    }
});

// Anti-cheating system
function initAntiCheating() {
    // Detect tab switching
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            handleCheatingAttempt();
        }
    });

    // Disable right click
    document.addEventListener('contextmenu', function(e) {
        e.preventDefault();
    });

    // Disable keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey || e.altKey) {
            e.preventDefault();
        }
    });
}

function handleCheatingAttempt() {
    alert('Warning: Cheating attempt detected! The quiz will be blocked if you continue.');
    // Add code to block the quiz after multiple attempts
}

// Timer functionality
function startTimer(duration, display) {
    let timer = duration;
    let minutes, seconds;
    
    let countdown = setInterval(function () {
        minutes = parseInt(timer / 60, 10);
        seconds = parseInt(timer % 60, 10);

        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        display.textContent = minutes + ":" + seconds;

        if (--timer < 0) {
            clearInterval(countdown);
            submitQuiz();
        }
    }, 1000);
}

// Update leaderboard
function updateLeaderboard(scores) {
    const leaderboard = document.getElementById('leaderboard');
    if (!leaderboard) return;

    // Sort scores in descending order
    scores.sort((a, b) => b.score - a.score);

    leaderboard.innerHTML = scores.map((entry, index) => `
        <div class="leaderboard-entry">
            <span class="rank">${index + 1}</span>
            <span class="username">${entry.username}</span>
            <span class="score">${entry.score}</span>
        </div>
    `).join('');
}