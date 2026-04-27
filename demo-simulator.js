/**
 * Capital Shield API Integration Demo Simulator
 * Client-side simulation of Capital Shield API logic
 */

(function() {
    'use strict';

    // Simulate Capital Shield API check
    function checkTrade(signal, asset, currentDrawdown, volatility24h, maxDDLimit, maxVolLimit) {
        // Convert percentages to decimals for comparison
        const drawdownDecimal = currentDrawdown / 100;
        const maxDDDecimal = maxDDLimit / 100;
        const volatilityDecimal = volatility24h / 100;
        const maxVolDecimal = maxVolLimit / 100;

        // DD check (drawdown must be >= limit, e.g., -8.5% >= -10%)
        if (drawdownDecimal < maxDDDecimal) {
            return {
                allowed: false,
                code: "DD_BREACH",
                reason: `Drawdown (${currentDrawdown}%) exceeds limit (${maxDDLimit}%)`
            };
        }

        // Volatility check
        if (volatilityDecimal > maxVolDecimal) {
            return {
                allowed: false,
                code: "VOL_BREACH",
                reason: `Volatility (${volatility24h}%) exceeds limit (${maxVolLimit}%)`
            };
        }

        // Regime guard (simplified: if volatility is very high relative to limit)
        const regimeThreshold = maxVolDecimal * 1.5; // 1.5x the limit
        if (volatilityDecimal > regimeThreshold) {
            return {
                allowed: false,
                code: "REGIME_GUARD",
                reason: `Crash regime detected (volatility ${volatility24h}% is ${(volatilityDecimal / maxVolDecimal).toFixed(1)}x limit)`
            };
        }

        // All checks passed
        return {
            allowed: true,
            code: "ALLOWED",
            reason: "All safety checks passed"
        };
    }

    // Setup range sliders for API demo
    function setupAPIRangeSliders() {
        const drawdownSlider = document.getElementById('api-drawdown');
        const drawdownInput = document.getElementById('api-drawdown-input');
        const drawdownValue = document.getElementById('api-drawdown-value');

        if (drawdownSlider && drawdownInput && drawdownValue) {
            // Update number input and display when slider changes
            drawdownSlider.addEventListener('input', function() {
                const val = parseFloat(this.value);
                drawdownInput.value = val;
                drawdownValue.textContent = val + '%';
            });

            // Update slider when number input changes
            drawdownInput.addEventListener('input', function() {
                let val = parseFloat(this.value);
                val = Math.max(-20, Math.min(0, val));
                this.value = val;
                drawdownSlider.value = val;
                drawdownValue.textContent = val + '%';
            });
        }

        const volatilitySlider = document.getElementById('api-volatility');
        const volatilityInput = document.getElementById('api-volatility-input');
        const volatilityValue = document.getElementById('api-volatility-value');

        if (volatilitySlider && volatilityInput && volatilityValue) {
            volatilitySlider.addEventListener('input', function() {
                const val = parseFloat(this.value);
                volatilityInput.value = val;
                volatilityValue.textContent = val + '%';
            });

            volatilityInput.addEventListener('input', function() {
                let val = parseFloat(this.value);
                val = Math.max(0, Math.min(200, val));
                this.value = val;
                volatilitySlider.value = val;
                volatilityValue.textContent = val + '%';
            });
        }
    }

    // Render API response
    function renderAPIResponse(result, inputs) {
        const panel = document.getElementById('api-output-panel');
        if (!panel) return;

        const decisionClass = result.allowed ? 'decision-allow' : 'decision-block';
        const decisionIcon = result.allowed ? '✅' : '🚫';
        const decisionText = result.allowed ? 'ALLOWED' : 'BLOCKED';

        const inputsHtml = `
            <div class="inputs-snapshot" style="margin-top: 32px;">
                <div class="snapshot-title">Request Details</div>
                <div class="snapshot-grid">
                    <div class="snapshot-item">
                        <div class="snapshot-label">Signal</div>
                        <div class="snapshot-value">${inputs.signal}</div>
                    </div>
                    <div class="snapshot-item">
                        <div class="snapshot-label">Asset</div>
                        <div class="snapshot-value">${inputs.asset}</div>
                    </div>
                    <div class="snapshot-item">
                        <div class="snapshot-label">Current Drawdown</div>
                        <div class="snapshot-value">${inputs.drawdown}%</div>
                    </div>
                    <div class="snapshot-item">
                        <div class="snapshot-label">24h Volatility</div>
                        <div class="snapshot-value">${inputs.volatility}%</div>
                    </div>
                    <div class="snapshot-item">
                        <div class="snapshot-label">Max DD Limit</div>
                        <div class="snapshot-value">${inputs.maxDD}%</div>
                    </div>
                    <div class="snapshot-item">
                        <div class="snapshot-label">Max Vol Limit</div>
                        <div class="snapshot-value">${inputs.maxVol}%</div>
                    </div>
                </div>
            </div>
        `;

        panel.innerHTML = `
            <div class="decision-badge ${decisionClass}">
                ${decisionIcon} ${decisionText}
            </div>
            
            <div class="reason-codes">
                <div class="reason-codes-title">Response</div>
                <div style="padding: 16px; background: ${result.allowed ? 'rgba(46, 168, 255, 0.1)' : 'rgba(255, 68, 68, 0.1)'}; border: 1px solid ${result.allowed ? 'rgba(46, 168, 255, 0.3)' : 'rgba(255, 68, 68, 0.3)'}; border-radius: 8px; margin-bottom: 16px;">
                    <div style="margin-bottom: 8px;">
                        <strong>Code:</strong> <code style="background: rgba(46, 168, 255, 0.1); padding: 4px 8px; border-radius: 4px; font-size: 12px;">${result.code}</code>
                    </div>
                    <div>
                        <strong>Reason:</strong> <span style="color: var(--text-primary);">${result.reason}</span>
                    </div>
                </div>
            </div>
            ${inputsHtml}
        `;

        // Scroll to output panel
        panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    // Setup form submission
    function setupAPIForm() {
        const form = document.getElementById('api-demo-form');
        if (!form) return;

        form.addEventListener('submit', function(e) {
            e.preventDefault();

            const signal = document.getElementById('api-signal').value;
            const asset = document.getElementById('api-asset').value;
            const drawdown = parseFloat(document.getElementById('api-drawdown').value);
            const volatility = parseFloat(document.getElementById('api-volatility').value);
            const maxDD = parseFloat(document.getElementById('api-max-dd').value);
            const maxVol = parseFloat(document.getElementById('api-max-vol').value);

            const inputs = {
                signal: signal,
                asset: asset,
                drawdown: drawdown,
                volatility: volatility,
                maxDD: maxDD,
                maxVol: maxVol
            };

            const result = checkTrade(signal, asset, drawdown, volatility, maxDD, maxVol);
            renderAPIResponse(result, inputs);
        });
    }

    // Copy code example
    window.copyCodeExample = function() {
        const code = `# 3 lines to protect your capital
from capital_shield import SafetyGate

gate = SafetyGate(max_drawdown=-0.10, max_volatility=0.80)

# Before every trade:
decision = gate.check(
    signal="BUY",
    asset="BTC",
    current_drawdown=-0.085,
    volatility_24h=0.45
)

if decision.allowed:
    execute_trade()
else:
    log(f"Blocked: {decision.code} - {decision.reason}")`;

        navigator.clipboard.writeText(code).then(function() {
            const btn = event.target;
            const originalText = btn.textContent;
            btn.textContent = 'Copied!';
            btn.style.background = 'rgba(46, 168, 255, 0.3)';
            setTimeout(function() {
                btn.textContent = originalText;
                btn.style.background = '';
            }, 2000);
        }).catch(function(err) {
            console.error('Failed to copy:', err);
        });
    };

    // Initialize
    function init() {
        setupAPIRangeSliders();
        setupAPIForm();
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
