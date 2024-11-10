import { fetchPortfolioData as fetchPortfolioDataAPI, fetchDashboardData, fetchWatchlist as fetchWatchlistAPI, fetchUserData } from './api.js';

function capitalizeFirstLetter(str) {
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

let currentPage = 1;
const rowsPerPage = 10;

function displayWatchlist(watchlist, page) {
    const watchlistTable = document.getElementById('watchlist-table');
    watchlistTable.innerHTML = '';

    const start = (page - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    const paginatedItems = watchlist.slice(start, end);

    paginatedItems.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${item.symbol}</td>
            <td>$${item.initial_price.toFixed(2)}</td>
            <td>$${item.current_price.toFixed(2)}</td>
            <td style="color: ${item.percentage_change >= 0 ? 'green' : 'red'};">
                ${item.percentage_change.toFixed(2)}%
            </td>
        `;
        watchlistTable.appendChild(row);
    });

    setupPagination(watchlist, page);
}

function setupPagination(watchlist, page) {
    const paginationContainer = document.getElementById('pagination');
    paginationContainer.innerHTML = '';

    const pageCount = Math.ceil(watchlist.length / rowsPerPage);
    for (let i = 1; i <= pageCount; i++) {
        const btn = document.createElement('button');
        btn.innerText = i;
        btn.classList.add('pagination-btn');
        if (i === page) btn.classList.add('active');
        btn.addEventListener('click', () => {
            currentPage = i;
            displayWatchlist(watchlist, currentPage);
        });
        paginationContainer.appendChild(btn);
    }
}

export async function fetchPortfolioData() {
    const token = localStorage.getItem('token');
    try {
        const userData = await fetchUserData(token);
        const dashboardData = await fetchDashboardData(token);
        const portfolioData = await fetchPortfolioDataAPI(token);

        if (portfolioData) {
            const portfolioContainer = document.getElementById('main-content');
            const username = capitalizeFirstLetter(userData.username);

            portfolioContainer.innerHTML = `
                <div id="portfolio" class="portfolio-container">
                    <div class="card">
                        <h2>Watchlist</h2>
                        <div class="table-responsive">
                            <table class="table">
                                <thead>
                                    <tr>
                                        <th>Symbol</th>
                                        <th>Initial Price</th>
                                        <th>Current Price</th>
                                        <th>Change</th>
                                    </tr>
                                </thead>
                                <tbody id="watchlist-table"></tbody>
                            </table>
                        </div>
                        <div id="pagination" class="pagination"></div>
                    </div>
                </div>
                <div id="portfolio" class="portfolio-container">
                    <div class="portfolio-layout">
                        <div class="portfolio-item">
                            <h2 class="portfolio-symbol">${username}'s Portfolio</h2>
                            <p><strong>User ID:</strong> ${portfolioData[0].user_profile}</p>
                            <p><strong>Amount:</strong> $${portfolioData[0].market_value.toLocaleString()}</p>
                            <p><strong>Last Updated:</strong> ${new Date(portfolioData[0].updated_at).toLocaleDateString()}</p>
                        </div>
                        <div class="stats-grid">
                            <div class="stat-card">
                                <h3>Total Investment</h3>
                                <div class="value">$${dashboardData.total_investment.toLocaleString()}</div>
                            </div>
                            <div class="stat-card">
                                <h3>Active Trades</h3>
                                <div class="value">${dashboardData.active_trades}</div>
                            </div>
                            <div class="stat-card">
                                <h3>Total Profit</h3>
                                <div id="profit-value" class=""></div>
                            </div>
                        </div>
                    </div>
                </div>`;

            const profit = portfolioData[0].market_value - dashboardData.total_investment;
            const profitValueDiv = document.getElementById("profit-value");
            profitValueDiv.innerHTML = `${profit >= 0 ? '+' : '-'}$${Math.abs(profit).toLocaleString()}`;
            profitValueDiv.classList.add(profit >= 0 ? 'text-green' : 'text-red');

            fetchWatchlist();
        }
    } catch (error) {
        console.error('Error fetching portfolio data:', error);
    }
}

export function loadPortfolio() {
    fetchPortfolioData();
}

export async function fetchWatchlist() {
    const token = localStorage.getItem('token');
    try {
        const watchlist = await fetchWatchlistAPI(token);
        displayWatchlist(watchlist, currentPage);
    } catch (error) {
        console.error('Error fetching watchlist:', error);
        alert('Failed to fetch watchlist.');
    }
}