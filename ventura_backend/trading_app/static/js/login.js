import { login } from './api.js';
import { showAuthenticatedLinks } from './app.js';
import { loadDashboard } from './dashboard.js';

export async function loadLogin() {
    const mainContent = document.getElementById('main-content');
    mainContent.innerHTML = `
        <div class="card" style="max-width: 400px; margin: 2rem auto;">
            <h2 class="text-center mb-4">Login </h2>
            <form id="login-form">
                <div class="form-group">
                    <input type="text" id="username" placeholder="Username" required>
                </div>
                <div class="form-group">
                    <input type="password" id="password" placeholder="Password" required>
                </div>
                <button type="submit" class="w-100 icon-button">Login</button>
            </form>
        </div>
    `;

    const loginForm = document.getElementById('login-form');
    loginForm.addEventListener('submit', function (e) {
        e.preventDefault();
        handleLogin();
    });
}

export async function handleLogin() {
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
