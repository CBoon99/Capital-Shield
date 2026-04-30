/**
 * Loads audit-pilot-status.json and updates #audit-pilot-spots-line on the homepage.
 */
(function () {
    'use strict';

    function render(data) {
        var el = document.getElementById('audit-pilot-spots-line');
        if (!el || !data) return;

        var total = parseInt(data.spots_total, 10);
        if (isNaN(total) || total < 1) total = 10;

        var taken = parseInt(data.spots_taken, 10);
        if (isNaN(taken) || taken < 0) taken = 0;
        if (taken > total) taken = total;

        var remaining = total - taken;
        if (remaining <= 0) {
            el.textContent = 'Audit pilot seats are full for this wave — apply to join the waitlist.';
            el.setAttribute('aria-live', 'polite');
            return;
        }

        el.textContent =
            remaining +
            ' of ' +
            total +
            ' Audit pilot seats remaining (updated ' +
            (data.last_updated || 'recently') +
            ').';
        el.setAttribute('aria-live', 'polite');
    }

    function fallback() {
        var el = document.getElementById('audit-pilot-spots-line');
        if (!el) return;
        el.textContent =
            'Audit pilot: up to 10 qualified seats — apply for current availability.';
    }

    fetch('/audit-pilot-status.json?' + Date.now(), { cache: 'no-store' })
        .then(function (r) {
            if (!r.ok) throw new Error('status');
            return r.json();
        })
        .then(render)
        .catch(fallback);
})();
