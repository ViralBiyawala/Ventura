export async function fetchPortfolioData() {
    const token = localStorage.getItem('token');
    try {
        // Fetch user details
        const userResponse = await fetch('http://localhost:8000/api/profile/', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!userResponse.ok) {
            throw new Error('Failed to fetch user details');
        }

        const userData = await userResponse.json();

        // Fetch portfolio data
        const portfolioResponse = await fetch('http://localhost:8000/api/portfolio/', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (portfolioResponse.ok) {
            const portfolioData = await portfolioResponse.json();
            const portfolioContainer = document.getElementById('portfolio');
            function capitalizeFirstLetter(str) {
                return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
            }
            
            const username = capitalizeFirstLetter(userData.username);
            portfolioContainer.innerHTML = `
            <div class="portfolio-container">
                    ${portfolioData.map(item => `
                        <div class="portfolio-item">
                            <h2 class="text-center portfolio-symbol"><strong>${username}'s Portfolio</strong></h2>
                            <p class="portfolio-symbol">User ID:${item.user_profile}</p>
                            <p><strong>Amount:</strong> $${item.market_value.toLocaleString()}</p>
                            <p><strong>Last Updated:</strong> ${new Date(item.updated_at).toLocaleDateString()}</p>
                        </div>
                    `).join('')}
                </div>`;
        } else {
            console.error('Error fetching portfolio data:');
        }
    } catch (error) {
        console.error('Error fetching portfolio data:', error);
        // alert('Failed to fetch portfolio data.');
    }
}

