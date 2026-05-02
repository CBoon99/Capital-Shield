/**
 * Coerentis (BoonMind) landing page JavaScript
 * Smooth scrolling, copy functionality, and basic interactions
 */

(function() {
    'use strict';

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
            messagesDiv.innerHTML = '';

            if (!validateForm(form)) {
                e.preventDefault();
                return false;
            }

            // No fetch: allow normal POST to /thanks/ (Netlify still records the submission).
            if (typeof fetch !== 'function') {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Sending...';
                return true;
            }

            e.preventDefault();

            const originalText = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.textContent = 'Sending...';

            const params = new URLSearchParams(new FormData(form));

            fetch('/', {
                method: 'POST',
                body: params
            })
                .then(function (res) {
                    if (!res.ok) throw new Error('Submit failed');
                })
                .then(function () {
                    showFormMessage(
                        messagesDiv,
                        'success',
                        "Thank you — your application was sent. We'll reply within 48 hours at the email you provided. Our team is notified at info@boonmind.io."
                    );
                    form.reset();
                })
                .catch(function () {
                    showFormMessage(
                        messagesDiv,
                        'error',
                        'Something went wrong. Please email info@boonmind.io directly or try again in a moment.'
                    );
                })
                .finally(function () {
                    submitBtn.disabled = false;
                    submitBtn.textContent = originalText;
                });
        });
    }

    function validateForm(form) {
        const name = form.querySelector('#name').value.trim();
        const email = form.querySelector('#email').value.trim();
        const tier = form.querySelector('#tier') ? form.querySelector('#tier').value : '';
        const tradingStack = form.querySelector('#tradingStack') ? form.querySelector('#tradingStack').value.trim() : '';
        const painPoint = form.querySelector('#painPoint') ? form.querySelector('#painPoint').value.trim() : '';
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
        
        if (!tier) {
            errors.push('Please select a tier');
            isValid = false;
        }
        
        if (!tradingStack) {
            errors.push('Primary trading stack is required');
            isValid = false;
        }
        
        if (!painPoint) {
            errors.push('Please describe your risk management pain point');
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

    function initStripeCheckout() {
        document.querySelectorAll('[data-stripe-plan]').forEach(function(btn) {
            btn.addEventListener('click', function() {
                var raw = btn.getAttribute('data-stripe-plan');
                if (!raw) return;

                var plan;
                if (raw === 'audit') {
                    var toggle = document.getElementById('pricing-toggle');
                    var annual = toggle && toggle.checked;
                    plan = annual ? 'audit-annual' : 'audit-monthly';
                } else {
                    plan = raw;
                }

                var original = btn.textContent;
                btn.disabled = true;
                btn.textContent = 'Redirecting…';

                fetch('/.netlify/functions/create-checkout-session', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ plan: plan })
                })
                    .then(function(res) {
                        return res.json().then(function(data) {
                            return { ok: res.ok, data: data };
                        });
                    })
                    .then(function(result) {
                        if (result.data && result.data.url) {
                            window.location.href = result.data.url;
                            return;
                        }
                        var msg = (result.data && result.data.error) ? result.data.error : 'Checkout could not start.';
                        alert(msg);
                        btn.disabled = false;
                        btn.textContent = original;
                    })
                    .catch(function() {
                        alert('Network error. Try again or email info@boonmind.io.');
                        btn.disabled = false;
                        btn.textContent = original;
                    });
            });
        });
    }

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

    function prefillTierFromQuery() {
        const tierSelect = document.getElementById('tier');
        if (!tierSelect) return;
        try {
            const params = new URLSearchParams(window.location.search);
            const tier = params.get('tier');
            if (tier && tierSelect.querySelector('option[value="' + tier + '"]')) {
                tierSelect.value = tier;
            }
            if (tier && window.location.hash === '#contact') {
                requestAnimationFrame(function() {
                    const el = document.getElementById('contact');
                    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
                });
            }
        } catch (err) { /* ignore */ }
    }

    // Initialize everything when DOM is ready
    function init() {
        initSmoothScroll();
        initCopyButtons();
        initHeaderScroll();
        initScrollAnimations();
        prefillTierFromQuery();
        initContactForm();
        initStripeCheckout();
    }

    // Run on DOMContentLoaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
