export async function fetchPortfolioData() {
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
            const portfolioContainer = document.getElementById('portfolio');
            portfolioContainer.innerHTML = portfolioData.map(item => `
                <div class="portfolio-item">
                    <p>User ID: ${item.user_profile}</p>
                    <p>Amount: ${item.market_value}</p>
                    <p>Last Updated: ${item.updated_at}</p>
                </div>
            `).join('');
        } else {
            console.error('Error fetching portfolio data:');
        }
    } catch (error) {
        console.error('Error fetching portfolio data:', error);
        // alert('Failed to fetch portfolio data.');
    }
}

