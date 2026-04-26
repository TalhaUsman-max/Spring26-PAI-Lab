// ── State Management ──
const state = {
  topic: null,
  difficulty: null,
  count: 15,
  questions: [],
  answers: {},
  currentQuestion: 0,
  submitted: false,
};

// ── DOM Helpers ──
const $ = (id) => document.getElementById(id);
const show = (el) => el.classList.remove("hidden");
const hide = (el) => el.classList.add("hidden");

// ── Progress Management ──
function getStepElement(stepNumber) {
  if (stepNumber === 5) return $('quizStep');
  if (stepNumber === 6) return $('resultsStep');
  return $(`step${stepNumber}`);
}

function updateProgress(step) {
  const progressFill = $('progressFill');
  const progressSteps = document.querySelectorAll('.step-indicator');
  const activeSteps = Math.min(step, progressSteps.length);

  progressSteps.forEach((indicator, index) => {
    indicator.classList.toggle('active', index < activeSteps);
  });

  const progress = ((Math.max(activeSteps, 1) - 1) / Math.max(progressSteps.length - 1, 1)) * 100;
  progressFill.style.width = `${progress}%`;
}

// ── Step Navigation ──
function goToStep(stepNumber) {
  document.querySelectorAll('.step').forEach(step => {
    step.classList.remove('active');
  });

  const targetStep = getStepElement(stepNumber);
  if (targetStep) {
    targetStep.classList.add('active');
    updateProgress(stepNumber);
  }
}

// ── Message Display ──
function showMessage(message, type = 'error') {
  const container = $('messageContainer');
  container.innerHTML = `
    <div class="message-box ${type}">
      ${type === 'loading' ? '<div class="spinner"></div>' : ''}
      <span>${message}</span>
    </div>
  `;
}

function clearMessages() {
  $('messageContainer').innerHTML = '';
}

// ── STEP 1: Topic Selection ──
$('validateBtn').addEventListener('click', () => validateTopic());
$('topicInput').addEventListener('keydown', (e) => {
  if (e.key === 'Enter') validateTopic();
});

document.querySelectorAll('.chip').forEach(chip => {
  chip.addEventListener('click', () => {
    document.querySelectorAll('.chip').forEach(c => c.classList.remove('selected'));
    chip.classList.add('selected');
    $('topicInput').value = chip.dataset.topic;
  });
});

async function validateTopic() {
  const input = $('topicInput').value.trim();
  if (!input) {
    showMessage('Please enter a topic to continue.');
    return;
  }

  clearMessages();
  showMessage('Validating topic with AI...', 'loading');
  $('validateBtn').disabled = true;

  try {
    const response = await fetch('/api/validate-topic', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic: input }),
    });

    const data = await response.json();

    if (data.valid) {
      state.topic = data.topic;
      updateTopicDisplay();
      goToStep(2);
    } else {
      showMessage(data.reason || 'Please enter a valid topic.');
    }
  } catch (error) {
    showMessage('Unable to connect to server. Please try again.');
  }

  clearMessages();
  $('validateBtn').disabled = false;
}

function updateTopicDisplay() {
  const displays = ['topicDisplay', 'topicDisplayStep3', 'topicDisplayStep4'];
  displays.forEach(id => {
    const element = $(id);
    if (element) {
      element.innerHTML = `
        <div style="font-size: 1.25rem; font-weight: 600; color: var(--primary-gold);">
          📚 ${state.topic}
        </div>
      `;
    }
  });
}

// ── STEP 2: Difficulty Selection ──
document.querySelectorAll('.difficulty-card').forEach(card => {
  card.addEventListener('click', () => {
    document.querySelectorAll('.difficulty-card').forEach(c => c.classList.remove('selected'));
    card.classList.add('selected');
    state.difficulty = card.dataset.difficulty;
  });
});

$('backToStep1').addEventListener('click', () => goToStep(1));

