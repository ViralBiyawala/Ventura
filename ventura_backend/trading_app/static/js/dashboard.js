import { initiateTrade as apiInitiateTrade, fetchInvestmentSettings as fetchInvestmentSettingsAPI, fetchWatchlist as fetchWatchlistAPI } from './api.js';

let currentPage = 1;
const rowsPerPage = 10;

function displayInvestmentSettings(investmentSettings, page) {
    const investmentSettingsTable = document.getElementById('investment-settings-table');
    investmentSettingsTable.innerHTML = '';

    const start = (page - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    const paginatedItems = investmentSettings.slice(start, end);

    paginatedItems.forEach(setting => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><span class="gradient-text">${setting.symbol}</span></td>
            <td>$${setting.amount.toLocaleString()}</td>
            <td>${setting.live_trading_percentage}%</td>
            <td>${setting.duration_days} days</td>
            <td>${new Date(setting.start_date).toLocaleDateString()}</td>
            <td><span class="badge bg-success">Active</span></td>
        `;
        investmentSettingsTable.appendChild(row);
    });

    setupPagination(investmentSettings, page);
}

function setupPagination(items, page) {
    const paginationContainer = document.getElementById('pagination');
    paginationContainer.innerHTML = '';

    const pageCount = Math.ceil(items.length / rowsPerPage);
    for (let i = 1; i <= pageCount; i++) {
        const btn = document.createElement('button');
        btn.innerText = i;
        btn.classList.add('pagination-btn');
        if (i === page) btn.classList.add('active');
        btn.addEventListener('click', () => {
            currentPage = i;
            displayInvestmentSettings(items, currentPage);
        });
        paginationContainer.appendChild(btn);
    }
}

export async function fetchInvestmentSettings() {
    const token = localStorage.getItem('token');
    try {
        const investmentSettings = await fetchInvestmentSettingsAPI(token);
        if (Array.isArray(investmentSettings)) {
            displayInvestmentSettings(investmentSettings, currentPage);
        } else {
            alert('Invalid investment settings data.');
        }
    } catch (error) {
        console.error('Error fetching investment settings:', error);
        alert('Failed to fetch investment settings.');
    }
}

export async function loadDashboard() {
    const token = localStorage.getItem('token');
    
    // Main content with both table and form displayed directly
    const mainContent = document.getElementById('main-content');
    mainContent.innerHTML = `
        <div class="portfolio-container">
        <div class="card">
            <h2>Investment Settings</h2>
            <div class="table-responsive">
                <table class="table">
                    <thead>
                        <tr>
                            <th>Symbol</th>
                            <th>Amount</th>
                            <th>Live Trading %</th>
                            <th>Duration</th>
                            <th>Start Date</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody id="investment-settings-table">
                    </tbody>
                </table>
            </div>
            <div id="pagination" class="pagination"></div>
        </div>
        
        <div class="card mt-4">
            <h2>Initiate Trade</h2>
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
    `;

    // Fetch and display settings
    fetchInvestmentSettings();
    fetchWatchlistAPI(token);

    // Add form submit event listener
    const tradeForm = document.getElementById('trade-form');
    tradeForm.addEventListener('submit', handleTradeFormSubmit);
}

export async function handleTradeFormSubmit(e) {
    e.preventDefault();
    const symbol = document.getElementById('symbol').value;
    const amount = document.getElementById('amount').value;
    const tradeFraction = document.getElementById('trade-fraction').value;
    const duration = document.getElementById('duration').value;

    const token = localStorage.getItem('token');
    const response = await apiInitiateTrade(token, {
        symbol,
        amount,
        trade_fraction: tradeFraction,
        duration_days: duration
    });

    if (response.ok) {
        alert('Trade initiated successfully!');
        fetchInvestmentSettings();
    } else {
        alert('Failed to initiate trade.');
    }
}
