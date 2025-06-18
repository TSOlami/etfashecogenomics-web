// Main JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initializeTooltips();

    // Set initial active tab
    showTab('overview');
});

// Tab functionality
function showTab(tabName, event) {
    // Get all tab buttons and content sections
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    const currentButton = event ? event.currentTarget : document.querySelector(`[onclick*="showTab('${tabName}"]`);

    // Remove active class from all buttons and content sections
    tabButtons.forEach(btn => {
        btn.classList.remove('active');
        btn.classList.remove('border-emerald-500', 'text-emerald-600');
        btn.classList.add('border-transparent', 'text-gray-500');
    });

    tabContents.forEach(content => {
        content.classList.remove('active');
    });

    // Add active class to clicked button
    if (currentButton) {
        currentButton.classList.add('active');
        currentButton.classList.add('border-emerald-500', 'text-emerald-600');
        currentButton.classList.remove('border-transparent', 'text-gray-500');
    }

    // Show selected tab content
    const selectedTab = document.getElementById(tabName);
    if (selectedTab) {
        selectedTab.classList.add('active');
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