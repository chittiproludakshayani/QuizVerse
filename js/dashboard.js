// Load and display student results
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is a teacher
    const currentUser = checkAuth();
    if (currentUser.type !== 'teacher') {
        window.location.href = 'index.html';
    }

    displayAllResults();
    updateLeaderboard();
});

function displayAllResults() {
    const results = JSON.parse(localStorage.getItem('quizResults') || '[]');
    displayResults(results);
}

function searchStudent() {
    const username = document.getElementById('student-search').value.trim();
    if (!username) {
        displayAllResults();
        return;
    }

    const results = JSON.parse(localStorage.getItem('quizResults') || '[]');
    const filteredResults = results.filter(result => 
        result.username.toLowerCase().includes(username.toLowerCase())
    );
    
    displayResults(filteredResults);
}

function displayResults(results) {
    const resultsContainer = document.getElementById('student-results');
    
    if (results.length === 0) {
        resultsContainer.innerHTML = '<p>No results found</p>';
        return;
    }

    const table = document.createElement('table');
    table.innerHTML = `
        <tr>
            <th>Username</th>
            <th>Difficulty</th>
            <th>Score</th>
            <th>Total Questions</th>
            <th>Date</th>
        </tr>
    `;

    results.forEach(result => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${result.username}</td>
            <td>${result.difficulty}</td>
            <td>${result.score}</td>
            <td>${result.totalQuestions}</td>
            <td>${new Date(result.date).toLocaleString()}</td>
        `;
        table.appendChild(row);
    });

    resultsContainer.innerHTML = '';
    resultsContainer.appendChild(table);
}

function updateLeaderboard() {
    const results = JSON.parse(localStorage.getItem('quizResults') || '[]');
    
    // Calculate average scores per student
    const studentScores = {};
    results.forEach(result => {
        if (!studentScores[result.username]) {
            studentScores[result.username] = {
                totalScore: 0,
                quizCount: 0
            };
        }
        studentScores[result.username].totalScore += (result.score / result.totalQuestions) * 100;
        studentScores[result.username].quizCount++;
    });

    // Convert to array and calculate averages
    const leaderboardData = Object.entries(studentScores)
        .map(([username, data]) => ({
            username,
            averageScore: data.totalScore / data.quizCount
        }))
        .sort((a, b) => b.averageScore - a.averageScore);

    // Display leaderboard
    const leaderboard = document.getElementById('leaderboard');
    leaderboard.innerHTML = leaderboardData
        .map((entry, index) => `
            <div class="leaderboard-entry">
                <span class="rank">${index + 1}</span>
                <span class="username">${entry.username}</span>
                <span class="score">${entry.averageScore.toFixed(1)}%</span>
            </div>
        `)
        .join('');
}