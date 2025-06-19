// Main JavaScript functionality - Enhanced for Real Data Integration
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing EcoGenomics dashboard...');
    
    // Initialize tooltips
    initializeTooltips();
    
    // Set initial active tab
    setInitialActiveTab();
    
    // Initialize charts after a short delay
    setTimeout(() => {
        initializeAllCharts();
    }, 200);
    
    // Initialize upload functionality
    initializeUploadFunctionality();
    
    // Initialize analysis functionality
    initializeAnalysisFunctionality();
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
                    },
                    title: {
                        display: true,
                        text: 'Temperature Trend'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        },
                        title: {
                            display: true,
                            text: 'Temperature (°C)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    }
                }
            }
        });
    }

    // Pollution levels chart
    const pollutionCtx = document.getElementById('pollutionChart');
    if (pollutionCtx && typeof chartData !== 'undefined') {
        console.log('Creating pollution levels chart...');
        
        // Destroy existing chart if it exists
        if (window.pollutionChart) {
            window.pollutionChart.destroy();
        }
        
        window.pollutionChart = new Chart(pollutionCtx, {
            type: 'bar',
            data: {
                labels: chartData.pollution_levels.labels,
                datasets: [{
                    label: 'Concentration (µg/m³)',
                    data: chartData.pollution_levels.data,
                    backgroundColor: [
                        '#ef4444', '#f97316', '#eab308', '#22c55e', '#3b82f6'
                    ],
                    borderColor: [
                        '#dc2626', '#ea580c', '#ca8a04', '#16a34a', '#2563eb'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Average Pollution Levels'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Concentration (µg/m³)'
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
    if (airQualityCtx && typeof chartData !== 'undefined') {
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
                labels: chartData.air_quality_trend.labels,
                datasets: [{
                    label: 'Air Quality Index',
                    data: chartData.air_quality_trend.data,
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
                    },
                    title: {
                        display: true,
                        text: 'Air Quality Index Trend'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0,0,0,0.05)'
                        },
                        title: {
                            display: true,
                            text: 'AQI Value'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: 'Date'
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
    
    // Mutation by distance chart
    const mutationCtx = document.getElementById('mutationChart');
    if (mutationCtx && typeof chartData !== 'undefined') {
        console.log('Creating mutation by distance chart...');
        
        // Destroy existing chart if it exists
        if (window.mutationChart) {
            window.mutationChart.destroy();
        }
        
        window.mutationChart = new Chart(mutationCtx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Mutations vs Distance',
                    data: chartData.mutation_by_distance.labels.map((label, index) => ({
                        x: parseFloat(label.replace('m', '')),
                        y: chartData.mutation_by_distance.data[index]
                    })),
                    backgroundColor: '#8b5cf6',
                    borderColor: '#7c3aed',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Mutations vs Distance from Pollution Source'
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Distance from Source (m)'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Mutations'
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

        // Generate heatmap data (this could be from real data)
        for (let i = 0; i < numRows * numCols; i++) {
            const cell = document.createElement('div');
            const value = Math.random();
            const hue = value > 0.66 ? 'from-red-500 to-red-600' :
                       value > 0.33 ? 'from-yellow-500 to-yellow-600' :
                       'from-emerald-500 to-emerald-600';
            
            cell.className = `w-full h-full rounded bg-gradient-to-br ${hue}`;
            cell.setAttribute('data-tooltip', `Expression: ${(value * 100).toFixed(1)}%`);
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

// Initialize upload functionality
function initializeUploadFunctionality() {
    console.log('Initializing upload functionality...');
    
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('fileInput');
    const fileTypeSelect = document.getElementById('fileType');
    const uploadProgress = document.getElementById('uploadProgress');
    const uploadStatus = document.getElementById('uploadStatus');
    
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleFileUpload();
        });
    }
    
    // Template download buttons
    const templateButtons = document.querySelectorAll('[data-template]');
    templateButtons.forEach(button => {
        button.addEventListener('click', function() {
            const templateType = this.getAttribute('data-template');
            downloadTemplate(templateType);
        });
    });
}

// Handle file upload
function handleFileUpload() {
    const fileInput = document.getElementById('fileInput');
    const fileTypeSelect = document.getElementById('fileType');
    const uploadProgress = document.getElementById('uploadProgress');
    const uploadStatus = document.getElementById('uploadStatus');
    
    if (!fileInput.files.length) {
        showUploadStatus('Please select a file to upload.', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('file_type', fileTypeSelect.value);
    
    // Show progress
    if (uploadProgress) {
        uploadProgress.style.display = 'block';
    }
    showUploadStatus('Uploading and processing file...', 'info');
    
    fetch('/upload/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (uploadProgress) {
            uploadProgress.style.display = 'none';
        }
        
        if (data.success) {
            showUploadStatus(data.message, 'success');
            // Refresh dashboard data
            setTimeout(() => {
                location.reload();
            }, 2000);
        } else {
            showUploadStatus(data.error || 'Upload failed', 'error');
        }
    })
    .catch(error => {
        if (uploadProgress) {
            uploadProgress.style.display = 'none';
        }
        showUploadStatus('Upload failed: ' + error.message, 'error');
    });
}

// Show upload status
function showUploadStatus(message, type) {
    const uploadStatus = document.getElementById('uploadStatus');
    if (uploadStatus) {
        uploadStatus.textContent = message;
        uploadStatus.className = `mt-2 text-sm ${
            type === 'success' ? 'text-green-600' :
            type === 'error' ? 'text-red-600' :
            'text-blue-600'
        }`;
        uploadStatus.style.display = 'block';
    }
}

// Download template
function downloadTemplate(templateType) {
    window.location.href = `/download-template/${templateType}/`;
}

// Initialize analysis functionality
function initializeAnalysisFunctionality() {
    console.log('Initializing analysis functionality...');
    
    const analysisButtons = document.querySelectorAll('[data-analysis]');
    analysisButtons.forEach(button => {
        button.addEventListener('click', function() {
            const analysisType = this.getAttribute('data-analysis');
            const dataset = this.getAttribute('data-dataset') || 'environmental';
            runAnalysis(analysisType, dataset);
        });
    });
}

// Run analysis
function runAnalysis(analysisType, dataset, parameters = {}) {
    console.log(`Running ${analysisType} analysis on ${dataset} data...`);
    
    const analysisStatus = document.getElementById('analysisStatus');
    if (analysisStatus) {
        analysisStatus.textContent = 'Running analysis...';
        analysisStatus.className = 'text-blue-600';
        analysisStatus.style.display = 'block';
    }
    
    fetch('/api/analysis/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            analysis_type: analysisType,
            dataset: dataset,
            parameters: parameters
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayAnalysisResults(data.results);
            if (analysisStatus) {
                analysisStatus.textContent = 'Analysis completed successfully!';
                analysisStatus.className = 'text-green-600';
            }
        } else {
            if (analysisStatus) {
                analysisStatus.textContent = 'Analysis failed: ' + (data.error || 'Unknown error');
                analysisStatus.className = 'text-red-600';
            }
        }
    })
    .catch(error => {
        if (analysisStatus) {
            analysisStatus.textContent = 'Analysis failed: ' + error.message;
            analysisStatus.className = 'text-red-600';
        }
    });
}

// Display analysis results
function displayAnalysisResults(results) {
    const resultsContainer = document.getElementById('analysisResults');
    if (!resultsContainer) return;
    
    let html = '<div class="bg-white p-4 rounded-lg shadow mt-4">';
    html += '<h3 class="text-lg font-semibold mb-3">Analysis Results</h3>';
    
    if (results.error) {
        html += `<p class="text-red-600">${results.error}</p>`;
    } else {
        html += '<div class="space-y-2">';
        html += formatAnalysisResults(results);
        html += '</div>';
    }
    
    html += '</div>';
    resultsContainer.innerHTML = html;
}

// Format analysis results for display
function formatAnalysisResults(results) {
    let html = '';
    
    // Handle different types of results
    if (results.summary) {
        html += '<h4 class="font-medium">Summary</h4>';
        html += '<ul class="list-disc list-inside ml-4">';
        for (const [key, value] of Object.entries(results.summary)) {
            html += `<li>${key.replace('_', ' ')}: ${value}</li>`;
        }
        html += '</ul>';
    }
    
    if (results.violations && results.violations.length > 0) {
        html += '<h4 class="font-medium mt-3">Pollution Violations</h4>';
        html += '<ul class="list-disc list-inside ml-4 text-red-600">';
        results.violations.forEach(violation => {
            html += `<li>${violation.location}: ${violation.violation}</li>`;
        });
        html += '</ul>';
    }
    
    if (results.correlations) {
        html += '<h4 class="font-medium mt-3">Correlations</h4>';
        html += '<ul class="list-disc list-inside ml-4">';
        results.correlations.forEach(corr => {
            html += `<li>${corr.parameter1} vs ${corr.parameter2}: ${corr.correlation.toFixed(3)} (${corr.strength})</li>`;
        });
        html += '</ul>';
    }
    
    return html;
}

// Utility functions
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

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

// Export functions for global access
window.showTab = showTab;
window.runAnalysis = runAnalysis;
window.handleFileUpload = handleFileUpload;
window.downloadTemplate = downloadTemplate;