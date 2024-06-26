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
                            max: 350,
                            ticks: {
                                stepSize: 10
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
