export async function fetchPortfolio() {
    const token = localStorage.getItem('token');
    try {
        const response = await fetch('http://localhost:8000/api/portfolio/', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const portfolioData = await response.json();
            if (Array.isArray(portfolioData)) {
                // Update balance dynamically
                const balance = portfolioData.reduce((acc, item) => acc + item.market_value, 0);
                const balanceElement = document.getElementById('balance');
                if (balanceElement) {
                    balanceElement.innerText = `Balance: $${balance.toFixed(2)}`;
                }

                // Format and display portfolio data
                const portfolioElement = document.getElementById('portfolio');
                if (portfolioElement) {
                    portfolioElement.innerHTML = portfolioData.map(item => `
                        <div class="portfolio-item">
                            <p>ID: ${item.id}</p>
                            <p>Market Value: $${item.market_value.toFixed(2)}</p>
                            <p>Updated At: ${new Date(item.updated_at).toLocaleString()}</p>
                        </div>
                    `).join('');
                }
            } else {
                alert('Invalid portfolio data.');
            }
        } else {
            alert('Failed to fetch portfolio data.');
        }
    } catch (error) {
        console.error('Error fetching portfolio:', error);
        alert('Failed to fetch portfolio data.');
    }
}

export function startPortfolioUpdateInterval() {
    setInterval(() => {
        const balanceElement = document.getElementById('balance');
        if (balanceElement) {
            fetchPortfolio();
        }
    }, 5000); // Update every 5 seconds
}

// export async function fetchTrades() {
//     const token = localStorage.getItem('token');
//     try {
//         const response = await fetch('http://localhost:8000/api/trades/', {
//             method: 'GET',
//             headers: {
//                 'Authorization': `Bearer ${token}`
//             }
//         });

//         if (response.ok) {
//             const tradesData = await response.json();
//             const tradesTable = document.getElementById('trades-table');
//             tradesTable.innerHTML = tradesData.map(trade => `
//                 <tr>
//                     <td>${trade.symbol}</td>
//                     <td>${trade.trade_type}</td>
//                     <td>${trade.current_price}</td>
//                     <td>${trade.quantity}</td>
//                     <td>${trade.timestamp}</td>
//                 </tr>
//             `).join('');
//         } else {
//             alert('Failed to fetch trades data.');
//         }
//     } catch (error) {
//         console.error('Error fetching trades:', error);
//         alert('Failed to fetch trades data.');
//     }
// }

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
        alert('Failed to fetch investment settings.');
    }
}

export async function fetchLiveTrades() {
    const token = localStorage.getItem('token');
    try {
        const response = await fetch('http://localhost:8000/api/live-trades/', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const liveTradesData = await response.json();
            const liveTradesSelect = document.getElementById('live-trades-select');
            liveTradesSelect.innerHTML = liveTradesData.map(trade => `
                <option value="${trade.id}">${trade.symbol} - ${trade.trade_type}</option>
            `).join('');
        } else {
            alert('Failed to fetch live trades data.');
        }
    } catch (error) {
        console.error('Error fetching live trades:', error);
        alert('Failed to fetch live trades data.');
    }
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