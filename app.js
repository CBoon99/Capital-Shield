/**
 * BoonMindX Capital Shield Landing Page JavaScript
 * Smooth scrolling, copy functionality, and basic interactions
 */

(function() {
    'use strict';

    // GitHub repository URL (update this when repo URL is known)
    const GITHUB_REPO_URL = '#'; // TODO: Set actual GitHub repo URL

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
        const form = document.querySelector('.contact-form');
        if (!form) return;

        form.addEventListener('submit', function(e) {
            // Netlify will handle the submission
            // Show success message after redirect
            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.get('form') === 'contact' && urlParams.get('success') === 'true') {
                showFormSuccess();
            }
        });
    }

    function showFormSuccess() {
        const form = document.querySelector('.contact-form');
        if (!form) return;

        const successMsg = document.createElement('div');
        successMsg.className = 'form-success';
        successMsg.textContent = 'Thank you! Your message has been sent. We\'ll get back to you soon.';
        form.insertBefore(successMsg, form.firstChild);
        
        // Reset form
        form.reset();
        
        // Scroll to success message
        successMsg.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    // Initialize GitHub links
    function initGitHubLinks() {
        const links = document.querySelectorAll('#github-link, #github-link-hero, #github-link-footer');
        links.forEach(link => {
            if (GITHUB_REPO_URL !== '#') {
                link.href = GITHUB_REPO_URL;
            } else {
                link.style.display = 'none'; // Hide if not set
            }
        });
    }

    // Initialize everything when DOM is ready
    function init() {
        initSmoothScroll();
        initCopyButtons();
        initHeaderScroll();
        initScrollAnimations();
        initContactForm();
        initGitHubLinks();
    }

    // Run on DOMContentLoaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
