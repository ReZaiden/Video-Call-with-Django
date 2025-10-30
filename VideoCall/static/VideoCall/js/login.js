// DOM Elements
const signinPage = document.getElementById('signin-page');
const signupPage = document.getElementById('signup-page');

// Switch pages
function switchToSignup() {
    signinPage.classList.remove('active');
    signupPage.classList.add('active');
}

function switchToSignin() {
    signupPage.classList.remove('active');
    signinPage.classList.add('active');
}
