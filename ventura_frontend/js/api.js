async function login(username, password) {
    const response = await fetch('http://localhost:8000/api/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    });
    return await response.json();
}

async function register(username, password) {
    const response = await fetch('http://localhost:8000/api/register/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    });
    return await response.json();
}

async function fetchPortfolio(token) {
    const response = await fetch('http://localhost:8000/api/portfolio/', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`, // Include the token in the headers
            'Content-Type': 'application/json'
        }
    });
    return await response.json();
}

// ...existing code...
export { login, register, fetchPortfolio };
// ...existing code...
