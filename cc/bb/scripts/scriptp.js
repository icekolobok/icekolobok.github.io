async function fetchData() {
    const response = await fetch('../data/participation.json'); // Assuming data.json is in the same directory
    const data = await response.json();
    return data;
}

fetchData().then(data => {
    const ctx = document.getElementById('myChart').getContext('2d');
    const myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: data.datasets
        },
        options: {
            scales: {
                x: {
                    stacked: true,
                    type: 'time',
                    time: {
                        unit: 'month',
                    },
                    title: {
                        display: true,
                        text: 'Date'
                    }
                },
                y1: {
                    beginAtZero: true,
                    stacked: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Players per Tournament'
                    }
                },
                y2: {
                    beginAtZero: true,
                    stacked: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Unique Players'
                    },
                    grid: {
                        drawOnChartArea: false
                    },
                },
            },
            responsive: true,
            maintainAspectRatio: false
        },
    });
});