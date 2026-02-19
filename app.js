/**
 * BoonMindX Capital Shield Landing Page JavaScript
 * Smooth scrolling, copy functionality, and basic interactions
 */

(function() {
    'use strict';

    // GitHub repository URL
    const GITHUB_REPO_URL = 'https://github.com/CBoon99/Capital-Shield';

    // Smooth scroll for anchor links
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                if (href === '#' || href === '') return;
                
                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    const headerOffset = 80;
                    const elementPosition = target.getBoundingClientRect().top;
                    const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                    window.scrollTo({
                        top: offsetPosition,
                        behavior: 'smooth'
                    });
                }
            });
        });
    }

    // Copy to clipboard functionality
    function initCopyButtons() {
        document.querySelectorAll('.copy-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const code = this.getAttribute('data-copy');
                if (!code) return;

                // Try modern clipboard API
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    navigator.clipboard.writeText(code).then(() => {
                        showCopyFeedback(this);
                    }).catch(err => {
                        console.error('Failed to copy:', err);
                        fallbackCopy(code, this);
                    });
                } else {
                    fallbackCopy(code, this);
                }
            });
        });
    }

    function fallbackCopy(text, button) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            showCopyFeedback(button);
        } catch (err) {
            console.error('Fallback copy failed:', err);
        }
        
        document.body.removeChild(textArea);
    }

    function showCopyFeedback(button) {
        const originalText = button.textContent;
        button.textContent = 'Copied!';
        button.style.background = 'rgba(46, 168, 255, 0.2)';
        button.style.borderColor = '#2EA8FF';
        
        setTimeout(() => {
            button.textContent = originalText;
            button.style.background = '';
            button.style.borderColor = '';
        }, 2000);
    }

    // Header scroll effect
    function initHeaderScroll() {
        const header = document.getElementById('header');
        if (!header) return;

        let lastScroll = 0;
        window.addEventListener('scroll', () => {
            const currentScroll = window.pageYOffset;
            
            if (currentScroll > 100) {
                header.style.background = 'rgba(7, 18, 37, 0.95)';
            } else {
                header.style.background = 'rgba(7, 18, 37, 0.85)';
            }
            
            lastScroll = currentScroll;
        }, { passive: true });
    }

    // Intersection Observer for fade-in animations
    function initScrollAnimations() {
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            return; // Skip animations if user prefers reduced motion
        }

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

        // Observe capability cards and other sections
        document.querySelectorAll('.capability-card, .license-card, .code-block').forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(20px)';
            el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(el);
        });
    }

    // Handle Netlify form submission
    function initContactForm() {
        const form = document.getElementById('contact-form');
        if (!form) return;

        const submitBtn = document.getElementById('submit-btn');
        const messagesDiv = document.getElementById('form-messages');

        form.addEventListener('submit', function(e) {
            // Clear previous messages
            messagesDiv.innerHTML = '';
            
            // Validate form before submission
            if (!validateForm(form)) {
                e.preventDefault();
                return false;
            }
            
            // Disable submit button and show "Sending..." state
            // Let Netlify handle the form submission naturally
            // The form will submit to action="/thanks/" and Netlify will process it
            submitBtn.disabled = true;
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Sending...';
            
            // Form will submit naturally - Netlify processes it and redirects to /thanks/
            // If there's a network error, the browser will handle it
            // Button stays disabled to prevent double-submission
        });
    }

    function validateForm(form) {
        const name = form.querySelector('#name').value.trim();
        const email = form.querySelector('#email').value.trim();
        const subject = form.querySelector('#subject').value;
        const message = form.querySelector('#message').value.trim();
        const messagesDiv = document.getElementById('form-messages');
        
        // Clear previous messages
        messagesDiv.innerHTML = '';
        
        let isValid = true;
        let errors = [];
        
        if (!name) {
            errors.push('Name is required');
            isValid = false;
        }
        
        if (!email) {
            errors.push('Email is required');
            isValid = false;
        } else if (!isValidEmail(email)) {
            errors.push('Please enter a valid email address');
            isValid = false;
        }
        
        if (!subject) {
            errors.push('Please select a subject');
            isValid = false;
        }
        
        if (!message) {
            errors.push('Message is required');
            isValid = false;
        }
        
        if (!isValid) {
            showFormMessage(messagesDiv, 'error', errors.join('. '));
        }
        
        return isValid;
    }

    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    function showFormMessage(container, type, message) {
        const msgDiv = document.createElement('div');
        msgDiv.className = type === 'error' ? 'form-error' : 'form-success';
        msgDiv.textContent = message;
        container.appendChild(msgDiv);
        
        // Scroll to message
        msgDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    // Pricing toggle function (monthly/annual)
    function togglePricing() {
        const toggle = document.getElementById('pricing-toggle');
        const monthlyElements = document.querySelectorAll('.pricing-monthly');
        const annualElements = document.querySelectorAll('.pricing-annual');
        
        if (toggle && toggle.checked) {
            // Show annual pricing
            monthlyElements.forEach(el => el.style.display = 'none');
            annualElements.forEach(el => el.style.display = 'block');
        } else {
            // Show monthly pricing
            monthlyElements.forEach(el => el.style.display = 'block');
            annualElements.forEach(el => el.style.display = 'none');
        }
    }

    // Make togglePricing available globally
    window.togglePricing = togglePricing;

    // Initialize everything when DOM is ready
    function init() {
        initSmoothScroll();
        initCopyButtons();
        initHeaderScroll();
        initScrollAnimations();
        initContactForm();
    }

    // Run on DOMContentLoaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
