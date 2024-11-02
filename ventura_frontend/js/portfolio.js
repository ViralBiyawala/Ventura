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
            if (Array.isArray(portfolioData)) {
                const labels = portfolioData.map(entry => entry.date);
                const data = portfolioData.map(entry => entry.balance);

                const ctx = document.getElementById('portfolio-chart').getContext('2d');
                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Market Value',
                            data: data,
                            backgroundColor: 'rgba(75, 192, 192, 0.2)',
                            borderColor: 'rgba(75, 192, 192, 1)',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
            } else {
                alert('Invalid portfolio data.');
            }
        } else {
            alert('Failed to fetch portfolio data.');
        }
    } catch (error) {
        console.error('Error fetching portfolio data:', error);
        alert('Failed to fetch portfolio data.');
    }
}
