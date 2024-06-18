async function fetchData() {
    const response = await fetch('../data/participation.json'); // Assuming data.json is in the same directory
    const data = await response.json();
    return data;
}

fetchData().then(data => {
    const ctx = document.getElementById('myChart').getContext('2d');
    const myChart = new Chart(ctx, {
        data: {
            datasets: [
                {
                    label: data.datasets[0].label,
                    data: data.datasets[0].data,
                    type: 'bar',
                    backgroundColor: 'rgba(0, 173, 131, 0.5)',
                    borderColor: 'rgba(1, 163, 104, 0.9)',
                    borderWidth: 1,
                    yAxisID: 'y-axis-1',
                    datalabels: {
                        align: 'end',
                        anchor: 'end'
                    }
                },
                {
                    label: data.datasets[1].label,
                    data: data.datasets[1].data,
                    type: 'line',
                    backgroundColor: 'rgba(0, 0, 0, 1)',
                    borderColor: 'rgba(0, 0, 0, 1)',
                    borderWidth: 3,
                    pointRadius: 0,
                    cubicInterpolationMode: 'monotone',
                    yAxisID: 'y-axis-2',
                    datalabels: {
                        align: 'end',
                        anchor: 'end'
                    }
                }
            ]
        },
        options: {
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'month',
                    },
                    title: {
                        display: true,
                        text: 'Date'
                    }
                },
                'y-axis-1': {
                    beginAtZero: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Players per Tournament'
                    }
                },
                'y-axis-2': {
                    beginAtZero: true,
                    position: 'left',
                    grid: {
                        drawOnChartArea: false
                    },
                    title: {
                        display: true,
                        text: 'Unique Players'
                    }
                }
            },
            responsive: true,
            maintainAspectRatio: false,
        }
    });
});