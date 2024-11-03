export async function fetchInvestmentSettings() {
    const token = localStorage.getItem('token');
    try {
        const response = await fetch('http://localhost:8000/api/investment-settings/', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const investmentSettings = await response.json();
            if (Array.isArray(investmentSettings)) {
                const investmentSettingsTable = document.getElementById('investment-settings-table');
                investmentSettingsTable.innerHTML = investmentSettings.map(setting => `
                    <tr>
                        <td><span class="gradient-text">${setting.symbol}</span></td>
                        <td>$${setting.amount.toLocaleString()}</td>
                        <td>${setting.live_trading_percentage}%</td>
                        <td>${setting.duration_days} days</td>
                        <td>${new Date(setting.start_date).toLocaleDateString()}</td>
                        <td><span class="badge bg-success">Active</span></td>
                    </tr>
                `).join('');
            } else {
                alert('Invalid investment settings data.');
            }
        } else {
            alert('Failed to fetch investment settings.');
        }
    } catch (error) {
        console.error('Error fetching investment settings:', error);
        alert('Failed to fetch investment settings.', error);
    }
}

export function loadDashboard() {
    const mainContent = document.getElementById('main-content');
    mainContent.innerHTML = `
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Investment</h3>
                <div class="value">$25,420.00</div>
            </div>
            <div class="stat-card">
                <h3>Active Trades</h3>
                <div class="value">12</div>
            </div>
            <div class="stat-card">
                <h3>Total Profit</h3>
                <div class="value gradient-text">+$1,240.50</div>
            </div>
            <div class="stat-card">
                <h3>Success Rate</h3>
                <div class="value">78%</div>
            </div>
        </div>
        <div class="card">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2>Investment Settings</h2>
                <button id="initiate-trade-button" class="btn-primary">Initiate Trade</button>
            </div>
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
        </div>
    `;
}

export async function initiateTrade(tradeData) {
    const token = localStorage.getItem('token');
    try {
        const response = await fetch('http://localhost:8000/api/start-trading/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(tradeData)
        });

        if (response.ok) {
            const result = await response.json();
            alert('Trade initiated successfully.');
        } else {
            alert('Failed to initiate trade.');
        }
    } catch (error) {
        console.error('Error initiating trade:', error);
        alert('Failed to initiate trade.');
    }
}