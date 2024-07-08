document.addEventListener('DOMContentLoaded', () => {
    fetch('../data/best.json')
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('myChart').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: data.datasets
                },
                options: {
                    indexAxis: 'y',
                    scales:{
                        x1: {
                            beginAtZero: true,
                            position: 'top',
                            max: 200,
                            ticks: {
                                stepSize: 10
                            },
                            title: {
                                display: true,
                                text: 'Points'
                            },
                            grid: {
                                display: true,
                                drawOnChartArea: true
                            },
                        },
                        x2: {
                            beginAtZero: true,
                            position: 'bottom',
                            max: 3400,
                            ticks: {
                                stepSize: 200
                            },
                            title: {
                                display: true,
                                text: 'Performance Rating'
                            },
                            grid: {
                                display: false,
                                drawOnChartArea: false,
                                drawTicks: true,
                            },
                        },
                    },
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        })
        .catch(error => console.error('Error loading the JSON data:', error));
});