$('nextToStep3').addEventListener('click', () => {
  if (!state.difficulty) {
    showMessage('Please select a difficulty level to continue.');
    return;
  }
  goToStep(3);
});

// ── STEP 3: Question Count Selection ──
document.querySelectorAll('.count-card').forEach(card => {
  card.addEventListener('click', () => {
    document.querySelectorAll('.count-card').forEach(c => c.classList.remove('selected'));
    card.classList.add('selected');
    state.count = parseInt(card.dataset.count);
  });
});

$('backToStep2').addEventListener('click', () => goToStep(2));

$('nextToStep4').addEventListener('click', () => {
  if (!state.count) {
    showMessage('Please select the number of questions.');
    return;
  }
  generateQuiz();
});

// ── STEP 4: Quiz Generation ──
function generateQuiz() {
  goToStep(4);

  // Show loading message
  showMessage('AI is generating your personalized quiz...', 'loading');

  fetch('/api/generate-quiz', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      topic: state.topic,
      difficulty: state.difficulty,
      count: state.count,
    }),
  })
  .then(response => response.json())
  .then(data => {
    if (data.questions && data.questions.length > 0) {
      state.questions = data.questions;
      state.answers = {};
      state.currentQuestion = 0;
      renderQuiz();
      goToStep(5); // Go to quiz step
    } else {
      throw new Error('No questions generated');
    }
  })
  .catch(error => {
    console.error('Quiz generation error:', error);
    showMessage('Failed to generate quiz. Please try again.');
    goToStep(3);
  });
}

$('backToStep3').addEventListener('click', () => goToStep(3));

// ── QUIZ INTERFACE ──
function renderQuiz() {
  const quizInfo = $('quizInfo');
  quizInfo.textContent = `Quiz: ${state.topic} (${state.difficulty})`;

  renderCurrentQuestion();
  updateQuizProgress();
}

function renderCurrentQuestion() {
  const container = $('questionsContainer');
  const question = state.questions[state.currentQuestion];

  const letters = ['A', 'B', 'C', 'D'];
  const optionsHTML = question.options.map((option, index) => `
    <div class="option-item ${state.answers[question.id] === index ? 'selected' : ''}"
         data-option="${index}"
         onclick="selectOption(${index})">
      <div class="option-letter">${letters[index]}</div>
      <div class="option-text">${option}</div>
    </div>
  `).join('');

  container.innerHTML = `
    <div class="question-card">
      <div class="question-number">Question ${state.currentQuestion + 1} of ${state.questions.length}</div>
      <div class="question-text">${question.question}</div>
      <div class="options-list">
        ${optionsHTML}
      </div>
      ${question.explanation ? `<div class="explanation">💡 ${question.explanation}</div>` : ''}
    </div>
  `;
}

function selectOption(optionIndex) {
  const question = state.questions[state.currentQuestion];
  state.answers[question.id] = optionIndex;

  // Update UI
  document.querySelectorAll('.option-item').forEach((item, index) => {
    item.classList.toggle('selected', index === optionIndex);
  });
}

function updateQuizProgress() {
  const progress = $('quizProgress');
  progress.textContent = `Question ${state.currentQuestion + 1} of ${state.questions.length}`;

  const prevBtn = $('prevQuestion');
  const nextBtn = $('nextQuestion');
  const finishBtn = $('finishQuiz');

  prevBtn.disabled = state.currentQuestion === 0;
  
  if (state.currentQuestion < state.questions.length - 1) {
    show(nextBtn);
    hide(finishBtn);
  } else {
    hide(nextBtn);
    show(finishBtn);
  }
}

$('prevQuestion').addEventListener('click', () => {
  if (state.currentQuestion > 0) {
    state.currentQuestion--;
    renderCurrentQuestion();
    updateQuizProgress();
  }
});

$('nextQuestion').addEventListener('click', () => {
  if (state.currentQuestion < state.questions.length - 1) {
    state.currentQuestion++;
    renderCurrentQuestion();
    updateQuizProgress();
  }
});

