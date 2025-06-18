// Dashboard-specific JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    initializeHeatmap();
});

function initializeCharts() {
    // Temperature Trend Chart
    const tempCtx = document.getElementById('temperatureChart');
    if (tempCtx && typeof chartData !== 'undefined') {
        new Chart(tempCtx, {
            type: 'line',
            data: {
                labels: chartData.temperature_trend.labels,
                datasets: [{
                    label: 'Temperature (°C)',
                    data: chartData.temperature_trend.data,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    // Species Distribution Chart
    const speciesCtx = document.getElementById('speciesChart');
    if (speciesCtx && typeof chartData !== 'undefined') {
        new Chart(speciesCtx, {
            type: 'doughnut',
            data: {
                labels: chartData.species_count.labels,
                datasets: [{
                    data: chartData.species_count.data,
                    backgroundColor: [
                        '#10b981',
                        '#06b6d4',
                        '#3b82f6',
                        '#8b5cf6',
                        '#f59e0b'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    }

    // Genetic Diversity Chart
    const geneticCtx = document.getElementById('geneticChart');
    if (geneticCtx && typeof chartData !== 'undefined') {
        new Chart(geneticCtx, {
            type: 'bar',
            data: {
                labels: chartData.genetic_diversity.labels,
                datasets: [{
                    label: 'Diversity Index',
                    data: chartData.genetic_diversity.data,
                    backgroundColor: '#06b6d4',
                    borderColor: '#0891b2',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 1,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }
}

function initializeHeatmap() {
    const heatmapContainer = document.getElementById('heatmap-container');
    if (heatmapContainer && typeof heatmapData !== 'undefined') {
        heatmapContainer.innerHTML = '';
        
        heatmapData.forEach((row, rowIndex) => {
            const rowDiv = document.createElement('div');
            rowDiv.className = 'flex gap-1';
            
            row.forEach((value, colIndex) => {
                const cell = document.createElement('div');
                cell.className = 'heatmap-cell w-8 h-8 rounded cursor-pointer tooltip';
                
                // Calculate color intensity based on value
                const intensity = Math.floor(value * 255);
                const blueValue = 200 + Math.floor(value * 55); // Range from 200 to 255
                cell.style.backgroundColor = `rgb(${255 - intensity}, ${255 - intensity}, ${blueValue})`;
                
                // Add tooltip
                cell.setAttribute('data-tooltip', `Diversity: ${(value * 100).toFixed(1)}%`);
                
                // Add hover effect
                cell.addEventListener('mouseenter', function() {
                    this.style.transform = 'scale(1.1)';
                    this.style.zIndex = '10';
                });
                
                cell.addEventListener('mouseleave', function() {
                    this.style.transform = 'scale(1)';
                    this.style.zIndex = '1';
                });
                
                rowDiv.appendChild(cell);
            });
            
            heatmapContainer.appendChild(rowDiv);
        });
    }
}

// Update charts when tab is switched
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('tab-btn')) {
        // Small delay to ensure tab content is visible before updating charts
        setTimeout(() => {
            const activeTab = e.target.getAttribute('data-tab');
            if (activeTab === 'genomic') {
                // Reinitialize genetic chart if needed
                const geneticCtx = document.getElementById('geneticChart');
                if (geneticCtx && geneticCtx.getContext) {
                    // Chart.js will handle the resize automatically
                }
            }
        }, 100);
    }
});