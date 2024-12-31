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
      // Update the points balance in the UI
      const pointsBalanceElement = document.querySelector('.points-balance .balance');
      if (pointsBalanceElement) {
        pointsBalanceElement.textContent = `${data.points_balance.toLocaleString()} Points`;
      }

      // Update points earned and points used
      const pointsEarnedElement = document.querySelector('.points-earned .value');
      const pointsUsedElement = document.querySelector('.points-used .value');
      if (pointsEarnedElement) {
        pointsEarnedElement.textContent = `${data.points_earned.toLocaleString()} Points Earned`;
      }
      if (pointsUsedElement) {
        pointsUsedElement.textContent = `${data.points_used.toLocaleString()} Points Used`;
      }
    })
    .catch(error => {
      console.error('Error fetching points data:', error);
    });
}

// Open Modals
function openBuyPointsModal() {
  document.getElementById('buyPointsModal').style.display = 'flex';
}

function openConvertPointsModal() {
  document.getElementById('convertPointsModal').style.display = 'flex';
}

function openSendMoneyModal() {
  document.getElementById('sendMoneyModal').style.display = 'flex';
}

function openProfileModal() {
  document.getElementById('profileModal').style.display = 'flex';
}

// Close Modals
function closeModal(modalId) {
  document.getElementById(modalId).style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function (event) {
  if (event.target.classList.contains('modal')) {
    event.target.style.display = 'none';
  }
};

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

// Initialize
fetchPointsData(); // Fetch points data on page load