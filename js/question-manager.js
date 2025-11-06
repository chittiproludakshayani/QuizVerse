// Initialize questions in localStorage if not exists
if (!localStorage.getItem('teacherQuestions')) {
    localStorage.setItem('teacherQuestions', JSON.stringify([]));
}

// Track concepts for the current question
let currentConcepts = [];

// Check if user is a teacher
document.addEventListener('DOMContentLoaded', function() {
    const currentUser = checkAuth();
    if (currentUser.type !== 'teacher') {
        window.location.href = 'index.html';
        return;
    }
    loadQuestions();
});

// Add a new concept
function addConcept() {
    const conceptInput = document.getElementById('newConcept');
    const concept = conceptInput.value.trim();
    
    if (concept && !currentConcepts.includes(concept)) {
        currentConcepts.push(concept);
        updateConceptsList();
        conceptInput.value = '';
    }
}

// Remove a concept
function removeConcept(concept) {
    currentConcepts = currentConcepts.filter(c => c !== concept);
    updateConceptsList();
}

// Update the concepts display
function updateConceptsList() {
    const conceptsList = document.getElementById('conceptsList');
    conceptsList.innerHTML = currentConcepts.map(concept => `
        <div class="concept-tag">
            <span>${concept}</span>
            <span class="remove-concept" onclick="removeConcept('${concept}')">&times;</span>
        </div>
    `).join('');
}

// Save a question
function saveQuestion(event) {
    event.preventDefault();

    const questionData = {
        id: Date.now().toString(), // Unique ID for the question
        subject: document.getElementById('subject').value,
        difficulty: document.getElementById('difficulty').value,
        question: document.getElementById('question').value,
        options: [
            document.getElementById('option0').value,
            document.getElementById('option1').value,
            document.getElementById('option2').value,
            document.getElementById('option3').value
        ],
        correctAnswer: parseInt(document.getElementById('correctAnswer').value),
        hint: {
            topic: document.getElementById('hintTopic').value,
            explanation: document.getElementById('hintExplanation').value,
            relatedConcepts: [...currentConcepts]
        },
        createdBy: JSON.parse(localStorage.getItem('currentUser')).username,
        createdAt: new Date().toISOString()
    };

    // Save to localStorage
    const questions = JSON.parse(localStorage.getItem('teacherQuestions'));
    questions.push(questionData);
    localStorage.setItem('teacherQuestions', JSON.stringify(questions));

    // Update questions in quizData
    updateQuizData();

    // Reset form
    resetForm();
    loadQuestions();

    alert('Question saved successfully!');
    return false;
}

// Reset the form
function resetForm() {
    document.getElementById('questionForm').reset();
    currentConcepts = [];
    updateConceptsList();
}

// Load questions
function loadQuestions() {
    const questions = JSON.parse(localStorage.getItem('teacherQuestions'));
    const currentUser = JSON.parse(localStorage.getItem('currentUser'));
    
    const questionList = document.getElementById('questionList');
    const userQuestions = questions.filter(q => q.createdBy === currentUser.username);
    
    questionList.innerHTML = `
        <h3>Your Questions (${userQuestions.length})</h3>
        ${userQuestions.map(q => `
            <div class="question-item">
                <div class="question-header">
                    <div>
                        <strong>${q.subject}</strong> - ${q.difficulty.toUpperCase()}
                    </div>
                    <div class="action-buttons">
                        <button class="edit-btn" onclick="editQuestion('${q.id}')">Edit</button>
                        <button class="delete-btn" onclick="deleteQuestion('${q.id}')">Delete</button>
                    </div>
                </div>
                <p><strong>Q:</strong> ${q.question}</p>
                <p><strong>Hint Topic:</strong> ${q.hint.topic}</p>
            </div>
        `).join('')}
    `;
}

// Delete a question
function deleteQuestion(id) {
    if (!confirm('Are you sure you want to delete this question?')) return;

    let questions = JSON.parse(localStorage.getItem('teacherQuestions'));
    questions = questions.filter(q => q.id !== id);
    localStorage.setItem('teacherQuestions', JSON.stringify(questions));
    
    updateQuizData();
    loadQuestions();
}

// Edit a question
function editQuestion(id) {
    const questions = JSON.parse(localStorage.getItem('teacherQuestions'));
    const question = questions.find(q => q.id === id);
    
    if (!question) return;

    // Fill form with question data
    document.getElementById('subject').value = question.subject;
    document.getElementById('difficulty').value = question.difficulty;
    document.getElementById('question').value = question.question;
    
    question.options.forEach((option, index) => {
        document.getElementById(`option${index}`).value = option;
    });
    
    document.getElementById('correctAnswer').value = question.correctAnswer;
    document.getElementById('hintTopic').value = question.hint.topic;
    document.getElementById('hintExplanation').value = question.hint.explanation;
    
    currentConcepts = [...question.hint.relatedConcepts];
    updateConceptsList();

    // Scroll to form
    document.getElementById('questionForm').scrollIntoView({ behavior: 'smooth' });
}

// Update quiz data with teacher questions
function updateQuizData() {
    const teacherQuestions = JSON.parse(localStorage.getItem('teacherQuestions'));
    
    // Group questions by difficulty
    const questionsByDifficulty = {
        easy: teacherQuestions.filter(q => q.difficulty === 'easy'),
        medium: teacherQuestions.filter(q => q.difficulty === 'medium'),
        hard: teacherQuestions.filter(q => q.difficulty === 'hard')
    };

    // Store in quizData format
    localStorage.setItem('quizData', JSON.stringify(questionsByDifficulty));
}