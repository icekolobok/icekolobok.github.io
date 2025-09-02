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
                    type: 'scatter',
                    backgroundColor: 'rgba(237, 40, 57, 0.5)',
                    borderColor: 'rgba(255, 0, 0, 0.9)',
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
                    type: 'scatter',
                    backgroundColor: 'rgba(0, 24, 168, 0.5)',
                    borderColor: 'rgba(0, 0, 255, 0.9)',
                    borderWidth: 1,
                    yAxisID: 'y-axis-1',
                    datalabels: {
                        align: 'end',
                        anchor: 'end'
                    }
                },
                {
                    label: data.datasets[2].label,
                    data: data.datasets[2].data,
                    type: 'scatter',
                    backgroundColor: 'rgba(255, 88, 0, 0.5)',
                    borderColor: 'rgba(255, 79, 0, 0.9)',
                    borderWidth: 1,
                    yAxisID: 'y-axis-1',
                    datalabels: {
                        align: 'end',
                        anchor: 'end'
                    }
                },
                {
                    label: data.datasets[3].label,
                    data: data.datasets[3].data,
                    type: 'scatter',
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
                    label: data.datasets[4].label,
                    data: data.datasets[4].data,
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
            plugins: {
                annotation: {
                  annotations: {
                    box1: {
                      type: 'box',
                      xMin: "2020-01-20T00:00:00",
                      xMax: "2023-05-05T00:00:00",
                      backgroundColor: 'rgba(255, 99, 132, 0.2)',
                      label:{
                        content: "COVID-19 pandemic",
                        display: true,
                        position: {x: 'center', y: 'start'}
                      }
                    },
                    box2: {
                        type: 'box',
                        xMin: "2022-08-24T00:00:00",
                        xMax: "2022-12-21T00:00:00",
                        backgroundColor: 'rgba(72, 104, 187, 0.2)',
                        label:{
                          content: "Play Magnus / chess24 acquisition",
                          display: true,
                          position: {x: 'center', y: 'end'}
                        }
                    },
                    line1: {
                        type: 'line',
                        xMin: "2020-10-23T00:00:00",
                        xMax: "2020-10-23T00:00:00",
                        borderColor: 'rgba(0, 0, 255, 0.5)',
                        borderWidth: 2,
                        label:{
                          content: "Queen's Gambit",
                          display: true,
                          position: "end",
                          backgroundColor: 'rgba(255, 255, 255, 0.5)',
                          color: '#00F'
                        }
                      },
                    line2: {
                        type: 'line',
                        xMin: "2024-12-17T00:00:00",
                        xMax: "2024-12-17T00:00:00",
                        borderColor: 'rgba(0, 0, 255, 0.5)',
                        borderWidth: 2,
                        label:{
                          content: "Proctor Introduction",
                          display: true,
                          position: "end",
                          backgroundColor: 'rgba(255, 255, 255, 0.5)',
                          color: '#00F'
                        }
                    }
                  }
                }
              }
        }
    });
});