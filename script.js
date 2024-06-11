document.addEventListener('DOMContentLoaded', () => {
    fetch('data.json')
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
                            max: 150, // Set the maximum value for the bottom x-axis
                            ticks: {
                                // forces step size to be 50 units
                                stepSize: 10
                              }
                        },
                        y: {
                            stacked: true
                        }
                    },
                    responsive: true,
                    maintainAspectRatio: false // Allow the chart to take the height of its container
                
                }
            });
        })
        .catch(error => console.error('Error loading the JSON data:', error));
});
