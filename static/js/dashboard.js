// Dashboard JavaScript Functions
// Secure Password Manager - Button Event Handlers

console.log('Dashboard JavaScript file loaded');

// Search functionality
function initializeSearch() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase().trim();
            const passwordItems = document.querySelectorAll('.password-item');
            const noResults = document.getElementById('noResults');
            let visibleCount = 0;

            passwordItems.forEach(function(item) {
                const service = item.dataset.service;
                const username = item.dataset.username;
                const url = item.dataset.url;
                
                const isMatch = service.includes(searchTerm) || 
                               username.includes(searchTerm) || 
                               url.includes(searchTerm);
                
                if (isMatch) {
                    item.style.display = 'block';
                    visibleCount++;
                } else {
                    item.style.display = 'none';
                }
            });

            // Show/hide no results message
            if (noResults) {
                if (visibleCount === 0 && searchTerm !== '') {
                    noResults.style.display = 'block';
                } else {
                    noResults.style.display = 'none';
                }
            }
        });
    }
}

// Password visibility toggle
function togglePasswordVisibility(fieldId) {
    console.log('togglePasswordVisibility called with fieldId:', fieldId);
    const field = document.getElementById(fieldId);
    if (!field) {
        console.error('Password field not found:', fieldId);
        return;
    }
    
    const button = field.nextElementSibling;
    const icon = button.querySelector('i');
    
    if (field.type === 'password') {
        field.type = 'text';
        icon.classList.remove('bi-eye');
        icon.classList.add('bi-eye-slash');
        console.log('Password shown for field:', fieldId);
    } else {
        field.type = 'password';
        icon.classList.remove('bi-eye-slash');
        icon.classList.add('bi-eye');
        console.log('Password hidden for field:', fieldId);
    }
}

// Show all passwords
function showAllPasswords() {
    console.log('showAllPasswords called');
    const passwordFields = document.querySelectorAll('.password-field');
    passwordFields.forEach(function(field) {
        field.type = 'text';
        const button = field.nextElementSibling;
        const icon = button.querySelector('i');
        icon.classList.remove('bi-eye');
        icon.classList.add('bi-eye-slash');
    });
}

// Hide all passwords
function hideAllPasswords() {
    console.log('hideAllPasswords called');
    const passwordFields = document.querySelectorAll('.password-field');
    passwordFields.forEach(function(field) {
        field.type = 'password';
        const button = field.nextElementSibling;
        const icon = button.querySelector('i');
        icon.classList.remove('bi-eye-slash');
        icon.classList.add('bi-eye');
    });
}

// Copy to clipboard functionality
function copyToClipboard(text, button) {
    console.log('copyToClipboard called with text length:', text.length);
    console.log('Button element:', button);
    
    if (!navigator.clipboard) {
        console.warn('Clipboard API not available, using fallback');
        copyToClipboardFallback(text, button);
        return;
    }
    
    navigator.clipboard.writeText(text).then(function() {
        console.log('Text copied successfully');
        // Store original icon
        const icon = button.querySelector('i');
        const originalClass = icon.className;
        
        // Change to success icon
        icon.className = 'bi bi-check-circle-fill text-success';
        button.classList.add('btn-success');
        button.classList.remove('btn-outline-primary');
        
        // Show success feedback
        if (typeof bootstrap !== 'undefined') {
            const tooltip = new bootstrap.Tooltip(button, {
                title: 'Copied!',
                trigger: 'manual'
            });
            tooltip.show();
            
            // Reset after 2 seconds
            setTimeout(function() {
                icon.className = originalClass;
                button.classList.remove('btn-success');
                button.classList.add('btn-outline-primary');
                tooltip.dispose();
            }, 2000);
        } else {
            // Reset after 2 seconds without tooltip
            setTimeout(function() {
                icon.className = originalClass;
                button.classList.remove('btn-success');
                button.classList.add('btn-outline-primary');
            }, 2000);
        }
    }).catch(function(err) {
        console.error('Failed to copy text: ', err);
        copyToClipboardFallback(text, button);
    });
}

function copyToClipboardFallback(text, button) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.opacity = '0';
    document.body.appendChild(textArea);
    textArea.select();
    
    try {
        const successful = document.execCommand('copy');
        console.log('Fallback copy result:', successful);
        if (successful) {
            // Show success feedback
            const icon = button.querySelector('i');
            const originalClass = icon.className;
            icon.className = 'bi bi-check-circle-fill text-success';
            
            setTimeout(function() {
                icon.className = originalClass;
            }, 2000);
        }
    } catch (err) {
        console.error('Fallback copy failed:', err);
        alert('Unable to copy password. Please copy manually.');
    }
    
    document.body.removeChild(textArea);
}

