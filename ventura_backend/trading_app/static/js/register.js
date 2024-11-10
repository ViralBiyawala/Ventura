import { register } from './api.js';

export async function handleRegister() {
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

export async function loadRegister() {
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
                <button type="submit" class="w-100 icon-button">Register</button>
            </form>
        </div>
    `;

    const registerForm = document.getElementById('register-form');
    registerForm.addEventListener('submit', function (e) {
        e.preventDefault();
        handleRegister();
    });
}

