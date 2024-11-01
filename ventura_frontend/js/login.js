async function handleLogin() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const data = await login(username, password);
        if (data.token) {
            localStorage.setItem('token', data.token);
            document.getElementById('dashboard-link').style.display = 'block';
            loadDashboard();
        } else {
            alert('Invalid credentials. Please try again.');
        }
    } catch (error) {
        console.error("Login error:", error);
        alert('Login failed. Please try again.');
    }
}
