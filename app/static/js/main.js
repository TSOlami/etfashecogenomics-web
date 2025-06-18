// Main JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initializeTooltips();

    // Set initial active tab
    showTab('overview');
    
    // Initialize charts after DOM is loaded
    setTimeout(initializeCharts, 100);
    
    // Add smooth animations
    addSmoothAnimations();
});

// Tab functionality - Enhanced with beautiful transitions
function showTab(tabName, event) {
    // Get all tab buttons and content sections
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    // Remove active class from all buttons
    tabButtons.forEach(btn => {
        btn.classList.remove('active');
        // Reset to default styles
        btn.style.background = '';
        btn.style.color = '';
        btn.style.transform = '';
        btn.style.boxShadow = '';
    });

    // Hide all tab contents with fade effect
    tabContents.forEach(content => {
        content.classList.remove('active');
        content.style.display = 'none';
        content.style.opacity = '0';
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

    // Add active class to clicked button with enhanced styling
    if (currentButton) {
        currentButton.classList.add('active');
    }

    // Show selected tab content with fade in effect
    const selectedTab = document.getElementById(tabName);
    if (selectedTab) {
        selectedTab.classList.add('active');
        selectedTab.style.display = 'block';
        
        // Fade in animation
        setTimeout(() => {
            selectedTab.style.opacity = '1';
            selectedTab.style.transition = 'opacity 0.3s ease-in-out';
        }, 10);
    }

    // Reinitialize charts for the active tab with delay for smooth transition
    setTimeout(() => {
        if (tabName === 'overview') {
            initializeOverviewCharts();
        } else if (tabName === 'genomic') {
            initializeGenomicCharts();
        } else if (tabName === 'biodiversity') {
            initializeHeatmap();
        }
    }, 150);
}

// Initialize all charts
function initializeCharts() {
    initializeOverviewCharts();
    initializeGenomicCharts();
    initializeHeatmap();
}

// Initialize overview tab charts with enhanced styling
function initializeOverviewCharts() {
    // Temperature trend chart
    const tempCtx = document.getElementById('temperatureChart');
    if (tempCtx && typeof chartData !== 'undefined') {
        // Destroy existing chart if it exists
        if (window.temperatureChart) {
            window.temperatureChart.destroy();
        }
        
        const gradient = tempCtx.getContext('2d').createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, 'rgba(16, 185, 129, 0.3)');
        gradient.addColorStop(1, 'rgba(16, 185, 129, 0.05)');
        
        window.temperatureChart = new Chart(tempCtx, {
            type: 'line',
            data: {
                labels: chartData.temperature_trend.labels,
                datasets: [{
                    label: 'Temperature (°C)',
                    data: chartData.temperature_trend.data,
                    borderColor: '#10b981',
                    backgroundColor: gradient,
                    tension: 0.4,
                    fill: true,
                    borderWidth: 3,
                    pointBackgroundColor: '#10b981',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
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
                            color: 'rgba(0, 0, 0, 0.05)',
                            drawBorder: false
                        },
                        ticks: {
                            color: '#6b7280'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: '#6b7280'
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
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
                    ],
                    borderWidth: 0,
                    hoverBorderWidth: 3,
                    hoverBorderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '60%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            color: '#374151',
                            font: {
                                size: 12,
                                weight: '500'
                            }
                        }
                    }
                }
            }
        });
    }
}

