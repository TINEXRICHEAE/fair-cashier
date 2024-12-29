// Initial State
let pointsBalance = 1000;
let totalTime = 0; // Total time in seconds
let sessionTime = 0; // Session time in seconds
let totalTimeInterval, sessionTimeInterval;

// DOM Elements
const pointsBalanceElement = document.getElementById('pointsBalance');
const statusProgressElement = document.getElementById('statusProgress');
const totalTimeElement = document.getElementById('totalTime');
const sessionTimeElement = document.getElementById('sessionTime');

// Update Points Balance
function updatePointsBalance() {
  pointsBalanceElement.textContent = pointsBalance.toLocaleString();
  updateStatusBar();
}

// Update Status Bar
function updateStatusBar() {
  const progress = (pointsBalance / 2000) * 100; // Assuming max points is 2000
  if (pointsBalance <= 0) {
    statusProgressElement.style.width = '100%';
    statusProgressElement.style.background = '#e74c3c';
  } else {
    statusProgressElement.style.width = `${progress}%`;
    statusProgressElement.style.background = `linear-gradient(to right, #27ae60 ${progress}%, #e67e22 ${progress}%)`;
  }
}

// Earn Points
function earnPoints(type, amount) {
  pointsBalance += amount;
  updatePointsBalance();
}

// Use Points
function usePoints(type, amount) {
  pointsBalance -= amount;
  if (pointsBalance < 0) pointsBalance = 0;
  updatePointsBalance();
}

// Format Time
function formatTime(seconds) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

// Update Time Counters
function updateTimeCounters() {
  totalTimeElement.textContent = formatTime(totalTime);
  sessionTimeElement.textContent = formatTime(sessionTime);
}

// Start Time Counters
function startTimeCounters() {
  totalTimeInterval = setInterval(() => {
    totalTime++;
    updateTimeCounters();
  }, 1000);

  sessionTimeInterval = setInterval(() => {
    sessionTime++;
    updateTimeCounters();
  }, 1000);
}

// Initialize
updatePointsBalance();
startTimeCounters();