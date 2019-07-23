/* globals Chart:false, feather:false */

(function () {
    'use strict'

    feather.replace()

    var ctx2 = document.getElementById('myPie')

    var pie_data = {
        datasets: [{
            data: [10, 20, 30],
            backgroundColor:["rgb(255, 99, 132)","rgb(54, 162, 235)","rgb(255, 205, 86)"]
        }],

        // These labels appear in the legend and in the tooltips when hovering different arcs
        labels: [
            'Red',
            'Yellow',
            'Blue'
        ]
    };

    var myDoughnutChart = new Chart(ctx2, {
        type: 'doughnut',
        data: pie_data,
        options: Chart.defaults.doughnut
    });


    // Graphs
    var ctx = document.getElementById('myChart')
    // eslint-disable-next-line no-unused-vars
    var myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: $('#myChart').parent('.chart-wrapper').data('series-labels'),
            datasets: [{
                label: 'Fact',
                data: $('#myChart').parent('.chart-wrapper').data('series-fact'),
                lineTension: 0.2,
                backgroundColor: 'transparent',
                borderColor: '#007bff',
                borderWidth: 4,
                pointBackgroundColor: '#007bff'
            },
                {
                    label: 'Plan',
                    borderDash: [5, 5],
                    lineTension: 0.2,
                    data: $('#myChart').parent('.chart-wrapper').data('series-plan'),
                    backgroundColor: 'transparent',
                    borderColor: '#ff1a23',
                    borderWidth: 4,
                    pointBackgroundColor: 'transparent'
                }

            ]
        },
        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: false
                    }
                }]
            },
            legend: {
                display: true
            }
        }
    })
}())
