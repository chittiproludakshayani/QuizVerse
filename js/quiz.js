// Sample quiz data with subjects and detailed hints
const quizData = {
    easy: [
        {
            question: "What is 2 + 2?",
            options: ["3", "4", "5", "6"],
            correctAnswer: 1,
            subject: "Mathematics",
            hint: {
                topic: "Basic Addition",
                explanation: "This involves simple addition of single-digit numbers. Try visualizing the numbers or using objects to count.",
                relatedConcepts: ["Number Line", "Counting", "Basic Arithmetic"]
            }
        },
        {
            question: "Which planet is closest to the Sun?",
            options: ["Mars", "Venus", "Mercury", "Earth"],
            correctAnswer: 2,
            hint: "It's the smallest planet in our solar system"
        },
        {
            question: "What is the primary color that makes purple when mixed with red?",
            options: ["Yellow", "Green", "Blue", "Orange"],
            correctAnswer: 2,
            hint: "Think of the colors in a rainbow"
        }
    ],
    medium: [
        {
            question: "What is 15 × 7?",
            options: ["95", "105", "115", "125"],
            correctAnswer: 1,
            hint: "Break down 15 into 10 + 5"
        },
        {
            question: "Which element has the chemical symbol 'Fe'?",
            options: ["Fluorine", "Iron", "Francium", "Iodine"],
            correctAnswer: 1,
            hint: "It's a common metal used in construction"
        },
        {
            question: "In which year did World War II end?",
            options: ["1943", "1944", "1945", "1946"],
            correctAnswer: 2,
            hint: "Think about the atomic bombs dropped on Japan"
        }
    ],
    hard: [
        {
            question: "What is the square root of 169?",
            options: ["11", "12", "13", "14"],
            correctAnswer: 2,
            hint: "Think of perfect squares between 10 and 15"
        },
        {
            question: "Which scientist proposed the theory of special relativity?",
            options: ["Isaac Newton", "Albert Einstein", "Niels Bohr", "Max Planck"],
            correctAnswer: 1,
            hint: "Famous for the equation E=mc²"
        },
        {
            question: "What is the capital of Brazil?",
            options: ["Rio de Janeiro", "São Paulo", "Brasília", "Salvador"],
            correctAnswer: 2,
            hint: "It was purposely built to be the capital in the 1960s"
        }
    ]
};

let currentQuiz = {
    difficulty: 'easy',
    questions: [],
    currentQuestion: 0,
    score: 0,
    answers: [],
    startTime: null,
    timeSpent: 0,
    timer: null
};

let isQuizBlocked = false;
let warningCount = 0;
const MAX_WARNINGS = 2;

// Initialize quiz
document.addEventListener('DOMContentLoaded', function() {
    // Get difficulty from URL
    const urlParams = new URLSearchParams(window.location.search);
    const difficulty = urlParams.get('difficulty') || 'easy';
    
    // Load quiz data from teacher questions
    const teacherQuizData = JSON.parse(localStorage.getItem('quizData'));
    if (teacherQuizData && teacherQuizData[difficulty] && teacherQuizData[difficulty].length > 0) {
        quizData[difficulty] = teacherQuizData[difficulty];
    }
    
    initializeQuiz(difficulty);
    startQuizTimer();
});

function initializeQuiz(difficulty) {
    currentQuiz.difficulty = difficulty;
    currentQuiz.questions = quizData[difficulty];
    document.getElementById('difficulty-level').textContent = 
        difficulty.charAt(0).toUpperCase() + difficulty.slice(1);
    
    displayQuestion();
}

function startQuizTimer() {
    const timerDisplay = document.getElementById('time');
    const duration = 1800; // 30 minutes
    currentQuiz.startTime = Date.now();

    // Clear existing timer if any
    if (currentQuiz.timer) {
        clearInterval(currentQuiz.timer);
    }

    // Add CSS for warning state
    const style = document.createElement('style');
    style.textContent = `
        #time.warning {
            color: #ff4444;
            animation: pulse-warning 1s infinite;
        }

        @keyframes pulse-warning {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
    `;
    document.head.appendChild(style);

    currentQuiz.timer = setInterval(function() {
        const elapsedTime = Math.floor((Date.now() - currentQuiz.startTime) / 1000);
        const remainingTime = duration - elapsedTime;

        if (remainingTime <= 0) {
            clearInterval(currentQuiz.timer);
            timerDisplay.textContent = '00:00';
            submitQuiz();
            return;
        }

        const minutes = Math.floor(remainingTime / 60);
        const seconds = remainingTime % 60;

        // Update display with leading zeros
        timerDisplay.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;

        // Store time spent for results
        currentQuiz.timeSpent = elapsedTime;

        // Add warning class when less than 5 minutes remaining
        if (remainingTime <= 300) {
            timerDisplay.classList.add('warning');
            // Flash warning message
            if (!document.getElementById('time-warning')) {
                const warningMsg = document.createElement('div');
                warningMsg.id = 'time-warning';
                warningMsg.textContent = 'Less than 5 minutes remaining!';
                warningMsg.style.cssText = 'color: #ff4444; font-weight: bold; margin-top: 5px; animation: pulse-warning 1s infinite;';
                timerDisplay.parentNode.appendChild(warningMsg);
            }
        }
    }, 1000);
}