// Initialize genomic tab charts with enhanced styling
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
                    borderWidth: 0,
                    borderRadius: 8,
                    borderSkipped: false,
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
                            color: 'rgba(0, 0, 0, 0.05)',
                            drawBorder: false
                        },
                        ticks: {
                            color: '#6b7280'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: '#6b7280'
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
        
        const gradient = samplesCtx.getContext('2d').createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, 'rgba(139, 92, 246, 0.3)');
        gradient.addColorStop(1, 'rgba(139, 92, 246, 0.05)');
        
        window.samplesChart = new Chart(samplesCtx, {
            type: 'line',
            data: {
                labels: chartData.monthly_samples.labels,
                datasets: [{
                    label: 'Monthly Samples',
                    data: chartData.monthly_samples.data,
                    borderColor: '#8b5cf6',
                    backgroundColor: gradient,
                    tension: 0.4,
                    fill: true,
                    borderWidth: 3,
                    pointBackgroundColor: '#8b5cf6',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
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
                            color: 'rgba(0, 0, 0, 0.05)',
                            drawBorder: false
                        },
                        ticks: {
                            color: '#6b7280'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: '#6b7280'
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
    }
}

// Initialize heatmap with enhanced interactivity
function initializeHeatmap() {
    const heatmapContainer = document.getElementById('heatmap-container');
    if (heatmapContainer && typeof heatmapData !== 'undefined') {
        heatmapContainer.innerHTML = '';
        
        heatmapData.forEach((row, rowIndex) => {
            row.forEach((value, colIndex) => {
                const cell = document.createElement('div');
                cell.className = 'heatmap-cell';
                
                // Calculate color intensity based on value with enhanced gradient
                const intensity = Math.floor(value * 255);
                const blueValue = 200 + Math.floor(value * 55); // Range from 200 to 255
                const greenValue = 255 - Math.floor(value * 100); // Subtle green tint
                cell.style.backgroundColor = `rgb(${greenValue}, ${255 - intensity}, ${blueValue})`;
                
                // Add tooltip with enhanced information
                cell.setAttribute('data-tooltip', `Region ${rowIndex + 1}-${colIndex + 1}: ${(value * 100).toFixed(1)}% Diversity`);
                
                // Add click event for detailed view
                cell.addEventListener('click', function() {
                    showDetailedView(rowIndex, colIndex, value);
                });
                
                heatmapContainer.appendChild(cell);
            });
        });
    }
}

// Show detailed view for heatmap cell
function showDetailedView(row, col, value) {
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="bg-white rounded-2xl p-8 max-w-md mx-4 shadow-2xl">
            <h3 class="text-xl font-bold text-gray-800 mb-4">Region ${row + 1}-${col + 1} Details</h3>
            <div class="space-y-3">
                <div class="flex justify-between">
                    <span class="text-gray-600">Biodiversity Index:</span>
                    <span class="font-semibold">${(value * 100).toFixed(1)}%</span>
                </div>
                <div class="flex justify-between">
                    <span class="text-gray-600">Species Count:</span>
                    <span class="font-semibold">${Math.floor(value * 150 + 50)}</span>
                </div>
                <div class="flex justify-between">
                    <span class="text-gray-600">Ecosystem Health:</span>
                    <span class="font-semibold ${value > 0.7 ? 'text-green-600' : value > 0.4 ? 'text-yellow-600' : 'text-red-600'}">
                        ${value > 0.7 ? 'Excellent' : value > 0.4 ? 'Good' : 'Needs Attention'}
                    </span>
                </div>
            </div>
            <button onclick="this.parentElement.parentElement.remove()" class="mt-6 w-full bg-gradient-to-r from-emerald-500 to-blue-500 text-white py-2 px-4 rounded-lg font-medium hover:from-emerald-600 hover:to-blue-600 transition-all duration-200">
                Close
            </button>
        </div>
    `;
    document.body.appendChild(modal);
}

// Enhanced tooltip functionality
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
                background: linear-gradient(135deg, rgba(0, 0, 0, 0.9), rgba(0, 0, 0, 0.8));
                color: white;
                padding: 8px 12px;
                border-radius: 8px;
                font-size: 12px;
                z-index: 1000;
                pointer-events: none;
                white-space: nowrap;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
                backdrop-filter: blur(10px);
                transform: translateY(-5px);
                opacity: 0;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            `;
            
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
            tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
            
            // Animate in
            setTimeout(() => {
                tooltip.style.opacity = '1';
                tooltip.style.transform = 'translateY(0)';
            }, 10);
            
            this._tooltip = tooltip;
        });
        
        element.addEventListener('mouseleave', function() {
            if (this._tooltip) {
                this._tooltip.style.opacity = '0';
                this._tooltip.style.transform = 'translateY(-5px)';
                setTimeout(() => {
                    if (this._tooltip && this._tooltip.parentNode) {
                        document.body.removeChild(this._tooltip);
                    }
                    this._tooltip = null;
                }, 300);
            }
        });
    });
}

// Add smooth animations to elements
function addSmoothAnimations() {
    // Animate cards on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe all cards and charts
    document.querySelectorAll('.card-shadow, .chart-container').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
        observer.observe(el);
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

// Add loading states for better UX
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '<div class="flex items-center justify-center h-32"><div class="animate-pulse text-gray-500">Loading...</div></div>';
    }
}

// Keyboard navigation support
document.addEventListener('keydown', function(e) {
    if (e.key === 'Tab') {
        document.body.classList.add('keyboard-navigation');
    }
});

document.addEventListener('mousedown', function() {
    document.body.classList.remove('keyboard-navigation');
});