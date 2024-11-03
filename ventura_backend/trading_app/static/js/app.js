import { register, login } from './api.js';
import { fetchInvestmentSettings } from './dashboard.js';
import { fetchPortfolioData } from './portfolio.js';
import { fetchInvestmentSettings } from './liveTrade.js';

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
    // setInterval(function () {
    //     const lastCall = getLastApiCall();
    //     const lastParams = getLastApiParams();

    //     if (lastCall && functionMapping[lastCall] && (lastCall.startsWith('loadPortfolio') || lastCall.startsWith('loadLiveTrade'))) {
    //         functionMapping[lastCall](...lastParams);
    //     }
    // }, 60000);
});

function showAuthenticatedLinks() {
    document.getElementById('login-link').style.display = 'none';
    document.getElementById('register-link').style.display = 'none';
    document.getElementById('dashboard-link').style.display = 'inline';
    document.getElementById('profile-link').style.display = 'inline';
    document.getElementById('portfolio-link').style.display = 'inline';
    document.getElementById('live-trade-link').style.display = 'inline';
}

function hideAuthenticatedLinks() {
    document.getElementById('login-link').style.display = 'inline';
    document.getElementById('register-link').style.display = 'inline';
    document.getElementById('dashboard-link').style.display = 'none';
    document.getElementById('profile-link').style.display = 'none';
    document.getElementById('portfolio-link').style.display = 'none';
    document.getElementById('live-trade-link').style.display = 'none';
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
        <button id="initiate-trade-button">Initiate Trade</button>
        <table class="table">
            <thead>
                <tr>
                    <th>Symbol</th>
                    <th>Amount</th>
                    <th>Live Trading Percentage</th>
                    <th>Duration (days)</th>
                    <th>Start Date</th>
                </tr>
            </thead>
            <tbody id="investment-settings-table">
            </tbody>
        </table>
    `;
    document.getElementById('initiate-trade-button').addEventListener('click', handleTradeFormSubmit);

    fetchInvestmentSettings();
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
    const existingModal = document.getElementById('tradeModal');
    if (existingModal) {
        existingModal.remove();
    }

    const mainContent = document.getElementById('main-content');
    const modalHTML = `
        <div class="modal fade" id="tradeModal" tabindex="-1" aria-labelledby="tradeModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="tradeModalLabel">Initiate Trade</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <form id="trade-form">
                            <div class="mb-3">
                                <label for="symbol" class="form-label">Symbol</label>
                                <input type="text" class="form-control" id="symbol" required>
                            </div>
                            <div class="mb-3">
                                <label for="amount" class="form-label">Amount</label>
                                <input type="number" class="form-control" id="amount" required>
                            </div>
                            <div class="mb-3">
                                <label for="trade-fraction" class="form-label">Trade Fraction</label>
                                <input type="number" class="form-control" id="trade-fraction" step="0.01" min="0" max="1" required>
                            </div>
                            <div class="mb-3">
                                <label for="duration" class="form-label">Duration (days)</label>
                                <input type="number" class="form-control" id="duration" required>
                            </div>
                            <button type="submit" class="btn btn-primary">Start Trading</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Add form submit handler
    const tradeForm = document.getElementById('initiate-trade-button');
    tradeForm.addEventListener('submit', handleTradeFormSubmit);

    // Initialize and show the modal
    // const tradeModalElement = document.getElementById('tradeModal');
    // const tradeModal = new bootstrap.Modal(tradeModalElement);
    // tradeModal.show();

    // // Clean up modal from the DOM when closed
    // tradeModalElement.addEventListener('hidden.bs.modal', function () {
    //     tradeModalElement.remove();
    // });
}

async function handleTradeFormSubmit(e) {
    e.preventDefault();
    // const symbol = document.getElementById('symbol').value;
    // const amount = document.getElementById('amount').value;
    // const tradeFraction = document.getElementById('trade-fraction').value;
    // const duration = document.getElementById('duration').value;

    const symbol = 'AAPLYI';
    const amount = 999;
    const tradeFraction = 0.5;
    const duration = 30;

    const token = localStorage.getItem('token');
    const response = await fetch('http://localhost:8000/api/start-trading/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            symbol,
            amount,
            trade_fraction: tradeFraction,
            duration_days: duration
        })
    });

    if (response.ok) {
        alert('Trade initiated successfully!');
        // const modal = bootstrap.Modal.getInstance(document.getElementById('tradeModal'));
        // modal.hide();
    } else {
        alert('Failed to initiate trade.');
    }
}

function loadPortfolio() {
    const mainContent = document.getElementById('main-content');
    mainContent.innerHTML = `
        <h2>Portfolio</h2>
        <div id="portfolio" class="portfolio-container"></div>`
    ;
    fetchPortfolioData();
}

function loadLiveTrade() {
    const mainContent = document.getElementById('main-content');
    mainContent.innerHTML = `
        <h2>Live Trade</h2>
        <div class="mb-3">
            <label for="live-trades-select" class="form-label">Select Stock</label>
            <select id="live-trades-select" class="form-select"></select>
        </div>
        <canvas id="live-trade-chart" width="400" height="200"></canvas>
    `;

    fetchLiveTradeSettings();

    const liveTradesSelect = document.getElementById('live-trades-select');
    liveTradesSelect.addEventListener('change', function () {
        const selectedSymbol = liveTradesSelect.value;
        visualizeLiveTrade(selectedSymbol);
    });
}
