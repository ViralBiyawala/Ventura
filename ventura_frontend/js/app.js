import { register, login, fetchPortfolio } from './api.js';

document.addEventListener('DOMContentLoaded', function () {
    const mainContent = document.getElementById('main-content');
    const loginLink = document.getElementById('login-link');
    const dashboardLink = document.getElementById('dashboard-link');
    const registerLink = document.getElementById('register-link');
    const profileLink = document.getElementById('profile-link');

    loginLink.addEventListener('click', function () {
        loadLogin();
    });

    dashboardLink.addEventListener('click', function () {
        loadDashboard();
    });

    registerLink.addEventListener('click', function () {
        loadRegister();
    });

    profileLink.addEventListener('click', function () {
        loadProfile();
    });

    // Check if the user is already logged in
    const token = localStorage.getItem('token');
    if (token) {
        showAuthenticatedLinks();
        loadDashboard();
    } else {
        loadLogin();
    }
});

function showAuthenticatedLinks() {
    document.getElementById('login-link').style.display = 'none';
    document.getElementById('register-link').style.display = 'none';
    document.getElementById('dashboard-link').style.display = 'inline';
    document.getElementById('profile-link').style.display = 'inline';
}

function hideAuthenticatedLinks() {
    document.getElementById('login-link').style.display = 'inline';
    document.getElementById('register-link').style.display = 'inline';
    document.getElementById('dashboard-link').style.display = 'none';
    document.getElementById('profile-link').style.display = 'none';
}

function loadLogin() {
    const mainContent = document.getElementById('main-content');
    mainContent.innerHTML = `
        <h2>Login</h2>
        <form id="login-form">
            <input type="text" id="username" placeholder="Username" required>
            <input type="password" id="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
    `;

    const loginForm = document.getElementById('login-form');
    loginForm.addEventListener('submit', function (e) {
        e.preventDefault();
        handleLogin();
    });
}

async function handleRegister() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    if (password !== confirmPassword) {
        alert('Passwords do not match!');
        return;
    }

    try {
        const response = await register(username, password);
        if (response && response.success) {
            alert('Registration successful!');
            loadLogin();
        } else {
            alert('Registration failed: ' + (response ? response.errors : 'Unknown error'));
        }
    } catch (error) {
        alert('An error occurred: ' + error.message);
    }
}

function loadRegister() {
    const mainContent = document.getElementById('main-content');
    mainContent.innerHTML = `
        <h2>Register</h2>
        <form id="register-form">
            <input type="text" id="username" placeholder="Username" required>
            <input type="password" id="password" placeholder="Password" required>
            <input type="password" id="confirm-password" placeholder="Confirm Password" required>
            <button type="submit">Register</button>
        </form>
    `;

    const registerForm = document.getElementById('register-form');
    registerForm.addEventListener('submit', function (e) {
        e.preventDefault();
        handleRegister();
    });
}

async function handleLogin() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const response = await login(username, password);
        if (response && response.access) {
            localStorage.setItem('token', response.access);
            showAuthenticatedLinks();
            loadDashboard();
        } else {
            alert('Login failed: ' + (response ? response.error : 'Unknown error'));
        }
    } catch (error) {
        alert('An error occurred: ' + error.message);
    }
}

function loadDashboard() {
    const mainContent = document.getElementById('main-content');
    mainContent.innerHTML = `
        <h2>Dashboard</h2>
        <div id="portfolio"></div>
        <button onclick="initiateTrade()">Initiate Trade</button>
    `;

    const token = localStorage.getItem('token');
    fetchPortfolio(token);
}

function loadProfile() {
    const mainContent = document.getElementById('main-content');
    const token = localStorage.getItem('token');

    fetch('http://localhost:8000/api/profile/', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Profile not found');
        }
        return response.json();
    })
    .then(data => {
        mainContent.innerHTML = `
            <h2>Profile</h2>
            <p>Username: ${data.username}</p>
            <button id="logout-button">Logout</button>
            <button id="delete-profile-button">Delete Profile</button>
        `;

        document.getElementById('logout-button').addEventListener('click', handleLogout);
        document.getElementById('delete-profile-button').addEventListener('click', handleDeleteProfile);
    })
    .catch(error => {
        alert('An error occurred: ' + error.message);
        handleLogout();
    });
}

function handleLogout() {
    localStorage.removeItem('token');
    hideAuthenticatedLinks();
    loadLogin();
}

function handleDeleteProfile() {
    const token = localStorage.getItem('token');

    fetch('http://localhost:8000/api/profile/', {
        method: 'DELETE',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            handleLogout();
        } else {
            alert('Profile deletion failed: ' + data.message);
        }
    })
    .catch(error => {
        alert('An error occurred: ' + error.message);
        handleLogout();
    });
}

function initiateTrade() {
    alert('Trade initiated!');
}
