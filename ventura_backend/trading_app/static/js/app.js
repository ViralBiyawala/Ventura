import { register, login } from './api.js';
import { loadProfile} from './profile.js';
import { loadDashboard } from './dashboard.js';
import { loadPortfolio } from './portfolio.js';
import { loadLiveTrade } from './liveTrade.js';

// Helper functions to save and load the last API call details
function saveLastApiCall(callName, params = []) {
    localStorage.setItem('lastGetApiCall', callName);
    localStorage.setItem('lastGetApiParams', JSON.stringify(params));
}

function getLastApiCall() {
    return localStorage.getItem('lastGetApiCall');
}

function getLastApiParams() {
    const params = localStorage.getItem('lastGetApiParams');
    return params ? JSON.parse(params) : [];
}

// Mapping of function names to their corresponding functions
const functionMapping = {
    loadLogin,
    loadDashboard,
    loadRegister,
    loadProfile,
    loadPortfolio,
    loadLiveTrade
};

document.addEventListener('DOMContentLoaded', function () {
    const mainContent = document.getElementById('main-content');
    const loginLink = document.getElementById('login-link');
    const dashboardLink = document.getElementById('dashboard-link');
    const registerLink = document.getElementById('register-link');
    const profileLink = document.getElementById('profile-link');
    const portfolioLink = document.getElementById('portfolio-link');
    const liveTradeLink = document.getElementById('live-trade-link');

    loginLink.addEventListener('click', function () {
        saveLastApiCall('');
        loadLogin();
    });

    dashboardLink.addEventListener('click', function () {
        saveLastApiCall('loadDashboard');
        loadDashboard();
    });

    registerLink.addEventListener('click', function () {
        saveLastApiCall('');
        loadRegister();
    });

    profileLink.addEventListener('click', function () {
        saveLastApiCall('loadProfile');
        loadProfile();
    });

    portfolioLink.addEventListener('click', function () {
        saveLastApiCall('loadPortfolio');
        loadPortfolio();
    });

    liveTradeLink.addEventListener('click', function () {
        saveLastApiCall('loadLiveTrade');
        loadLiveTrade();
    });

    const token = localStorage.getItem('token');
    
    if (token) {
        showAuthenticatedLinks();
        // Load the last page accessed or default to Dashboard
        const lastCall = getLastApiCall();
        const lastParams = getLastApiParams();
        
        if (lastCall && functionMapping[lastCall]) {
            functionMapping[lastCall](...lastParams);
        } else {
            loadDashboard();
        }
    } else {
        loadLogin();
    }

    // Re-hit the last "GET" API every 60 seconds if it exists
    setInterval(function () {
        const lastCall = getLastApiCall();
        const lastParams = getLastApiParams();

        if (lastCall && functionMapping[lastCall] && (lastCall.startsWith('loadPortfolio') || lastCall.startsWith('loadLiveTrade'))) {
            functionMapping[lastCall](...lastParams);
        }
    }, 5000);
});

function showAuthenticatedLinks() {
    document.getElementById('login-link').style.display = 'none';
    document.getElementById('register-link').style.display = 'none';
    document.getElementById('dashboard-link').style.display = 'inline';
    document.getElementById('profile-link').style.display = 'inline';
    document.getElementById('portfolio-link').style.display = 'inline';
    document.getElementById('live-trade-link').style.display = 'inline';
}

export async function hideAuthenticatedLinks() {
    document.getElementById('login-link').style.display = 'inline';
    document.getElementById('register-link').style.display = 'inline';
    document.getElementById('dashboard-link').style.display = 'none';
    document.getElementById('profile-link').style.display = 'none';
    document.getElementById('portfolio-link').style.display = 'none';
    document.getElementById('live-trade-link').style.display = 'none';
}

export async function loadLogin() {
    const mainContent = document.getElementById('main-content');
    mainContent.innerHTML = `
        <div class="card" style="max-width: 400px; margin: 2rem auto;">
            <h2 class="text-center mb-4">Login</h2>
            <form id="login-form">
                <div class="form-group">
                    <input type="text" id="username" placeholder="Username" required>
                </div>
                <div class="form-group">
                    <input type="password" id="password" placeholder="Password" required>
                </div>
                <button type="submit" class="w-100">Login</button>
            </form>
        </div>
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
        <div class="card" style="max-width: 400px; margin: 2rem auto;">
            <h2 class="text-center mb-4">Register</h2>
            <form id="register-form">
                <div class="form-group">
                    <input type="text" id="username" placeholder="Username" required>
                </div>
                <div class="form-group">
                    <input type="password" id="password" placeholder="Password" required>
                </div>
                <div class="form-group">
                    <input type="password" id="confirm-password" placeholder="Confirm Password" required>
                </div>
                <button type="submit" class="w-100">Register</button>
            </form>
        </div>
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
