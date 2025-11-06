// Database simulation using localStorage
function initializeDatabase() {
    if (!localStorage.getItem('students')) {
        localStorage.setItem('students', JSON.stringify([]));
    }
    if (!localStorage.getItem('teachers')) {
        localStorage.setItem('teachers', JSON.stringify([]));
    }
}

// Initialize database on page load
initializeDatabase();

// Utility functions
function isUsernameAvailable(username, userType) {
    const users = JSON.parse(localStorage.getItem(userType));
    return !users.some(user => user.username.toLowerCase() === username.toLowerCase());
}

function validatePassword(password) {
    // Password must be at least 8 characters long and contain at least one number and one letter
    return password.length >= 8 && /[A-Za-z]/.test(password) && /[0-9]/.test(password);
}

// Registration functions
function registerStudent(event) {
    event.preventDefault();
    
    const fullname = document.getElementById('fullname').value.trim();
    const username = document.getElementById('username').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;

    // Validation
    if (password !== confirmPassword) {
        alert('Passwords do not match!');
        return false;
    }

    if (!validatePassword(password)) {
        alert('Password must be at least 8 characters long and contain at least one letter and one number.');
        return false;
    }

    if (!isUsernameAvailable(username, 'students')) {
        alert('Username already taken. Please choose another one.');
        return false;
    }

    // Create new student object
    const student = {
        fullname,
        username,
        email,
        password: btoa(password), // Basic encoding (not secure for production)
        dateRegistered: new Date().toISOString()
    };

    // Save to database
    const students = JSON.parse(localStorage.getItem('students'));
    students.push(student);
    localStorage.setItem('students', JSON.stringify(students));

    alert('Registration successful! Please login to continue.');
    window.location.href = 'student-login.html';
    return false;
}

function registerTeacher(event) {
    event.preventDefault();
    
    const fullname = document.getElementById('fullname').value.trim();
    const username = document.getElementById('username').value.trim();
    const email = document.getElementById('email').value.trim();
    const subject = document.getElementById('subject').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const accessKey = document.getElementById('accessKey') ? document.getElementById('accessKey').value.trim() : '';

    // Verify teacher access key
    const REQUIRED_TEACHER_KEY = '1092';
    if (accessKey !== REQUIRED_TEACHER_KEY) {
        alert('Invalid teacher access key. Please contact the administrator.');
        return false;
    }

    // Validation
    if (password !== confirmPassword) {
        alert('Passwords do not match!');
        return false;
    }

    if (!validatePassword(password)) {
        alert('Password must be at least 8 characters long and contain at least one letter and one number.');
        return false;
    }

    if (!isUsernameAvailable(username, 'teachers')) {
        alert('Username already taken. Please choose another one.');
        return false;
    }

    // Create new teacher object
    const teacher = {
        fullname,
        username,
        email,
        subject,
        password: btoa(password), // Basic encoding (not secure for production)
        accessKeyVerified: true,
        dateRegistered: new Date().toISOString()
    };

    // Save to database
    const teachers = JSON.parse(localStorage.getItem('teachers'));
    teachers.push(teacher);
    localStorage.setItem('teachers', JSON.stringify(teachers));

    alert('Registration successful! Please login to continue.');
    window.location.href = 'teacher-login.html';
    return false;
}