// Delete confirmation
function confirmDelete(passwordId, serviceName) {
    console.log('confirmDelete called with passwordId:', passwordId, 'serviceName:', serviceName);
    
    const serviceElement = document.getElementById('serviceToDelete');
    const deleteForm = document.getElementById('deleteForm');
    
    if (!serviceElement || !deleteForm) {
        console.error('Modal elements not found');
        return;
    }
    
    serviceElement.textContent = serviceName;
    deleteForm.action = '/delete_password/' + passwordId;
    
    console.log('Delete form action set to:', deleteForm.action);
    
    // Check if Bootstrap is available
    if (typeof bootstrap === 'undefined') {
        console.error('Bootstrap is not loaded');
        if (confirm('Are you sure you want to delete the password for ' + serviceName + '?')) {
            deleteForm.submit();
        }
        return;
    }
    
    const modal = new bootstrap.Modal(document.getElementById('deleteModal'));
    modal.show();
    console.log('Delete modal shown');
}

// Auto-hide passwords after 30 seconds for security
let passwordVisibilityTimer;

function startPasswordVisibilityTimer() {
    clearTimeout(passwordVisibilityTimer);
    passwordVisibilityTimer = setTimeout(function() {
        hideAllPasswords();
    }, 30000); // 30 seconds
}

// Set up event listeners for all buttons
function setupEventListeners() {
    console.log('Setting up event listeners...');
    
    // Password visibility toggle buttons
    document.querySelectorAll('.toggle-password-btn').forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.dataset.target;
            console.log('Toggle button clicked for:', targetId);
            togglePasswordVisibility(targetId);
            startPasswordVisibilityTimer();
        });
    });
    
    // Copy password buttons
    document.querySelectorAll('.copy-password-btn').forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const password = this.dataset.password;
            console.log('Copy button clicked for password length:', password.length);
            copyToClipboard(password, this);
        });
    });
    
    // Delete password buttons
    document.querySelectorAll('.delete-password-btn').forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const passwordId = this.dataset.passwordId;
            const serviceName = this.dataset.serviceName;
            console.log('Delete button clicked for:', serviceName);
            confirmDelete(passwordId, serviceName);
        });
    });
    
    // Show all passwords button
    document.querySelectorAll('.show-all-btn').forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Show all button clicked');
            showAllPasswords();
        });
    });
    
    // Hide all passwords button
    document.querySelectorAll('.hide-all-btn').forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Hide all button clicked');
            hideAllPasswords();
        });
    });
    
    console.log('Event listeners setup complete');
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard JavaScript loaded successfully');
    
    // Test if functions are defined
    console.log('togglePasswordVisibility function exists:', typeof togglePasswordVisibility === 'function');
    console.log('copyToClipboard function exists:', typeof copyToClipboard === 'function');
    console.log('confirmDelete function exists:', typeof confirmDelete === 'function');
    console.log('showAllPasswords function exists:', typeof showAllPasswords === 'function');
    console.log('hideAllPasswords function exists:', typeof hideAllPasswords === 'function');
    
    // Test Bootstrap availability
    console.log('Bootstrap available:', typeof bootstrap !== 'undefined');
    
    // Initialize search functionality
    initializeSearch();
    
    // Set up event listeners for buttons
    setupEventListeners();
    
    // Initialize tooltips
    try {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[title]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    } catch (err) {
        console.warn('Could not initialize tooltips:', err);
    }
    
    // Test button functionality - count found buttons
    const passwordButtons = document.querySelectorAll('.toggle-password-btn');
    console.log('Found password visibility buttons:', passwordButtons.length);
    
    const copyButtons = document.querySelectorAll('.copy-password-btn');
    console.log('Found copy buttons:', copyButtons.length);
    
    const deleteButtons = document.querySelectorAll('.delete-password-btn');
    console.log('Found delete buttons:', deleteButtons.length);
    
    const showAllButtons = document.querySelectorAll('.show-all-btn');
    console.log('Found show all buttons:', showAllButtons.length);
    
    const hideAllButtons = document.querySelectorAll('.hide-all-btn');
    console.log('Found hide all buttons:', hideAllButtons.length);
    
    console.log('Dashboard initialization complete!');
});
