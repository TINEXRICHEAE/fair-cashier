function showLoginPrompt() {
  document.getElementById('loginPromptModal').style.display = 'block'; // Show the modal
}

function closeModal(modalId) {
  document.getElementById(modalId).style.display = 'none'; // Hide the modal
}

function redirectToLogin() {
  window.location.href = '/login_user'; // Redirect to login page
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function checkAuthAndExecute(action) {
  const csrftoken = getCookie('csrftoken');
  fetch('/check_auth', {
    headers: {
      'X-CSRFToken': csrftoken
    }
  })
    .then(response => response.json())
    .then(data => {
      if (data.is_authenticated) {
        action(); // Execute the action if authenticated
      } else {
        showLoginPrompt();
      }
    })
    .catch(error => {
      console.error('Error checking authentication:', error);
    });
}

// Fetch Points Data from Backend
function fetchPointsData() {
  const csrftoken = getCookie('csrftoken');
  fetch('/points', {
    headers: {
      'X-CSRFToken': csrftoken
    }
  })
    .then(response => response.json())
    .then(data => {
      pointsBalance = data.points_balance;
      updatePointsBalance();
    })
    .catch(error => {
      console.error('Error fetching points data:', error);
    });
}

// Update Points Data on Backend
function updatePointsData(pointsEarned, pointsUsed) {
  const csrftoken = getCookie('csrftoken');
  fetch('/points', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-CSRFToken': csrftoken
    },
    body: `points_earned=${pointsEarned}&points_used=${pointsUsed}`
  })
    .then(response => response.json())
    .then(data => {
      pointsBalance = data.points_balance;
      updatePointsBalance();
    })
    .catch(error => {
      console.error('Error updating points data:', error);
    });
}

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
  updatePointsData(amount, 0);
}

// Use Points
function usePoints(type, amount) {
  updatePointsData(0, amount);
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
fetchPointsData(); // Fetch points data on page load
startTimeCounters();

function logoutUser() {
  fetch('/logout_user', {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken'), // Include the CSRF token
    },
  })
    .then(response => response.json())
    .then(data => {
      if (data.message === 'Logout successful') {
        alert('You have been logged out.');
        window.location.href = ""; // Redirect to the main app page
      } else {
        alert('Logout failed. Please try again.');
      }
    })
    .catch(error => {
      console.error('Error during logout:', error);
    });
}