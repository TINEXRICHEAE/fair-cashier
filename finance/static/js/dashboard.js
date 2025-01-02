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
// Initialize
fetchPointsData(); // Fetch points data on page load

// For Buy and Sell Points Modals
function updatePaymentDetailsPlaceholder(paymentChannelElement, paymentDetailsInputElement) {
  const paymentChannel = paymentChannelElement.value;

  switch (paymentChannel) {
    case 'MTN':
      paymentDetailsInputElement.placeholder = "Enter MTN Mobile Number";
      break;
    case 'Airtel':
      paymentDetailsInputElement.placeholder = "Enter Airtel Money Number";
      break;
    case 'bank_transfer': // Note: Ensure this matches the option value in HTML
      paymentDetailsInputElement.placeholder = "Enter Bank Account Number";
      break;
    default:
      paymentDetailsInputElement.placeholder = "Enter Mobile, or Bank Account Number";
  }
}

// Function to send form data to the backend
async function processPayment(url, data) {
  const response = await fetch(url, {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')  // Include CSRF token for Django
      },
      body: JSON.stringify(data)
  });
  const result = await response.json();
  if (result.status === 'success') {
      alert(`${result.message}\nDetails: ${JSON.stringify(result.details, null, 2)}`);
  } else {
      alert(`Error: ${result.message}`);
  }
}

// Function to handle Buy Points form submission
function handleBuyPoints(event) {
  event.preventDefault();

  // Get form data
  const pointsToBuy = parseInt(document.getElementById('pointsToBuy').value);
  const paymentChannel = document.getElementById('paymentChannelForBuy').value;
  const paymentDetails = document.getElementById('paymentDetailsForBuy').value;

  // Convert points to amount (128 points = $1 = UGX 3500)
  const amount = pointsToBuy / 128;
  const amountUGX = amount * 3500;

  // Confirm the conversion rate with the user
  const confirmation = confirm(
      `You are buying ${pointsToBuy} points.\n` +
      `At $${amount.toFixed(2)} (UGX ${amountUGX.toFixed(2)}).\n` +
      `Do you want to proceed?`
  );

  if (!confirmation) {
      return; // Stop if the user cancels
  }

  // Prepare data for the backend
  const data = {
      email: prompt('Enter Your Registered Email to Confirm the Transaction:'),
      password: prompt('Enter Your Password:'),
      pointsToBuy: pointsToBuy,
      payment_channel: paymentChannel,
      payment_details: paymentDetails
  };

  // Send data to the backend
  processPayment('/buy-points', data);
}

// Function to handle Sell Points form submission
function handleSellPoints(event) {
  event.preventDefault();

  // Get form data
  const pointsToSell = parseInt(document.getElementById('pointsToSell').value);
  const paymentChannel = document.getElementById('paymentChannelForSell').value;
  const paymentDetails = document.getElementById('paymentDetailsForSell').value;

  // Convert points to amount (128 points = $1 = UGX 3500)
  const amount = pointsToSell / 128;
  const amountUGX = amount * 3500;

  // Confirm the conversion rate with the user
  const confirmation = confirm(
      `You are selling ${pointsToSell} points.\n` +
      `At $${amount.toFixed(2)} (UGX ${amountUGX.toFixed(2)}).\n` +
      `Do you want to proceed?`
  );

  if (!confirmation) {
      return; // Stop if the user cancels
  }

  // Prepare data for the backend
  const data = {
      email: prompt('Enter Your Registered Email to Confirm the Transaction:'),
      password: prompt('Enter Your Password:'),
      pointsToSell: pointsToSell,
      payment_channel: paymentChannel,
      payment_details: paymentDetails
  };

  // Send data to the backend
  processPayment('/sell-points', data);
}

