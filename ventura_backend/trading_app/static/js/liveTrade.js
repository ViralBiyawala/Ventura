export async function fetchInvestmentOptions() {
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
            console.log(tradeData);
            const candlestickData = tradeData.map(trade => ({
                x: new Date(trade.timestamp).valueOf(),
                o: trade.price - 10,
                h: trade.price  + 30,
                l: trade.price - 15,
                c: trade.price
            }));

            const ctx = document.getElementById('live-trade-chart').getContext('2d');
            ctx.canvas.width = 1000;
            ctx.canvas.height = 250;

            const chart = new Chart(ctx, {
                type: 'candlestick',
                data: {
                    datasets: [{
                        label: `Live Trade Data for ${symbol}`,
                        data: candlestickData,
                    }, {
                        label: 'Close price',
                        type: 'line',
                        data: candlestickData.map(d => ({ x: d.x, y: d.c })),
                        hidden: true,
                    }]
                },
                options: {
                    scales: {
                        x: {
                            type: 'time',
                            time: {
                                unit: 'day',
                                tooltipFormat: 'MMM dd'
                            }
                        },
                        y: {
                            beginAtZero: false
                        }
                    },
                    plugins: {
                        tooltip: {
                            callbacks: {
                                title: function(tooltipItems) {
                                    return tooltipItems[0].label.split(',')[0];
                                }
                            }
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