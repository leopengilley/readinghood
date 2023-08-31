function openPopup(popupId) {
  var overlay = document.getElementById('overlay');
  var popup = document.getElementById(popupId);

  overlay.style.display = 'block';
  popup.style.display = 'block';

  // Clear form fields when opening a popup
  var form = popup.querySelector('form');
  if (form) {
    form.reset();
  }
}


function closePopup(popupId) {
  var overlay = document.getElementById('overlay');
  var popup = document.getElementById(popupId);
  
  overlay.style.display = 'none';
  popup.style.display = 'none';
}

function submitForm(event, formType) {
  event.preventDefault(); // Prevent form submission

  if (formType === 'signup') {
    // Handle signup form submission
    var email = document.getElementById('signupEmail').value;
    var username = document.getElementById('signupUsername').value;
    var password = document.getElementById('signupPassword').value;
    var confirmPassword = document.getElementById('signupConfirmPassword').value;

    // Perform signup logic here
    console.log('Signup form submitted');
    console.log('Email:', email);
    console.log('Username:', username);
    console.log('Password:', password);
    console.log('Confirm Password:', confirmPassword);

    // Close the popup after form submission
    closePopup('popup1');
  } else if (formType === 'login') {
    // Handle login form submission
    var username = document.getElementById('loginUsername').value;
    var password = document.getElementById('loginPassword').value;

    // Perform login logic here
    console.log('Login form submitted');
    console.log('Username:', username);
    console.log('Password:', password);

    // Close the popup after form submission
    closePopup('popup2');
  }
}

function togglePasswordVisibility(inputId) {
  var passwordInput = document.getElementById(inputId);
  var toggleButton = document.querySelector(`[onclick="togglePasswordVisibility('${inputId}')]`);

  if (passwordInput.type === 'password') {
    passwordInput.type = 'text';
    toggleButton.style.backgroundImage = 'url(eye-icon-inverted.png)';
  } else {
    passwordInput.type = 'password';
    toggleButton.style.backgroundImage = 'url(eye-icon.png)';
  }
}