$('finishQuiz').addEventListener('click', () => {
  calculateResults();
  goToStep(6); // Go to results step
});

// ── RESULTS PAGE ──
function calculateResults() {
  let correct = 0;
  const breakdown = [];

  state.questions.forEach((question, index) => {
    const userAnswer = state.answers[question.id];
    const correctIndex = question.correct_answer ?? question.correct;
    const isCorrect = userAnswer === correctIndex;

    if (isCorrect) correct++;

    breakdown.push({
      question: question.question,
      userAnswer: question.options[userAnswer] || 'Not answered',
      correctAnswer: question.options[correctIndex] || 'Unknown',
      isCorrect: isCorrect,
      explanation: question.explanation
    });
  });

  const percentage = Math.round((correct / state.questions.length) * 100);
  displayResults(correct, percentage, breakdown);
}

function displayResults(correct, percentage, breakdown) {
  const finalScore = $('finalScore');
  const scorePercentage = $('scorePercentage');
  const gradeBadge = $('gradeBadge');
  const quizSummary = $('quizSummary');
  const breakdownList = $('breakdownList');

  finalScore.textContent = `${percentage}%`;
  scorePercentage.textContent = `${correct} out of ${state.questions.length} correct`;

  // Grade calculation
  let grade, gradeColor;
  if (percentage >= 90) {
    grade = 'A+';
    gradeColor = '#10b981';
  } else if (percentage >= 80) {
    grade = 'A';
    gradeColor = '#059669';
  } else if (percentage >= 70) {
    grade = 'B';
    gradeColor = '#84cc16';
  } else if (percentage >= 60) {
    grade = 'C';
    gradeColor = '#f59e0b';
  } else if (percentage >= 50) {
    grade = 'D';
    gradeColor = '#f97316';
  } else {
    grade = 'F';
    gradeColor = '#ef4444';
  }

  gradeBadge.textContent = grade;
  gradeBadge.style.background = `linear-gradient(135deg, ${gradeColor}, ${gradeColor}dd)`;

  // Summary
  let summary;
  if (percentage >= 80) {
    summary = 'Excellent work! You have a strong understanding of this topic.';
  } else if (percentage >= 60) {
    summary = 'Good job! You have a solid grasp of the material.';
  } else {
    summary = 'Keep studying! Review the explanations to improve your understanding.';
  }
  quizSummary.textContent = summary;

  // Breakdown
  breakdownList.innerHTML = breakdown.map((item, index) => `
    <div class="breakdown-item">
      <div class="breakdown-question">Question ${index + 1}: ${item.question}</div>
      <div class="breakdown-answer">
        Your answer: ${item.userAnswer}<br>
        Correct answer: ${item.correctAnswer}<br>
        ${item.isCorrect ? '✅ Correct' : '❌ Incorrect'}
      </div>
    </div>
  `).join('');
}

$('retakeQuiz').addEventListener('click', () => {
  state.answers = {};
  state.currentQuestion = 0;
  state.submitted = false;
  renderQuiz();
  goToStep(5);
});

$('newTopic').addEventListener('click', () => {
  // Reset state
  state.topic = null;
  state.difficulty = null;
  state.count = 15;
  state.questions = [];
  state.answers = {};
  state.currentQuestion = 0;
  state.submitted = false;

  // Clear inputs
  $('topicInput').value = '';
  document.querySelectorAll('.chip').forEach(c => c.classList.remove('selected'));
  document.querySelectorAll('.difficulty-card').forEach(c => c.classList.remove('selected'));
  document.querySelectorAll('.count-card').forEach(c => c.classList.remove('selected'));
  document.querySelectorAll('.count-card')[2].classList.add('selected'); // Default 15 questions

  clearMessages();
  goToStep(1);
});

// ── Initialize ──
document.addEventListener('DOMContentLoaded', () => {
  // Set default question count
  state.count = 15;

  // Initialize progress
  updateProgress(1);
});