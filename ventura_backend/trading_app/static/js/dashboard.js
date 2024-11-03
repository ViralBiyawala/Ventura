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
                        <td>${setting.symbol}</td>
                        <td>${setting.amount}</td>
                        <td>${setting.live_trading_percentage}</td>
                        <td>${setting.duration_days}</td>
                        <td>${setting.start_date}</td>
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
// ...existing code...

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