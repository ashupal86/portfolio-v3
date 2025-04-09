/**
 * Comic Book Portfolio - Main JavaScript
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize variables
    let currentSection = null;
    let typingTimeout = null;
    const sections = document.querySelectorAll('section[id]');
    
    // Initialize Bootstrap tooltips and popovers if available
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
        
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }
    
    // === Section visibility is now handled by layout.html navigation script ===
    
    /**
     * Show only the target section and hide others
     * This is now only used for section-specific initialization
     */
    function showSection(targetSection) {
        if (!targetSection) return;
        
        // Initialize specific features based on the section
        initializeSectionFeatures(targetSection);
    }
    
    /**
     * Update active state in navbar
     * Note: This is now handled by layout.html navigation script
     */
    function updateActiveNav(activeLink) {
        // Left for compatibility, but actual navigation is handled in layout.html
        console.log('Active nav updated:', activeLink);
    }
    
    /**
     * Initialize section-specific features
     */
    function initializeSectionFeatures(section) {
        const sectionId = section.getAttribute('id');
        
        if (sectionId === 'about') {
            // Terminal typing effect for about section
            initializeTypingEffect();
        } else if (sectionId === 'skills') {
            // Animate skill bars
            animateSkillBars();
        } else if (sectionId === 'projects') {
            // Initialize project filters if present
            initializeProjectFilters();
        } else if (sectionId === 'achievements') {
            // No filter initialization needed anymore as we removed the filters
            // Just animate the achievement cards
            setupIntersectionObserver();
        }
        
        // Initialize skills section
        initializeSkillsSection();
    }
    
    /**
     * Terminal typing effect for about section
     */
    function initializeTypingEffect() {
        const aboutTerminal = document.querySelector('.about-terminal .terminal-text');
        if (!aboutTerminal) return;
        
        // Clear any previous typing timeout
        if (typingTimeout) clearTimeout(typingTimeout);
        
        const text = aboutTerminal.textContent;
        aboutTerminal.textContent = '';
        aboutTerminal.style.display = 'block';
        
        let i = 0;
        function typeNextChar() {
            if (i < text.length) {
                aboutTerminal.textContent += text.charAt(i);
                i++;
                
                // Random typing speed for realistic effect
                const randomSpeed = Math.floor(Math.random() * 40) + 20;
                typingTimeout = setTimeout(typeNextChar, randomSpeed);
            } else {
                // Add blinking cursor at the end
                const cursor = document.createElement('span');
                cursor.className = 'cursor-blink';
                cursor.textContent = '_';
                aboutTerminal.appendChild(cursor);
            }
        }
        
        typeNextChar();
    }
    
    /**
     * Animate skill bars
     */
    function animateSkillBars() {
        // For the minimal skill tags design
        const skillTags = document.querySelectorAll('.skill-tag');
        
        skillTags.forEach((tag, index) => {
            // Apply a staggered animation delay
            const delay = 50 + (index * 30);
            tag.style.opacity = '0';
            tag.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                tag.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                tag.style.opacity = '1';
                tag.style.transform = 'translateY(0)';
            }, delay);
        });
    }
    
    /**
     * Initialize project filters
     */
    function initializeProjectFilters() {
        const filterButtons = document.querySelectorAll('.project-filter');
        if (filterButtons.length === 0) return;
        
        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                const filterValue = this.getAttribute('data-filter');
                
                // Update active button state
                filterButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                
                // Filter projects
                const projects = document.querySelectorAll('.project-card');
                
                projects.forEach(project => {
                    if (filterValue === 'all') {
                        project.style.display = 'block';
                    } else {
                        // Check for both data-categories and data-category attributes
                        const projectCard = project.closest('[data-categories], [data-category]');
                        if (!projectCard) return;
                        
                        if (projectCard.hasAttribute('data-categories')) {
                            // Handle comma-separated categories
                            const projectCategories = projectCard.getAttribute('data-categories').split(',');
                            if (projectCategories.includes(filterValue)) {
                                project.style.display = 'block';
                            } else {
                                project.style.display = 'none';
                            }
                        } else if (projectCard.hasAttribute('data-category')) {
                            // Handle single category
                            const projectCategory = projectCard.getAttribute('data-category');
                            if (projectCategory === filterValue) {
                                project.style.display = 'block';
                            } else {
                                project.style.display = 'none';
                            }
                        }
                    }
                });
            });
        });

        // Also handle btn-filter class for project pages
        const btnFilterButtons = document.querySelectorAll('.btn-filter');
        if (btnFilterButtons.length === 0) return;
        
        btnFilterButtons.forEach(button => {
            button.addEventListener('click', function() {
                const filterValue = this.getAttribute('data-filter');
                
                // Update active button state
                btnFilterButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                
                // Filter projects
                const projectItems = document.querySelectorAll('.project-item');
                
                projectItems.forEach(item => {
                    if (filterValue === 'all' || item.getAttribute('data-category') === filterValue) {
                        item.style.display = 'block';
                    } else {
                        item.style.display = 'none';
                    }
                });
            });
        });
    }
    
    /**
     * Initialize Intersection Observer for animations
     */
    function setupIntersectionObserver() {
        if ('IntersectionObserver' in window) {
            const animatedElements = document.querySelectorAll('.animate-on-scroll');
            
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animated');
                        // Unobserve after animation
                        observer.unobserve(entry.target);
                    }
                });
            }, {
                threshold: 0.1
            });
            
            animatedElements.forEach(element => {
                observer.observe(element);
            });
        } else {
            // Fallback for browsers that don't support Intersection Observer
            document.querySelectorAll('.animate-on-scroll').forEach(element => {
                element.classList.add('animated');
            });
        }
    }
    
    /**
     * Contact form handling
     */
    function setupContactForm() {
        const contactForm = document.getElementById('contactForm');
        if (!contactForm) return;
        
        contactForm.addEventListener('submit', function(e) {
            // Forms are handled server-side, but we can add client-side validation here
            const formFields = contactForm.querySelectorAll('input, textarea');
            let isValid = true;
            
            formFields.forEach(field => {
                if (field.hasAttribute('required') && !field.value.trim()) {
                    isValid = false;
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                // Add comic book style validation message
                const alertBox = document.querySelector('.contact-alert') || document.createElement('div');
                alertBox.className = 'alert alert-danger contact-alert comic-panel';
                alertBox.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Oops! Please fill out all required fields.';
                
                if (!document.querySelector('.contact-alert')) {
                    contactForm.prepend(alertBox);
                }
            }
        });
    }
    
    /**
     * Handle image loading errors
     */
    function setupImageErrorHandling() {
        const projectImages = document.querySelectorAll('.project-img, .blog-img, img[src*="/static/img/"]');
        
        projectImages.forEach(img => {
            img.addEventListener('error', function() {
                // Replace broken image with a placeholder container
                const parent = this.parentElement;
                
                // Create placeholder div
                const placeholder = document.createElement('div');
                placeholder.className = this.className + ' image-placeholder d-flex align-items-center justify-content-center bg-dark';
                
                // Add appropriate icon based on image context
                let icon = document.createElement('i');
                
                if (this.src.includes('projects')) {
                    icon.className = 'fas fa-code fa-3x text-primary';
                } else if (this.src.includes('blog')) {
                    icon.className = 'fas fa-newspaper fa-3x text-primary';
                } else if (this.src.includes('achievements')) {
                    icon.className = 'fas fa-trophy fa-3x text-primary';
                } else {
                    icon.className = 'fas fa-image fa-3x text-primary';
                }
                
                placeholder.appendChild(icon);
                
                // Replace the image with the placeholder
                if (parent) {
                    parent.replaceChild(placeholder, this);
                }
            });
        });
    }
    
    /**
     * Setup Konami Code Easter Egg
     */
    function setupKonamiCodeEasterEgg() {
        // Konami code sequence: up, up, down, down, left, right, left, right, B, A
        const konamiCode = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'KeyB', 'KeyA'];
        let konamiIndex = 0;
        
        document.addEventListener('keydown', function(e) {
            // Check if the key matches the expected key in the sequence
            const expectedKey = konamiCode[konamiIndex];
            const pressedKey = e.code;
            
            if (pressedKey === expectedKey) {
                // Move to the next key in the sequence
                konamiIndex++;
                
                // Check if the entire sequence has been entered
                if (konamiIndex === konamiCode.length) {
                    activateAdminEasterEgg();
                    konamiIndex = 0; // Reset for next time
                }
            } else {
                // Reset the sequence if an incorrect key is pressed
                konamiIndex = 0;
            }
        });
        
        // Activate admin easter egg
        function activateAdminEasterEgg() {
            const adminLink = document.querySelector('.admin-easter-egg');
            if (adminLink) {
                adminLink.classList.add('activated');
                
                // Display a comic-style message
                const easterEggMessage = document.createElement('div');
                easterEggMessage.className = 'alert alert-success comic-panel fixed-bottom mb-0 text-center';
                easterEggMessage.style.zIndex = '9999';
                easterEggMessage.innerHTML = '<i class="fas fa-unlock-alt me-2"></i> <span class="bangers-font">Admin Mode Unlocked!</span> Click the terminal icon in the footer.';
                
                document.body.appendChild(easterEggMessage);
                
                // Remove the message after 5 seconds
                setTimeout(() => {
                    easterEggMessage.classList.add('fade-out');
                    setTimeout(() => {
                        document.body.removeChild(easterEggMessage);
                    }, 500);
                }, 5000);
                
                // Scroll to footer to show the admin link
                setTimeout(() => {
                    const footer = document.querySelector('footer');
                    if (footer) {
                        footer.scrollIntoView({ behavior: 'smooth' });
                    }
                }, 1000);
            }
        }
    }
    
    // Call setup functions
    // setupNavigation(); // Navigation is now handled in layout.html
    setupIntersectionObserver();
    setupContactForm();
    setupImageErrorHandling();
    setupKonamiCodeEasterEgg();
    
    // Handle theme toggle if present
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            document.body.classList.toggle('light-theme');
            
            // Store theme preference
            const isDarkTheme = !document.body.classList.contains('light-theme');
            localStorage.setItem('darkTheme', isDarkTheme);
            
            // Update toggle icon
            this.innerHTML = isDarkTheme ? 
                '<i class="fas fa-sun"></i>' : 
                '<i class="fas fa-moon"></i>';
        });
        
        // Check for saved theme preference
        const savedDarkTheme = localStorage.getItem('darkTheme') === 'true';
        if (!savedDarkTheme) {
            document.body.classList.add('light-theme');
            themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
        }
    }
    
    // Skills filter functionality
    function initializeSkillsSection() {
        // Animate skill tags when in view
        const animateSkillTags = () => {
            const skillTags = document.querySelectorAll('.skill-tag');
            skillTags.forEach((tag, index) => {
                // Apply a staggered animation delay
                setTimeout(() => {
                    tag.style.opacity = '1';
                    tag.style.transform = 'translateY(0)';
                }, 50 + (index * 30));
            });
        };
        
        // Use Intersection Observer to check when skills section is visible
        const skillsSection = document.getElementById('skills');
        if (skillsSection) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        animateSkillTags();
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.2 });
            
            observer.observe(skillsSection);
            
            // Set initial state for animation
            const skillTags = document.querySelectorAll('.skill-tag');
            skillTags.forEach(tag => {
                tag.style.opacity = '0';
                tag.style.transform = 'translateY(20px)';
                tag.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            });
        }
    }
    
    /**
     * Initialize achievement filters
     * Note: We no longer need this function as we removed the filters
     * Keeping an empty function for compatibility with existing code
     */
    function initializeAchievementFilters() {
        // Function intentionally left empty as filters were removed
    }
    
    /**
     * Initialize event filters
     * Note: We no longer need this function as we removed the events section
     * Keeping an empty function for compatibility with existing code
     */
    function initializeEventFilters() {
        // Function intentionally left empty as events section was removed
    }
}); 


