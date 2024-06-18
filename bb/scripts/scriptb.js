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
                    scales: {
                        x: {
                            beginAtZero: true,
                            position: 'top',
                            max: 340,
                            ticks: {
                                stepSize: 20
                              }
                        },
                        y: {
                            stacked: false,
                            categoryPercentage: 1.0,
                            barPercentage: 1.0
                        }
                    },
                    responsive: true,
                    maintainAspectRatio: false
                
                }
            });
        })
        .catch(error => console.error('Error loading the JSON data:', error));
});
