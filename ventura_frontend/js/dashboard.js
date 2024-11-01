async function fetchPortfolio() {
    const token = localStorage.getItem('token');
    const response = await fetch('http://localhost:8000/api/portfolio/', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });

    if (response.ok) {
        const portfolioData = await response.json();
        document.getElementById('portfolio').innerHTML = JSON.stringify(portfolioData);
    } else {
        alert('Failed to fetch portfolio data.');
    }
}
