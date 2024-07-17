document.addEventListener('DOMContentLoaded', () => {
    fetch('../data/freq.json')
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
                            stacked: false,
                            position: 'top',
                            max: 75,
                            ticks: {
                                stepSize: 5
                              }
                        },
                        y: {
                            stacked: true
                        }
                    },
                    animations: {
                          duration: 0,
                          colors: false,
                          x: false
                    },
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    animation: false,
                    responsive: true,
                    maintainAspectRatio: false
                
                }
            });
        })
        .catch(error => console.error('Error loading the JSON data:', error));
});
