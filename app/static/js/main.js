// Main JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initializeTooltips();

    // Set initial active tab
    showTab('overview');
    
    // Initialize charts after DOM is loaded
    setTimeout(initializeCharts, 100);
});

// Tab functionality - matches demo behavior
function showTab(tabName, event) {
    // Get all tab buttons and content sections
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    // Remove active class from all buttons and content sections
    tabButtons.forEach(btn => {
        btn.classList.remove('active');
        btn.classList.remove('border-emerald-500', 'text-emerald-600', 'bg-emerald-50');
        btn.classList.add('border-transparent', 'text-gray-500', 'hover:text-gray-700', 'hover:border-gray-300');
    });

    tabContents.forEach(content => {
        content.classList.remove('active');
        content.style.display = 'none';
    });

    // Find the clicked button
    let currentButton;
    if (event) {
        currentButton = event.currentTarget;
    } else {
        // Find button by data-tab attribute or onclick content
        currentButton = document.querySelector(`[data-tab="${tabName}"]`) || 
                      document.querySelector(`[onclick*="'${tabName}'"]`);
    }

    // Add active class to clicked button
    if (currentButton) {
        currentButton.classList.add('active');
        currentButton.classList.add('border-emerald-500', 'text-emerald-600', 'bg-emerald-50');
        currentButton.classList.remove('border-transparent', 'text-gray-500', 'hover:text-gray-700', 'hover:border-gray-300');
    }

    // Show selected tab content
    const selectedTab = document.getElementById(tabName);
    if (selectedTab) {
        selectedTab.classList.add('active');
        selectedTab.style.display = 'block';
    }

    // Reinitialize charts for the active tab
    setTimeout(() => {
        if (tabName === 'overview') {
            initializeOverviewCharts();
        } else if (tabName === 'genomic') {
            initializeGenomicCharts();
        } else if (tabName === 'biodiversity') {
            initializeHeatmap();
        }
    }, 100);
}

// Initialize all charts
function initializeCharts() {
    initializeOverviewCharts();
    initializeGenomicCharts();
    initializeHeatmap();
}

// Initialize overview tab charts
function initializeOverviewCharts() {
    // Temperature trend chart
    const tempCtx = document.getElementById('temperatureChart');
    if (tempCtx && typeof chartData !== 'undefined') {
        // Destroy existing chart if it exists
        if (window.temperatureChart) {
            window.temperatureChart.destroy();
        }
        
        window.temperatureChart = new Chart(tempCtx, {
            type: 'line',
            data: {
                labels: chartData.temperature_trend.labels,
                datasets: [{
                    label: 'Temperature (°C)',
                    data: chartData.temperature_trend.data,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
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

    // Species count chart
    const speciesCtx = document.getElementById('speciesChart');
    if (speciesCtx && typeof chartData !== 'undefined') {
        // Destroy existing chart if it exists
        if (window.speciesChart) {
            window.speciesChart.destroy();
        }
        
        window.speciesChart = new Chart(speciesCtx, {
            type: 'doughnut',
            data: {
                labels: chartData.species_count.labels,
                datasets: [{
                    data: chartData.species_count.data,
                    backgroundColor: [
                        '#10b981',
                        '#06b6d4',
                        '#8b5cf6',
                        '#f59e0b',
                        '#ef4444'
                    ]
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
}

// Initialize genomic tab charts
function initializeGenomicCharts() {
    const geneticCtx = document.getElementById('geneticChart');
    if (geneticCtx && typeof chartData !== 'undefined') {
        // Destroy existing chart if it exists
        if (window.geneticChart) {
            window.geneticChart.destroy();
        }
        
        window.geneticChart = new Chart(geneticCtx, {
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

    // Monthly samples chart
    const samplesCtx = document.getElementById('samplesChart');
    if (samplesCtx && typeof chartData !== 'undefined') {
        // Destroy existing chart if it exists
        if (window.samplesChart) {
            window.samplesChart.destroy();
        }
        
        window.samplesChart = new Chart(samplesCtx, {
            type: 'line',
            data: {
                labels: chartData.monthly_samples.labels,
                datasets: [{
                    label: 'Monthly Samples',
                    data: chartData.monthly_samples.data,
                    borderColor: '#8b5cf6',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
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

// Initialize heatmap
function initializeHeatmap() {
    const heatmapContainer = document.getElementById('heatmap-container');
    if (heatmapContainer && typeof heatmapData !== 'undefined') {
        heatmapContainer.innerHTML = '';
        
        heatmapData.forEach((row, rowIndex) => {
            const rowDiv = document.createElement('div');
            rowDiv.className = 'flex gap-1';
            
            row.forEach((value, colIndex) => {
                const cell = document.createElement('div');
                cell.className = 'heatmap-cell w-8 h-8 rounded cursor-pointer transition-all duration-200 hover:scale-110';
                
                // Calculate color intensity based on value
                const intensity = Math.floor(value * 255);
                const blueValue = 200 + Math.floor(value * 55); // Range from 200 to 255
                cell.style.backgroundColor = `rgb(${255 - intensity}, ${255 - intensity}, ${blueValue})`;
                
                // Add tooltip
                cell.setAttribute('data-tooltip', `Diversity: ${(value * 100).toFixed(1)}%`);
                
                rowDiv.appendChild(cell);
            });
            
            heatmapContainer.appendChild(rowDiv);
        });
    }
}

// Tooltip functionality
function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            const tooltipText = this.getAttribute('data-tooltip');
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip-popup';
            tooltip.textContent = tooltipText;
            tooltip.style.cssText = `
                position: absolute;
                background: #333;
                color: white;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 12px;
                z-index: 1000;
                pointer-events: none;
                white-space: nowrap;
            `;
            
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
            tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
            
            this._tooltip = tooltip;
        });
        
        element.addEventListener('mouseleave', function() {
            if (this._tooltip) {
                document.body.removeChild(this._tooltip);
                this._tooltip = null;
            }
        });
    });
}

// Utility functions
function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}

function getStatusColor(status) {
    const statusColors = {
        'normal': 'text-emerald-600',
        'optimal': 'text-emerald-600',
        'good': 'text-emerald-600',
        'clear': 'text-emerald-600',
        'warning': 'text-yellow-600',
        'critical': 'text-red-600'
    };
    return statusColors[status.toLowerCase()] || 'text-gray-600';
}