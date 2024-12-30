document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('registrationForm');
  const emailInput = document.getElementById('email');
  const passwordInput = document.getElementById('password');
  const emailError = document.getElementById('emailError');
  const passwordError = document.getElementById('passwordError');
  const messageBox = document.getElementById('messageBox');

  // Password validation rules
  const passwordRules = {
    length: /.{8,}/,
    uppercase: /[A-Z]/,
    lowercase: /[a-z]/,
    digit: /\d/,
    special: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/,
  };

  // Live password validation
  passwordInput.addEventListener('input', function () {
    const password = passwordInput.value;
    Object.keys(passwordRules).forEach((rule) => {
      const isValid = passwordRules[rule].test(password);
      const ruleElement = document.getElementById(rule);
      ruleElement.classList.toggle('valid', isValid);
    });
  });

  // Form submission handler
  form.addEventListener('submit', function (event) {
    event.preventDefault();
    let isValid = true;

    // Validate email
    if (!validateEmail(emailInput.value)) {
      emailError.textContent = 'Please enter a valid email address.';
      emailError.style.display = 'block';
      isValid = false;
    } else {
      emailError.style.display = 'none';
    }

    // Validate password
    if (!validatePassword(passwordInput.value)) {
      passwordError.textContent = 'Password must meet all requirements.';
      passwordError.style.display = 'block';
      isValid = false;
    } else {
      passwordError.style.display = 'none';
    }

    // Submit form if valid
    if (isValid) {
      const formData = new FormData(form);
      fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
          'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
        },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.error) {
            showMessage(data.error, 'error');
          } else {
            showMessage(data.message, 'success');
            form.reset();
            // Optionally, redirect to login page or dashboard after successful registration
            setTimeout(() => {
              window.location.href = "/login_user";
            }, 2000);
          }
        })
        .catch((error) => {
          showMessage('An error occurred. Please try again.', 'error');
        });
    }
  });

  // Helper functions
  function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  function validatePassword(password) {
    return Object.values(passwordRules).every((rule) => rule.test(password));
  }

  function showMessage(message, type) {
    messageBox.textContent = message;
    messageBox.className = `message-box ${type}`;
    messageBox.style.display = 'block';
  }
});