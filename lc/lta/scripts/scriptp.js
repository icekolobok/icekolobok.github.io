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
            maintainAspectRatio: false,
            plugins: {
                annotation: {
                  annotations: {
                    box1: {
                      type: 'box',
                      xMin: "2020-01-20T00:00:00",
                      xMax: "2023-05-05T00:00:00",
                      backgroundColor: 'rgba(255, 99, 132, 0.1)',
                      label:{
                        content: "COVID-19 pandemic",
                        display: true,
                        position: {x: 'center', y: 'start'}
                      }
                    },
                    line1: {
                        type: 'line',
                        xMin: "2020-10-23T00:00:00",
                        xMax: "2020-10-23T00:00:00",
                        borderColor: 'rgba(0, 0, 255, 0.4)',
                        borderWidth: 2,
                        label:{
                          content: "Queen's Gambit",
                          display: true,
                          position: "end",
                          backgroundColor: 'rgba(255, 255, 255, 0.5)',
                          color: '#00F'
                        }
                      }
                  }
                }
              }
        },
    });
});