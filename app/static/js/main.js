// Main JavaScript functionality - Consolidated and Fixed
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing dashboard...');
    
    // Initialize tooltips
    initializeTooltips();
    
    // Set initial active tab
    setInitialActiveTab();
    
    // Initialize charts after a short delay
    setTimeout(() => {
        initializeAllCharts();
    }, 200);
});

// Set initial active tab state
function setInitialActiveTab() {
    console.log('Setting initial active tab...');
    
    // Hide all tab contents first
    const tabContents = document.querySelectorAll('.tab-content');
    console.log('Found tab contents:', tabContents.length);
    
    tabContents.forEach(content => {
        content.style.display = 'none';
        content.classList.remove('active');
    });

    // Remove active state from all tab buttons
    const tabButtons = document.querySelectorAll('.tab-btn');
    console.log('Found tab buttons:', tabButtons.length);
    
    tabButtons.forEach(btn => {
        btn.classList.remove('active', 'border-emerald-500', 'text-emerald-600');
        btn.classList.add('border-transparent', 'text-gray-500');
    });

    // Set overview tab as active
    const overviewButton = document.querySelector('[onclick*="overview"]');
    const overviewContent = document.getElementById('overview');
    
    console.log('Overview button found:', !!overviewButton);
    console.log('Overview content found:', !!overviewContent);
    
    if (overviewButton) {
        overviewButton.classList.add('active', 'border-emerald-500', 'text-emerald-600');
        overviewButton.classList.remove('border-transparent', 'text-gray-500');
    }
    
    if (overviewContent) {
        overviewContent.style.display = 'block';
        overviewContent.classList.add('active');
        console.log('Overview tab activated');
    }
}

// Tab functionality - Main function for switching tabs
function showTab(tabName, event) {
    console.log('Switching to tab:', tabName);
    
    // Get all tab buttons and content sections
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    console.log('Tab buttons found:', tabButtons.length);
    console.log('Tab contents found:', tabContents.length);

    // Hide all tab contents and remove active class
    tabContents.forEach(content => {
        content.style.display = 'none';
        content.classList.remove('active');
        console.log('Hiding content:', content.id);
    });

    // Remove active class from all buttons
    tabButtons.forEach(btn => {
        btn.classList.remove('active', 'border-emerald-500', 'text-emerald-600');
        btn.classList.add('border-transparent', 'text-gray-500');
    });

    // Find the clicked button
    let currentButton;
    if (event) {
        currentButton = event.currentTarget;
    } else {
        currentButton = document.querySelector(`[onclick*="'${tabName}'"]`);
    }

    // Add active class to clicked button
    if (currentButton) {
        currentButton.classList.add('active', 'border-emerald-500', 'text-emerald-600');
        currentButton.classList.remove('border-transparent', 'text-gray-500');
        console.log('Button activated:', currentButton);
    }

    // Show selected tab content
    const selectedTab = document.getElementById(tabName);
    if (selectedTab) {
        selectedTab.style.display = 'block';
        selectedTab.classList.add('active');
        console.log('Content shown for tab:', tabName);
    } else {
        console.error('Tab content not found for:', tabName);
    }

    // Reinitialize charts for the active tab
    setTimeout(() => {
        initializeChartsForTab(tabName);
    }, 100);
}

// Initialize charts for specific tab
function initializeChartsForTab(tabName) {
    console.log('Initializing charts for tab:', tabName);
    
    switch(tabName) {
        case 'overview':
            initializeOverviewCharts();
            break;
        case 'environmental':
            initializeEnvironmentalCharts();
            break;
        case 'bioinformatics':
            initializeGenomicCharts();
            break;
        case 'analytics':
            initializeHeatmap();
            break;
        default:
            console.log('No specific charts for tab:', tabName);
    }
}

// Initialize all charts
function initializeAllCharts() {
    console.log('Initializing all charts...');
    initializeOverviewCharts();
    initializeEnvironmentalCharts();
    initializeGenomicCharts();
    initializeHeatmap();
}

// Initialize overview tab charts
function initializeOverviewCharts() {
    console.log('Initializing overview charts...');
    
    // Temperature trend chart
    const tempCtx = document.getElementById('temperatureChart');
    if (tempCtx && typeof chartData !== 'undefined') {
        console.log('Creating temperature chart...');
        
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
        console.log('Creating species chart...');
        
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

// Initialize environmental monitoring charts
function initializeEnvironmentalCharts() {
    console.log('Initializing environmental charts...');
    
    const airQualityCtx = document.getElementById('airQualityChart');
    if (airQualityCtx) {
        console.log('Creating air quality chart...');
        
        // Destroy existing chart if it exists
        if (window.airQualityChart) {
            window.airQualityChart.destroy();
        }
        
        const gradient = airQualityCtx.getContext('2d').createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, 'rgba(16, 185, 129, 0.2)');
        gradient.addColorStop(1, 'rgba(16, 185, 129, 0.0)');

        window.airQualityChart = new Chart(airQualityCtx, {
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
    }
}

// Initialize genomic tab charts
function initializeGenomicCharts() {
    console.log('Initializing genomic charts...');
    
    const geneticCtx = document.getElementById('geneticChart');
    if (geneticCtx && typeof chartData !== 'undefined') {
        console.log('Creating genetic diversity chart...');
        
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
        console.log('Creating samples chart...');
        
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

    // Gene heatmap
    const geneHeatmapContainer = document.getElementById('geneHeatmap');
    if (geneHeatmapContainer) {
        console.log('Creating gene heatmap...');
        
        const numRows = 5;
        const numCols = 5;
        
        // Clear existing content
        geneHeatmapContainer.innerHTML = '';

        // Generate random heatmap data
        for (let i = 0; i < numRows * numCols; i++) {
            const cell = document.createElement('div');
            const value = Math.random();
            const hue = value > 0.66 ? 'from-red-500 to-red-600' :
                       value > 0.33 ? 'from-yellow-500 to-yellow-600' :
                       'from-emerald-500 to-emerald-600';
            
            cell.className = `w-full h-full rounded bg-gradient-to-br ${hue}`;
            geneHeatmapContainer.appendChild(cell);
        }
    }
}

// Initialize heatmap for analytics tab
function initializeHeatmap() {
    console.log('Initializing biodiversity heatmap...');
    
    const heatmapContainer = document.getElementById('heatmap-container');
    if (heatmapContainer && typeof heatmapData !== 'undefined') {
        console.log('Creating biodiversity heatmap...');
        
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

// Simple test function for debugging
function testTabSwitching() {
    console.log('Testing tab switching...');
    const tabs = ['overview', 'environmental', 'bioinformatics', 'analytics', 'reports'];
    
    tabs.forEach((tab, index) => {
        setTimeout(() => {
            console.log(`Testing tab: ${tab}`);
            showTab(tab);
        }, index * 1000);
    });
}