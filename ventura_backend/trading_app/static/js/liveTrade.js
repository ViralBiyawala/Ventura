import { fetchLiveTrades, fetchInvestmentSettings } from './api.js';  // Add this import statement

let chartInstance = null;

export async function fetchInvestmentOptions() {
    const token = localStorage.getItem('token');
    try {
        const investmentSettingsData = await fetchInvestmentSettings(token);
        if (investmentSettingsData) {
            if (Array.isArray(investmentSettingsData)) {
                const liveTradesSelect = document.getElementById('live-trades-select');
                liveTradesSelect.innerHTML = investmentSettingsData.map(setting => `
                    <option value="${setting.symbol}">${setting.symbol}</option>
                `).join('');

                // Retrieve the selected symbol from localStorage
                const selectedSymbol = localStorage.getItem('selectedSymbol') || investmentSettingsData[0].symbol;
                liveTradesSelect.value = selectedSymbol;

                // Visualize the selected symbol
                visualizeLiveTrade(selectedSymbol);

                // Add event listener for dropdown change
                liveTradesSelect.addEventListener('change', (event) => {
                    const selectedSymbol = event.target.value;
                    localStorage.setItem('selectedSymbol', selectedSymbol);  // Store the selected symbol
                    visualizeLiveTrade(selectedSymbol);
                });
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

export function loadLiveTrade() {
    const mainContent = document.getElementById('main-content');
    mainContent.innerHTML = `
        <div class="portfolio-container">
        <div class="card chart-container mt-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2>Live Trading Chart</h2>
                <select id="live-trades-select" class="form-select" style="width: auto;">
                </select>
            </div>
            <canvas id="live-trade-chart"></canvas>
        </div>
        </div>
    `;
    fetchInvestmentOptions();  // Call fetch to populate select options
}

let chart = null;

export async function visualizeLiveTrade(symbol) {
    const token = localStorage.getItem('token');
    const response = await fetchLiveTrades(token, symbol);  // Use the new function
    if (response) {
        const tradeData = response;

        const candlestickData = tradeData.map(trade => ({
            x: new Date(trade.timestamp).valueOf(),
            o: trade.price - 10,
            h: trade.price + 30,
            l: trade.price - 15,
            c: trade.price
        }));

        const ctx = document.getElementById('live-trade-chart').getContext('2d');
        ctx.canvas.width = 1000;
        ctx.canvas.height = 250;

        // Destroy existing chart if it exists
        if (chart) {
            chart.destroy();
        }

        // Create a new chart instance and assign it to the variable
        chart = new Chart(ctx, {
            type: 'candlestick',
            data: {
                datasets: [{
                    label: `${symbol} Price`,
                    data: candlestickData,
                }, {
                    label: 'Close price',
                    type: 'line',
                    data: candlestickData.map(d => ({ x: d.x, y: d.c })),
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
}