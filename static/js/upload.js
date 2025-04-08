/**
 * Image Upload Handling
 */

class ImageUploader {
    constructor(options = {}) {
        this.options = {
            uploadUrl: '/admin/upload',
            maxFileSize: 5 * 1024 * 1024, // 5MB default
            allowedTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/svg+xml'],
            csrfToken: null,
            onSuccess: null,
            onError: null,
            ...options
        };
        
        this.uploaderElements = document.querySelectorAll('.image-uploader');
        if (this.uploaderElements.length) {
            this.init();
        }
    }
    
    init() {
        this.uploaderElements.forEach(uploader => {
            const inputField = uploader.querySelector('input[type="file"]');
            const dropArea = uploader.querySelector('.drop-area');
            const previewContainer = uploader.querySelector('.image-preview');
            const hiddenInput = uploader.querySelector('input[type="hidden"]');
            
            if (inputField && dropArea) {
                // Click to upload
                dropArea.addEventListener('click', () => {
                    inputField.click();
                });
                
                // File selection changed
                inputField.addEventListener('change', (e) => {
                    const file = e.target.files[0];
                    if (file) {
                        this.validateAndUpload(file, previewContainer, hiddenInput);
                    }
                });
                
                // Drag and drop
                ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                    dropArea.addEventListener(eventName, (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                    });
                });
                
                // Add dragover visual effect
                dropArea.addEventListener('dragenter', () => {
                    dropArea.classList.add('dragover');
                });
                
                dropArea.addEventListener('dragover', () => {
                    dropArea.classList.add('dragover');
                });
                
                dropArea.addEventListener('dragleave', () => {
                    dropArea.classList.remove('dragover');
                });
                
                // Handle drop
                dropArea.addEventListener('drop', (e) => {
                    dropArea.classList.remove('dragover');
                    const file = e.dataTransfer.files[0];
                    if (file) {
                        this.validateAndUpload(file, previewContainer, hiddenInput);
                    }
                });
                
                // Show existing image if available
                if (hiddenInput && hiddenInput.value) {
                    this.showPreview(hiddenInput.value, previewContainer);
                }
            }
        });
    }
    
    validateAndUpload(file, previewContainer, hiddenInput) {
        // Check file type
        if (!this.options.allowedTypes.includes(file.type)) {
            this.showError('File type not allowed. Please upload an image file.');
            return;
        }
        
        // Check file size
        if (file.size > this.options.maxFileSize) {
            this.showError(`File too large. Maximum size is ${this.options.maxFileSize / (1024 * 1024)}MB.`);
            return;
        }
        
        // Show loading state
        if (previewContainer) {
            previewContainer.innerHTML = '<div class="upload-loading"><i class="fas fa-spinner fa-spin"></i></div>';
        }
        
        // Create form data
        const formData = new FormData();
        formData.append('file', file);
        
        // Add CSRF token if available
        if (this.options.csrfToken) {
            formData.append('csrf_token', this.options.csrfToken);
        }
        
        // Upload the file
        fetch(this.options.uploadUrl, {
            method: 'POST',
            body: formData,
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Show preview
                this.showPreview(data.filepath, previewContainer);
                
                // Set hidden input value
                if (hiddenInput) {
                    hiddenInput.value = data.filepath;
                }
                
                // Call success callback
                if (typeof this.options.onSuccess === 'function') {
                    this.options.onSuccess(data);
                }
            } else {
                this.showError(data.error || 'Upload failed');
            }
        })
        .catch(error => {
            this.showError('Upload failed: ' + error.message);
            
            // Call error callback
            if (typeof this.options.onError === 'function') {
                this.options.onError(error);
            }
        });
    }
    
    showPreview(filePath, previewContainer) {
        if (!previewContainer) return;
        
        const fullUrl = filePath.startsWith('http') ? filePath : `/static/${filePath}`;
        
        previewContainer.innerHTML = `
            <div class="preview-image-container">
                <img src="${fullUrl}" alt="Uploaded image" class="preview-image">
                <button type="button" class="remove-image"><i class="fas fa-times"></i></button>
            </div>
        `;
        
        // Add remove functionality
        const removeButton = previewContainer.querySelector('.remove-image');
        if (removeButton) {
            removeButton.addEventListener('click', () => {
                previewContainer.innerHTML = '';
                
                // Find and clear the hidden input
                const hiddenInput = previewContainer.closest('.image-uploader').querySelector('input[type="hidden"]');
                if (hiddenInput) {
                    hiddenInput.value = '';
                }
            });
        }
    }
    
    showError(message) {
        console.error('Upload error:', message);
        
        // Display error message
        const errorBox = document.createElement('div');
        errorBox.className = 'alert alert-danger';
        errorBox.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${message}`;
        
        document.querySelector('.upload-alert-container')?.appendChild(errorBox);
        
        // Remove after 5 seconds
        setTimeout(() => {
            errorBox.remove();
        }, 5000);
    }
}

// Initialize the uploader when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ImageUploader();
}); 