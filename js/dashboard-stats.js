document.addEventListener('DOMContentLoaded', function() {
    const currentUser = checkAuth();
    if (!currentUser) return;

    // Set user name and avatar
    document.getElementById('userName').textContent = currentUser.username;
    document.getElementById('userAvatar').textContent = currentUser.username[0].toUpperCase();

    // Load user stats
    updateUserStats();
});

function updateUserStats() {
    const currentUser = JSON.parse(localStorage.getItem('currentUser'));
    const results = JSON.parse(localStorage.getItem('quizResults') || '[]');
    const userResults = results.filter(r => r.username === currentUser.username);

    // Total quizzes
    document.getElementById('totalQuizzes').textContent = userResults.length;

    if (userResults.length > 0) {
        // Average score
        const avgScore = userResults.reduce((acc, curr) => 
            acc + (curr.score / curr.totalQuestions) * 100, 0) / userResults.length;
        document.getElementById('avgScore').textContent = `${Math.round(avgScore)}%`;

        // Best score
        const bestScore = Math.max(...userResults.map(r => (r.score / r.totalQuestions) * 100));
        document.getElementById('bestScore').textContent = `${Math.round(bestScore)}%`;
    }
}