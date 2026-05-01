/**
 * Coerentis Protection Evidence - Chart Rendering
 * Drawdown comparison chart for crisis simulations
 */

(function() {
    'use strict';

    // Real data from May 2021 Crypto Crash simulation
    // Note: Dates simplified for display (actual simulation had hourly data points)
    const MAY_2021_CRASH_DATA = {
        dates: [
            '2021-05-12', '2021-05-13', '2021-05-14', '2021-05-15', '2021-05-16',
            '2021-05-17', '2021-05-18', '2021-05-19', '2021-05-20', '2021-05-21',
            '2021-05-22', '2021-05-23'
        ],
        // Sample equity curve values (every ~22 hours from full dataset)
        unshielded: [
            100000, 100000, 100139, 100222, 100320,
            100755, 100643, 100780, 101079, 101368,
            102020, 116946  // Final value after recovery
        ],
        shielded: [
            100000, 100000, 100139, 100222, 100320,
            100755, 100643, 100780, 101079, 101368,
            102020, 115229  // Slightly lower due to blocked trades
        ]
    };

    let drawdownChart = null;

    function initDrawdownChart() {
        const canvas = document.getElementById('drawdownChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');

        // Destroy existing chart if it exists
        if (drawdownChart) {
            drawdownChart.destroy();
        }

        drawdownChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: MAY_2021_CRASH_DATA.dates,
                datasets: [
                    {
                        label: 'Unshielded',
                        data: MAY_2021_CRASH_DATA.unshielded,
                        borderColor: '#FF4444',
                        backgroundColor: 'rgba(255, 68, 68, 0.1)',
                        borderWidth: 3,
                        fill: false,
                        tension: 0.1,
                        pointRadius: 0,
                        pointHoverRadius: 6
                    },
                    {
                        label: 'Shielded',
                        data: MAY_2021_CRASH_DATA.shielded,
                        borderColor: '#2EA8FF',
                        backgroundColor: 'rgba(46, 168, 255, 0.1)',
                        borderWidth: 3,
                        fill: false,
                        tension: 0.1,
                        pointRadius: 0,
                        pointHoverRadius: 6
                    },
                    {
                        label: 'Max Drawdown Limit',
                        data: MAY_2021_CRASH_DATA.dates.map(() => 90000), // -10% limit
                        borderColor: '#2EA8FF',
                        borderWidth: 2,
                        borderDash: [5, 5],
                        fill: false,
                        pointRadius: 0,
                        pointHoverRadius: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        display: false // Using custom legend in HTML
                    },
                    tooltip: {
                        backgroundColor: 'rgba(7, 18, 37, 0.9)',
                        padding: 12,
                        titleFont: {
                            size: 14,
                            weight: '600'
                        },
                        bodyFont: {
                            size: 13
                        },
                        callbacks: {
                            label: function(context) {
                                const value = context.parsed.y;
                                const formatted = new Intl.NumberFormat('en-GB', {
                                    style: 'currency',
                                    currency: 'GBP',
                                    minimumFractionDigits: 0,
                                    maximumFractionDigits: 0
                                }).format(value);
                                
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                label += formatted;
                                
                                // Add drawdown percentage for portfolio values
                                if (context.datasetIndex < 2) {
                                    const drawdown = ((value - 100000) / 100000 * 100).toFixed(1);
                                    label += ` (${drawdown}%)`;
                                }
                                
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false,
                            color: 'rgba(255, 255, 255, 0.05)'
                        },
                        ticks: {
                            color: 'var(--text-muted)',
                            font: {
                                size: 11
                            },
                            maxRotation: 45,
                            minRotation: 45
                        }
                    },
                    y: {
                        beginAtZero: false,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        },
                        ticks: {
                            color: 'var(--text-muted)',
                            font: {
                                size: 11
                            },
                            callback: function(value) {
                                return '£' + (value / 1000).toFixed(0) + 'K';
                            }
                        }
                    }
                }
            }
        });
    }

    // Initialize when DOM is ready
    function init() {
        // Wait for Chart.js to be available
        if (typeof Chart === 'undefined') {
            setTimeout(init, 100);
            return;
        }

        initDrawdownChart();

        // Handle window resize for responsive chart
        let resizeTimer;
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(function() {
                if (drawdownChart) {
                    drawdownChart.resize();
                }
            }, 250);
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Export function to update chart with real data
    window.updateDrawdownChart = function(data) {
        if (!data || !drawdownChart) return;
        
        drawdownChart.data.labels = data.dates;
        drawdownChart.data.datasets[0].data = data.unshielded;
        drawdownChart.data.datasets[1].data = data.shielded;
        drawdownChart.update();
    };
})();
