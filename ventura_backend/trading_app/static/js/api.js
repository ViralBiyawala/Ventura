const BASE_URL = 'http://localhost:8000/api';  // Can be updated to the appropriate base URL

// Helper function for making API requests
async function apiRequest(endpoint, method = 'GET', token = null, data = null) {
    const headers = {
        'Content-Type': 'application/json',
    };

    // Include authorization token if available
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const body = data ? JSON.stringify(data) : null;

    try {
        const response = await fetch(`${BASE_URL}${endpoint}`, {
            method,
            headers,
            body
        });

        if (!response.ok) {
            // Handle error response
            const errorData = await response.json();
            throw new Error(errorData?.message || 'Request failed');
        }

        return await response.json();
    } catch (error) {
        console.error('API request error:', error);
        throw error;  // Propagate error for handling upstream
    }
}

// Login function
async function login(username, password) {
    return await apiRequest('/login/', 'POST', null, { username, password });
}

// Register function
async function register(username, password) {
    return await apiRequest('/register/', 'POST', null, { username, password });
}

// Fetch Investment Settings
async function fetchInvestmentSettings(token) {
    return await apiRequest('/investment-settings/', 'GET', token);
}

// Fetch Watchlist
async function fetchWatchlist(token) {
    return await apiRequest('/watchlist/', 'GET', token);
}



// Initiate Trade
async function initiateTrade(token, tradeData) {
    // Convert amount to string as required by backend
    tradeData.amount = tradeData.amount.toString();
    return await apiRequest('/start-trading/', 'POST', token, tradeData);
}

// Fetch Profile
async function fetchProfile(token) {
    return await apiRequest('/profile/', 'GET', token);
}

// Delete Profile
async function deleteProfile(token) {
    return await apiRequest('/profile/', 'DELETE', token);
}

// Fetch Portfolio Data
async function fetchPortfolioData(token) {
    return await apiRequest('/portfolio/', 'GET', token);
}

// Fetch Live Trades for a specific symbol
async function fetchLiveTrades(token, symbol) {
    return await apiRequest(`/live-trades/?symbol=${symbol}`, 'GET', token);
}

// Fetch Dashboard Data
async function fetchDashboardData(token) {
    return await apiRequest('/dashboard/', 'GET', token);
}

// Fetch Investment Options
async function fetchInvestmentOptions(token) {
    return await apiRequest('/investment-options/', 'GET', token);
}

// Visualize Live Trade for a specific symbol
async function visualizeLiveTrade(token, symbol) {
    return await apiRequest(`/visualize-live-trade/?symbol=${symbol}`, 'GET', token);
}

// fetch the user information
async function fetchUserData(token) {
    return await apiRequest('/user/', 'GET', token);
}

// delete the user information
async function deleteUserData(token) {
    return await apiRequest('/user/', 'DELETE', token);
}

export { login, register, fetchInvestmentSettings, fetchWatchlist, initiateTrade, fetchProfile, deleteProfile, fetchPortfolioData, fetchLiveTrades, fetchDashboardData, fetchInvestmentOptions, visualizeLiveTrade, fetchUserData, deleteUserData };
