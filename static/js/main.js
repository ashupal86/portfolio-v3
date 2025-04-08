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
    
    // Setup achievement cards and modals
    setupAchievementCards();
    
    /**
     * Handle navigation link clicks for smooth scrolling and section display
     */
    function setupNavigation() {
        // Handle both in-page nav links and navbar links that point to sections
        const inPageNavLinks = document.querySelectorAll('.nav-link[href^="#"]');
        const navbarSectionLinks = document.querySelectorAll('.navbar-nav .nav-link[href*="#"]');
        
        // Function to extract section ID from href
        function getSectionId(href) {
            // Handle both "#section" and "index.html#section" type URLs
            const hashIndex = href.indexOf('#');
            if (hashIndex !== -1) {
                return href.substring(hashIndex + 1);
            }
            return null;
        }
        
        // Function to handle navigation clicks
        function handleNavClick(e, targetId) {
            e.preventDefault();
            
            const targetSection = document.getElementById(targetId);
            
            if (targetSection) {
                // Hide all sections except the target
                showOnlySection(targetSection);
                
                // Smooth scroll to the section
                window.scrollTo({
                    top: targetSection.offsetTop - 80, // Adjust for navbar height
                    behavior: 'smooth'
                });
                
                // Update active state in navbar
                updateActiveNav(this);
                
                // Close mobile navbar if open
                const navbarCollapse = document.querySelector('.navbar-collapse');
                if (navbarCollapse && navbarCollapse.classList.contains('show')) {
                    document.querySelector('.navbar-toggler').click();
                }
            }
        }
        
        // Handle in-page navigation links
        inPageNavLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                const targetId = this.getAttribute('href').substring(1);
                handleNavClick.call(this, e, targetId);
            });
        });
        
        // Handle navbar links that point to sections
        navbarSectionLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                // Only process links pointing to the current page with a hash
                if (link.getAttribute('href').includes('#')) {
                    const targetId = getSectionId(link.getAttribute('href'));
                    if (targetId) {
                        handleNavClick.call(this, e, targetId);
                    }
                }
            });
        });
        
        // Handle initial page load - show first section or hash section
        if (window.location.hash) {
            const targetId = window.location.hash.substring(1);
            const targetSection = document.getElementById(targetId);
            
            if (targetSection) {
                showOnlySection(targetSection);
                const targetLink = document.querySelector(`.nav-link[href*="#${targetId}"]`);
                if (targetLink) updateActiveNav(targetLink);
            } else {
                showOnlySection(sections[0]);
            }
        } else {
            // On first load, show only the first section (hero section)
            showOnlySection(sections[0]);
        }
    }
    
    /**
     * Show only the target section and hide others
     */
    function showOnlySection(targetSection) {
        if (currentSection === targetSection) return;
        
        // Store the new current section
        currentSection = targetSection;
        
        // Hide all sections with a fade out
        sections.forEach(section => {
            if (section !== targetSection) {
                section.style.display = 'none';
                section.classList.remove('fade-in');
            }
        });
        
        // Show target section with a fade in
        targetSection.style.display = 'block';
        setTimeout(() => {
            targetSection.classList.add('fade-in');
        }, 50);
        
        // Initialize specific features based on the section
        initializeSectionFeatures(targetSection);
    }
    
    /**
     * Update active state in navbar
     */
    function updateActiveNav(activeLink) {
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => link.classList.remove('active'));
        activeLink.classList.add('active');
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
        }
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
    
    /**
     * Setup achievement cards with modal functionality
     */
    function setupAchievementCards() {
        const achievementCards = document.querySelectorAll('.achievement-card');
        const achievementModal = document.getElementById('achievementModal');
        
        if (!achievementCards.length || !achievementModal) return;
        
        let bsModal = null;
        
        // Check if Bootstrap is available
        if (typeof bootstrap !== 'undefined') {
            try {
                // Initialize modal properly
                bsModal = new bootstrap.Modal(achievementModal, {
                    backdrop: true,
                    keyboard: true,
                    focus: true
                });
                
                // Make sure the modal can be closed
                achievementModal.addEventListener('hide.bs.modal', function () {
                    document.body.classList.remove('modal-open');
                    const backdrop = document.querySelector('.modal-backdrop');
                    if (backdrop) {
                        backdrop.parentNode.removeChild(backdrop);
                    }
                });
            } catch (e) {
                console.error('Failed to initialize modal:', e);
                return;
            }
        } else {
            console.error('Bootstrap is not available. Modals will not work.');
            return;
        }
        
        // Add click event to each achievement card
        achievementCards.forEach(card => {
            // Add hover effect
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-10px)';
                this.style.boxShadow = '0 15px 30px rgba(0, 0, 0, 0.3)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(-5px)';
                this.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.2)';
            });
            
            // Add click handler
            card.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                try {
                    const title = this.querySelector('.achievement-title').textContent;
                    const description = this.querySelector('.achievement-description').textContent;
                    
                    // Get image if exists
                    let imageSrc = null;
                    const imageElement = this.querySelector('.achievement-img');
                    if (imageElement) {
                        imageSrc = imageElement.getAttribute('src');
                    }
                    
                    // Get date if exists
                    let dateText = '';
                    const dateElement = this.querySelector('.achievement-date-badge');
                    if (dateElement) {
                        dateText = dateElement.textContent.trim();
                    }
                    
                    // Get certificate PDF if exists
                    let certificatePdf = null;
                    const certificateSection = this.querySelector('.achievement-certificate');
                    if (certificateSection) {
                        const downloadLink = certificateSection.querySelector('a[download]');
                        if (downloadLink) {
                            certificatePdf = downloadLink.getAttribute('href');
                        }
                    }
                    
                    // Update modal content
                    const modalTitle = document.getElementById('achievementModalTitle');
                    const modalDescription = document.getElementById('modalDescription'); 
                    
                    if (modalTitle) modalTitle.textContent = title;
                    if (modalDescription) modalDescription.textContent = description;
                    
                    // Update image container
                    const imageContainer = document.getElementById('modalImageContainer');
                    if (imageContainer) {
                        imageContainer.innerHTML = '';
                        
                        if (imageSrc) {
                            const img = document.createElement('img');
                            img.src = imageSrc;
                            img.alt = title;
                            img.className = 'img-fluid achievement-modal-img';
                            imageContainer.appendChild(img);
                        } else {
                            const placeholder = document.createElement('div');
                            placeholder.className = 'achievement-modal-placeholder d-flex align-items-center justify-content-center';
                            const icon = document.createElement('i');
                            icon.className = 'fas fa-trophy fa-5x text-primary';
                            placeholder.appendChild(icon);
                            imageContainer.appendChild(placeholder);
                        }
                        
                        // Add date if available
                        if (dateText) {
                            const dateDiv = document.createElement('div');
                            dateDiv.className = 'achievement-modal-date mt-2';
                            const dateIcon = document.createElement('i');
                            dateIcon.className = 'fas fa-calendar-alt me-1';
                            dateDiv.appendChild(dateIcon);
                            dateDiv.appendChild(document.createTextNode(dateText));
                            imageContainer.appendChild(dateDiv);
                        }
                        
                        // Add certificate buttons if available
                        if (certificatePdf) {
                            // Extract filename from path
                            const filename = certificatePdf.split('/').pop();
                            
                            const certificateDiv = document.createElement('div');
                            certificateDiv.className = 'achievement-modal-certificates';
                            
                            const certificateTitle = document.createElement('h5');
                            certificateTitle.className = 'mb-2';
                            certificateTitle.innerHTML = '<i class="fas fa-certificate me-1"></i> Certificate';
                            certificateDiv.appendChild(certificateTitle);
                            
                            const buttonGroup = document.createElement('div');
                            buttonGroup.className = 'btn-group';
                            
                            // Download button
                            const downloadBtn = document.createElement('a');
                            downloadBtn.href = certificatePdf;
                            downloadBtn.className = 'btn btn-sm btn-primary';
                            downloadBtn.setAttribute('download', '');
                            downloadBtn.innerHTML = '<i class="fas fa-download me-1"></i> Download';
                            buttonGroup.appendChild(downloadBtn);
                            
                            // View button
                            const viewBtn = document.createElement('a');
                            viewBtn.href = `/view-certificate/${filename}`;
                            viewBtn.className = 'btn btn-sm btn-outline-info';
                            viewBtn.setAttribute('target', '_blank');
                            viewBtn.innerHTML = '<i class="fas fa-eye me-1"></i> View';
                            buttonGroup.appendChild(viewBtn);
                            
                            certificateDiv.appendChild(buttonGroup);
                            imageContainer.appendChild(certificateDiv);
                        }
                    }
                    
                    // Show the modal using Bootstrap API
                    bsModal.show();
                } catch (error) {
                    console.error('Error opening modal:', error);
                }
            });
        });
        
        // Add click handlers to modal close buttons
        const closeButtons = achievementModal.querySelectorAll('[data-bs-dismiss="modal"]');
        closeButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                try {
                    bsModal.hide();
                } catch (error) {
                    console.error('Error closing modal:', error);
                    
                    // Fallback manual close if Bootstrap API fails
                    achievementModal.classList.remove('show');
                    achievementModal.style.display = 'none';
                    document.body.classList.remove('modal-open');
                    
                    const backdrop = document.querySelector('.modal-backdrop');
                    if (backdrop) backdrop.parentNode.removeChild(backdrop);
                }
            });
        });
        
        // Add click handler to the modal backdrop
        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('modal') || e.target.classList.contains('modal-backdrop')) {
                try {
                    bsModal.hide();
                } catch (error) {
                    console.error('Error closing modal via backdrop:', error);
                }
            }
        });
        
        // Add ESC key handler
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && document.body.classList.contains('modal-open')) {
                try {
                    bsModal.hide();
                } catch (error) {
                    console.error('Error closing modal via ESC key:', error);
                }
            }
        });
    }
    
    // Call setup functions
    setupNavigation();
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
}); 