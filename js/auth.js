function validateStudentLogin(event) {
    event.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    const students = JSON.parse(localStorage.getItem('students') || '[]');
    const student = students.find(s => s.username === username && atob(s.password) === password);
    
    if (student) {
        // Store login status in localStorage
        localStorage.setItem('currentUser', JSON.stringify({
            type: 'student',
            username: username
        }));
        window.location.href = 'quiz-selection.html';
    } else {
        alert('Invalid username or password');
    }
}

function validateTeacherLogin(event) {
    event.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const accessKey = document.getElementById('accessKey') ? document.getElementById('accessKey').value.trim() : '';

    const teachers = JSON.parse(localStorage.getItem('teachers') || '[]');
    const teacher = teachers.find(t => t.username === username && atob(t.password) === password);
    
    // Validate access key as proxy
    const REQUIRED_TEACHER_KEY = '1092';
    if (!teacher || accessKey !== REQUIRED_TEACHER_KEY) {
        alert('Invalid username/password or access key.');
        return false;
    }
    
    if (teacher) {
        // Store login status in localStorage
        localStorage.setItem('currentUser', JSON.stringify({
            type: 'teacher',
            username: username
        }));
        window.location.href = 'teacher-dashboard.html';
    } else {
        // fallback (should not reach due to check above)
        alert('Invalid username or password');
    }
}

// Check if user is logged in
function checkAuth() {
    const currentUser = JSON.parse(localStorage.getItem('currentUser'));
    if (!currentUser) {
        window.location.href = 'index.html';
    }
    return currentUser;
}

// Logout function
function logout() {
    localStorage.removeItem('currentUser');
    window.location.href = 'index.html';
}