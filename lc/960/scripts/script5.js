document.addEventListener('DOMContentLoaded', () => {
    fetch('../data/data5.json')
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
                            stacked: true,
                            position: 'top',
                            max: 6,
                            ticks: {
                                stepSize: 1
                              }
                        },
                        y: {
                            stacked: true
                        }
                    },
                    responsive: true,
                    maintainAspectRatio: false
                
                }
            });
        })
        .catch(error => console.error('Error loading the JSON data:', error));
});
