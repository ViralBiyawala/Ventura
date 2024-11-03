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
            const investmentSettingsData = await response.json();
            if (Array.isArray(investmentSettingsData)) {
                const liveTradesSelect = document.getElementById('live-trades-select');
                liveTradesSelect.innerHTML = investmentSettingsData.map(setting => `
                    <option value="${setting.symbol}">${setting.symbol}</option>
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

export async function visualizeLiveTrade(symbol) {
    const token = localStorage.getItem('token');
    try {
        const response = await fetch(`http://localhost:8000/api/live-trades/?symbol=${symbol}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const tradeData = await response.json();
            const labels = tradeData.map(trade => new Date(trade.timestamp).toLocaleTimeString());
            const prices = tradeData.map(trade => trade.price);

            const ctx = document.getElementById('live-trade-chart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: `Live Trade Data for ${symbol}`,
                        data: prices,
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1,
                        fill: false
                    }]
                },
                options: {
                    scales: {
                        x: {
                            type: 'time',
                            time: {
                                unit: 'minute'
                            }
                        },
                        y: {
                            beginAtZero: false
                        }
                    }
                }
            });
        } else {
            alert('Failed to fetch trade data.');
        }
    } catch (error) {
        console.error('Error fetching trade data:', error);
        alert('Failed to fetch trade data.');
    }
}