// Function to handle Share Points form submission
function handleSharePoints(event) {
  event.preventDefault();

  // Get form data
  const receiverEmail = document.getElementById('receiverEmail').value;
  const pointsToShare = parseInt(document.getElementById('pointsToShare').value);

  // Confirm the transaction with the user
  const confirmation = confirm(
      `You are about to share ${pointsToShare} points with ${receiverEmail}.\n` +
      `Do you want to proceed?`
  );

  if (!confirmation) {
      return; // Stop if the user cancels
  }

  // Prepare data for the backend
  const data = {
      email: prompt('Enter Your Registered Email to Confirm the Transaction:'),
      password: prompt('Enter Your Password:'),
      receiverEmail: receiverEmail,
      pointsToShare: pointsToShare
  };

  // Send data to the backend
  processPayment('/share-points', data);
}


// Attach event listeners to the forms
document.getElementById('buyPointsModal').querySelector('form').addEventListener('submit', handleBuyPoints);
document.getElementById('sellPointsModal').querySelector('form').addEventListener('submit', handleSellPoints);
// Attach event listener to the Share Points form
document.getElementById('sharePointsModal').querySelector('form').addEventListener('submit', handleSharePoints);

// Buy Points Modal
function openBuyPointsModal() {
  document.getElementById('buyPointsModal').style.display = 'flex';
}



// Sell Points Modal
function openSellPointsModal() {
  document.getElementById('sellPointsModal').style.display = 'flex';
}


// Share Points Modal
function openSharePointsModal() {
  document.getElementById('sharePointsModal').style.display = 'flex';
}

// Profie Modal
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

// Function to fetch and display transaction history
function fetchTransactionHistory() {
  const csrftoken = getCookie('csrftoken');
  fetch('/transaction-history', {
      headers: {
          'X-CSRFToken': csrftoken
      }
  })
      .then(response => response.json())
      .then(data => {
          if (data.status === 'success') {
              const tbody = document.querySelector('.transaction-history tbody');
              tbody.innerHTML = ''; // Clear existing rows

              // Populate the table with transaction data
              data.transactions.forEach(transaction => {
                  const row = document.createElement('tr');
                  row.innerHTML = `
                      <td>${transaction.date}</td>
                      <td>${transaction.type}</td>
                      <td>${transaction.points}</td>
                      <td>${transaction.direction}</td>
                      <td>${transaction.status}</td>
                  `;
                  tbody.appendChild(row);
              });
          } else {
              console.error('Error fetching transaction history:', data.message);
          }
      })
      .catch(error => {
          console.error('Error fetching transaction history:', error);
      });
}

// Fetch transaction history on page load
fetchTransactionHistory();


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


// Function to fetch and display the user's email
function fetchUserEmail() {
  const csrftoken = getCookie('csrftoken');
  fetch('/get-user-email', {  // Ensure the trailing slash is included
      headers: {
          'X-CSRFToken': csrftoken
      }
  })
      .then(response => {
          if (!response.ok) {
              throw new Error(`HTTP error! Status: ${response.status}`);
          }
          return response.json();
      })
      .then(data => {
          if (data.status === 'success') {
              document.getElementById('email').textContent = data.email;
          } else {
              console.error('Error fetching user email:', data.message);
          }
      })
      .catch(error => {
          console.error('Error fetching user email:', error);
      });
}

// Function to delete the user's account
function deleteAccount() {
  const confirmation = confirm('Are you sure you want to delete your account? This action cannot be undone.');
  if (!confirmation) {
      return; // Stop if the user cancels
  }

  const csrftoken = getCookie('csrftoken');
  fetch('/delete-account', {
      method: 'POST',
      headers: {
          'X-CSRFToken': csrftoken,
          'Content-Type': 'application/json'
      }
  })
      .then(response => response.json())
      .then(data => {
          if (data.status === 'success') {
              alert(data.message);
              window.location.href = ''; // Redirect to the home page
          } else {
              alert('Error: ' + data.message);
          }
      })
      .catch(error => {
          console.error('Error deleting account:', error);
      });
}

// Fetch user email when the profile modal is opened
function openProfileModal() {
  document.getElementById('profileModal').style.display = 'flex';
  fetchUserEmail(); // Fetch and display the user's email
}