function displayQuestion() {
    const question = currentQuiz.questions[currentQuiz.currentQuestion];
    if (!question) return;

    document.getElementById('question-text').textContent = question.question;
    
    const optionsContainer = document.getElementById('options-container');
    optionsContainer.innerHTML = '';
    
    question.options.forEach((option, index) => {
        const optionElement = document.createElement('div');
        optionElement.className = 'option';
        if (currentQuiz.answers[currentQuiz.currentQuestion] === index) {
            optionElement.classList.add('selected');
        }
        optionElement.innerHTML = `
            <span class="option-letter">${String.fromCharCode(65 + index)}.</span>
            <span class="option-text">${option}</span>
        `;
        optionElement.addEventListener('click', () => selectOption(index));
        optionsContainer.appendChild(optionElement);
    });
    
    // Hide hint text when showing new question
    document.getElementById('hint-text').classList.add('hidden');
    
    updateNavigationButtons();
}

function selectOption(index) {
    // Store the selected answer
    currentQuiz.answers[currentQuiz.currentQuestion] = index;
    
    // Update visual selection
    const options = document.querySelectorAll('.option');
    options.forEach(option => option.classList.remove('selected'));
    options[index].classList.add('selected');
    
    // Add animation effect
    options[index].style.animation = 'pulse 0.3s';
    setTimeout(() => {
        options[index].style.animation = '';
    }, 300);
}

function showHint() {
    const hintBox = document.getElementById('hint-box');
    const currentQuestion = currentQuiz.questions[currentQuiz.currentQuestion];
    
    // Show the hint box
    hintBox.style.display = 'block';
    
    if (typeof currentQuestion.hint === 'object') {
        // Structured hint
        document.getElementById('hint-topic').textContent = currentQuestion.hint.topic || 'General Help';
        document.getElementById('hint-explanation').textContent = currentQuestion.hint.explanation || '';
        
        const conceptsList = document.getElementById('hint-concepts');
        conceptsList.innerHTML = '';
        if (currentQuestion.hint.relatedConcepts) {
            currentQuestion.hint.relatedConcepts.forEach(concept => {
                const li = document.createElement('li');
                li.textContent = concept;
                conceptsList.appendChild(li);
            });
        }
    } else {
        // Simple string hint
        document.getElementById('hint-topic').textContent = 'Quick Tip';
        document.getElementById('hint-explanation').textContent = currentQuestion.hint || 'No hint available for this question.';
        document.getElementById('hint-concepts').innerHTML = '';
    }

    // Add animation
    hintBox.classList.add('fade-in');
    setTimeout(() => {
        hintBox.classList.remove('fade-in');
    }, 500);
}

// Add event listener for hint box close button
document.querySelector('.hint-close').addEventListener('click', () => {
    const hintBox = document.getElementById('hint-box');
    hintBox.style.display = 'none';
});

function updateNavigationButtons() {
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const submitBtn = document.getElementById('submit-btn');
    
    prevBtn.disabled = currentQuiz.currentQuestion === 0;
    
    if (currentQuiz.currentQuestion === currentQuiz.questions.length - 1) {
        nextBtn.classList.add('hidden');
        submitBtn.classList.remove('hidden');
    } else {
        nextBtn.classList.remove('hidden');
        submitBtn.classList.add('hidden');
    }
}

function nextQuestion() {
    if (currentQuiz.currentQuestion < currentQuiz.questions.length - 1) {
        currentQuiz.currentQuestion++;
        displayQuestion();
    }
}

function previousQuestion() {
    if (currentQuiz.currentQuestion > 0) {
        currentQuiz.currentQuestion--;
        displayQuestion();
    }
}

function submitQuiz() {
    // Stop the timer
    if (currentQuiz.timer) {
        clearInterval(currentQuiz.timer);
    }
    
    // Calculate score
    currentQuiz.score = currentQuiz.answers.reduce((score, answer, index) => {
        return score + (answer === currentQuiz.questions[index].correctAnswer ? 1 : 0);
    }, 0);

    // Store result in localStorage
    const results = JSON.parse(localStorage.getItem('quizResults') || '[]');
    const currentUser = JSON.parse(localStorage.getItem('currentUser'));
    
    const ts = Date.now();
    const pushed = {
        username: currentUser.username,
        difficulty: currentQuiz.difficulty,
        score: currentQuiz.score,
        totalQuestions: currentQuiz.questions.length,
        timeSpent: currentQuiz.timeSpent,
        timestamp: ts,
        date: new Date().toISOString()
    };

    results.push(pushed);
    localStorage.setItem('quizResults', JSON.stringify(results));

    // Save the last quiz result so the results page can pick it up immediately
    const lastResult = {
        score: currentQuiz.score,
        total: currentQuiz.questions.length,
        timeSpent: currentQuiz.timeSpent,
        timestamp: ts,
        difficulty: currentQuiz.difficulty
    };
    localStorage.setItem('lastQuizResults', JSON.stringify(lastResult));
    // Persist difficulty (used by leaderboard grouping)
    localStorage.setItem('currentQuizDifficulty', currentQuiz.difficulty);
    
    // Redirect to results page
    window.location.href = `results.html?score=${currentQuiz.score}&total=${currentQuiz.questions.length}&time=${currentQuiz.timeSpent}`;
}

// Event Listeners
document.getElementById('hint-btn').addEventListener('click', showHint);
document.getElementById('next-btn').addEventListener('click', nextQuestion);
document.getElementById('prev-btn').addEventListener('click', previousQuestion);
document.getElementById('submit-btn').addEventListener('click', submitQuiz);