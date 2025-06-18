// Initialize charts when the document is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeAirQualityChart();
    initializeGeneHeatmap();
});

function initializeAirQualityChart() {
    const ctx = document.getElementById('airQualityChart');    if (ctx) {
        const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, 'rgba(16, 185, 129, 0.2)');
        gradient.addColorStop(1, 'rgba(16, 185, 129, 0.0)');

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
                datasets: [{
                    label: 'Air Quality Index',
                    data: [65, 78, 90, 85, 95, 110, 156],
                    borderColor: '#10b981',
                    backgroundColor: gradient,
                    tension: 0.4,
                    fill: true
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
                        grid: {
                            color: 'rgba(0,0,0,0.05)'
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
    }}

function initializeGeneHeatmap() {
    const heatmapContainer = document.getElementById('geneHeatmap');
    if (heatmapContainer) {
        const numRows = 5;
        const numCols = 5;
        
        // Clear existing content
        heatmapContainer.innerHTML = '';

        // Generate random heatmap data
        for (let i = 0; i < numRows * numCols; i++) {
            const cell = document.createElement('div');
            const value = Math.random();
            const hue = value > 0.66 ? 'from-red-500 to-red-600' :
                       value > 0.33 ? 'from-yellow-500 to-yellow-600' :
                       'from-emerald-500 to-emerald-600';
            
            cell.className = `w-full h-full rounded bg-gradient-to-br ${hue}`;
            heatmapContainer.appendChild(cell);
        }
    }
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