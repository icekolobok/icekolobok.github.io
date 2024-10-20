document.addEventListener('DOMContentLoaded', () => {
    fetch('../data/data8.json')
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
                            max: 230,
                            ticks: {
                                stepSize: 10
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
                    animation: false,
                    responsive: true,
                    maintainAspectRatio: false
                
                }
            });
        })
        .catch(error => console.error('Error loading the JSON data:', error));
});
