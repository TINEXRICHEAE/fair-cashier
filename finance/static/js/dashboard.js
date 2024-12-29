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