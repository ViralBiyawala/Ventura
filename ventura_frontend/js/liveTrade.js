export async function fetchLiveTrades() {
    const token = localStorage.getItem('token');
    try {
        const response = await fetch('http://localhost:8000/api/investment-settings/', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const investmentSettingsData = await response.json();
            if (Array.isArray(investmentSettingsData)) {
                const liveTradesSelect = document.getElementById('live-trades-select');
                liveTradesSelect.innerHTML = investmentSettingsData.map(setting => `
                    <option value="${setting.id}">${setting.symbol}</option>
                `).join('');
            } else {
                alert('Invalid investment settings data.');
            }
        } else {
            alert('Failed to fetch investment settings data.');
        }
    } catch (error) {
        console.error('Error fetching investment settings:', error);
        alert('Failed to fetch investment settings data.');
    }
}

export async function visualizeLiveTrade(tradeId) {
    const token = localStorage.getItem('token');
    try {
        const response = await fetch(`http://localhost:8000/api/trades/${tradeId}/`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const tradeData = await response.json();
            // Implement visualization logic here using tradeData
        } else {
            alert('Failed to fetch trade data.');
        }
    } catch (error) {
        console.error('Error fetching trade data:', error);
        alert('Failed to fetch trade data.');
    }
}
