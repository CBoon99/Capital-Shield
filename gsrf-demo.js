/**
 * GSRF live demo (embedded in main Capital Shield landing).
 * Deterministic filter math matches the GSRF specification.
 */
(function () {
    'use strict';

    function GSRFFilter(options) {
        options = options || {};
        this.beta = Math.min(0.9, Math.max(0.01, options.beta || 0.3));
        this.k_return = Math.max(0.1, options.k_return || 1.0);
        this.mem = Math.min(0.5, Math.max(0.0, options.mem || 0.2));
        this.targetCenter = options.targetCenter || 50;
        this.current = this.targetCenter;
        this.previous = this.targetCenter;
    }

    GSRFFilter.prototype.update = function (observation, dt) {
        dt = dt === undefined ? 1.0 : dt;
        var gradient = -(this.current - this.targetCenter);
        var memory = Math.tanh(this.current - this.previous);
        var u = this.k_return * gradient + this.mem * memory;
        var filtered = this.current + this.beta * u * dt;
        filtered = Math.min(100, Math.max(0, filtered));
        this.previous = this.current;
        this.current = filtered;
        return filtered;
    };

    GSRFFilter.prototype.reset = function () {
        this.current = this.targetCenter;
        this.previous = this.targetCenter;
    };

    window.startGsrfProTrial = function () {
        window.alert('Pro trial: Email carl@boonmind.io to start your 14-day GSRF Pro trial. We will set up your account within 24 hours.');
    };

    window.contactGsrfEnterprise = function () {
        window.alert('Enterprise: Email carl@boonmind.io with your requirements. We will respond within 1 business day.');
    };

    function initGsrfDemo() {
        var root = document.getElementById('gsrf-demo');
        if (!root) return;

        var slider = document.getElementById('gsrf-riskSlider');
        var rawSpan = document.getElementById('gsrf-rawValue');
        var gsrfSpan = document.getElementById('gsrf-gsrfValue');
        var resetBtn = document.getElementById('gsrf-resetDemo');
        if (!slider || !rawSpan || !gsrfSpan || !resetBtn) return;

        var gsrf = new GSRFFilter({
            beta: 0.6,
            mem: 0.3,
            k_return: 1.2,
            targetCenter: 50
        });

        var time = 0;
        var rawValue = 50;

        function updateDemo() {
            var sliderVal = parseFloat(slider.value, 10);
            var oscillation = Math.sin(time) * 15;
            rawValue = Math.min(100, Math.max(0, sliderVal + oscillation));
            var filteredValue = gsrf.update(rawValue);
            rawSpan.textContent = Math.round(rawValue) + '%';
            gsrfSpan.textContent = Math.round(filteredValue) + '%';

            var rawCard = root.querySelector('.gsrf-value-card.gsrf-raw');
            var gsrfCard = root.querySelector('.gsrf-value-card.gsrf-filtered');
            if (rawCard && gsrfCard) {
                if (Math.abs(rawValue - filteredValue) > 5) {
                    rawCard.style.borderLeft = '3px solid #ff8800';
                    gsrfCard.style.borderLeft = '3px solid #2ecc71';
                } else {
                    rawCard.style.borderLeft = '3px solid transparent';
                    gsrfCard.style.borderLeft = '3px solid transparent';
                }
            }

            time += 0.1;
            requestAnimationFrame(updateDemo);
        }

        resetBtn.addEventListener('click', function () {
            gsrf.reset();
        });

        updateDemo();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initGsrfDemo);
    } else {
        initGsrfDemo();
    }
})();
