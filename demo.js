/**
 * Capital Shield Interactive Demo
 * Deterministic Risk Scenario Simulator
 */

(function() {
    'use strict';

    // Default drawdown threshold
    const DRAWDOWN_THRESHOLD = 12;

    // Preset configurations
    const PRESETS = {
        'flash-crash': {
            drawdownPercent: 18,
            volatilityRegime: 'high',
            slippageBps: 150,
            signalConfidence: 45,
            apiHealth: 'degraded',
            killSwitch: 'off',
            positionSizePercent: 8
        },
        'choppy-noise': {
            drawdownPercent: 8,
            volatilityRegime: 'high',
            slippageBps: 95,
            signalConfidence: 55,
            apiHealth: 'ok',
            killSwitch: 'off',
            positionSizePercent: 6
        },
        'healthy-trend': {
            drawdownPercent: 5,
            volatilityRegime: 'low',
            slippageBps: 25,
            signalConfidence: 85,
            apiHealth: 'ok',
            killSwitch: 'off',
            positionSizePercent: 4
        }
    };

    // Gate evaluation rules
    const GATE_RULES = [
        {
            id: 'killSwitch',
            name: 'Kill Switch',
            code: 'KILL_SWITCH',
            check: (inputs) => inputs.killSwitch === 'on',
            getMessage: (inputs) => 'Kill switch is active - all trades blocked'
        },
        {
            id: 'apiHealth',
            name: 'API Health Check',
            code: 'API_UNHEALTHY',
            check: (inputs) => inputs.apiHealth !== 'ok',
            getMessage: (inputs) => `API health is "${inputs.apiHealth}" - fail-closed default blocks trade`
        },
        {
            id: 'drawdown',
            name: 'Drawdown Limit',
            code: 'DD_BREACH',
            check: (inputs) => inputs.drawdownPercent > DRAWDOWN_THRESHOLD,
            getMessage: (inputs) => `Drawdown (${inputs.drawdownPercent}%) exceeds threshold (${DRAWDOWN_THRESHOLD}%)`
        },
        {
            id: 'volatilityRegime',
            name: 'Volatility Regime Filter',
            code: 'VOL_REGIME_BREACH',
            check: (inputs) => inputs.volatilityRegime === 'high' && inputs.signalConfidence < 70,
            getMessage: (inputs) => `High volatility regime requires signal confidence ≥ 70% (current: ${inputs.signalConfidence}%)`
        },
        {
            id: 'slippage',
            name: 'Slippage Limit',
            code: 'SLIPPAGE_BREACH',
            check: (inputs) => inputs.slippageBps > 80,
            getMessage: (inputs) => `Slippage (${inputs.slippageBps} bps) exceeds limit (80 bps)`
        },
        {
            id: 'positionSize',
            name: 'Position Size Limit',
            code: 'POS_SIZE_BREACH',
            check: (inputs) => inputs.positionSizePercent > 10,
            getMessage: (inputs) => `Position size (${inputs.positionSizePercent}%) exceeds limit (10%)`
        }
    ];

    // Initialize demo
    function init() {
        setupRangeSliders();
        setupPresetButtons();
        setupFormSubmission();
    }

    // Sync range sliders with number inputs
    function setupRangeSliders() {
        const sliders = [
            { slider: 'drawdownPercent', input: 'drawdownPercentInput', value: 'drawdownValue', suffix: '%' },
            { slider: 'slippageBps', input: 'slippageBpsInput', value: 'slippageValue', suffix: ' bps' },
            { slider: 'signalConfidence', input: 'signalConfidenceInput', value: 'confidenceValue', suffix: '%' },
            { slider: 'positionSizePercent', input: 'positionSizePercentInput', value: 'positionValue', suffix: '%' }
        ];

        sliders.forEach(({ slider, input, value, suffix }) => {
            const sliderEl = document.getElementById(slider);
            const inputEl = document.getElementById(input);
            const valueEl = document.getElementById(value);

            if (!sliderEl || !inputEl || !valueEl) return;

            // Initialize display value
            const initialVal = parseFloat(sliderEl.value);
            valueEl.textContent = initialVal + suffix;

            // Update number input and display value when slider changes
            sliderEl.addEventListener('input', function() {
                const val = parseFloat(this.value);
                inputEl.value = val;
                valueEl.textContent = val + suffix;
            });

            // Update slider when number input changes
            inputEl.addEventListener('input', function() {
                let val = parseFloat(this.value);
                // Clamp to min/max
                const min = parseFloat(this.min) || 0;
                const max = parseFloat(this.max) || 100;
                val = Math.max(min, Math.min(max, val));
                this.value = val;
                sliderEl.value = val;
                valueEl.textContent = val + suffix;
            });
        });
    }

    // Setup preset buttons
    function setupPresetButtons() {
        const presetButtons = document.querySelectorAll('.preset-btn');
        
        presetButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                const presetName = this.getAttribute('data-preset');
                const preset = PRESETS[presetName];
                
                if (!preset) return;
                
                // Apply preset values
                document.getElementById('drawdownPercent').value = preset.drawdownPercent;
                document.getElementById('drawdownPercentInput').value = preset.drawdownPercent;
                document.getElementById('drawdownValue').textContent = preset.drawdownPercent + '%';
                
                document.getElementById('volatilityRegime').value = preset.volatilityRegime;
                
                document.getElementById('slippageBps').value = preset.slippageBps;
                document.getElementById('slippageBpsInput').value = preset.slippageBps;
                document.getElementById('slippageValue').textContent = preset.slippageBps + ' bps';
                
                document.getElementById('signalConfidence').value = preset.signalConfidence;
                document.getElementById('signalConfidenceInput').value = preset.signalConfidence;
                document.getElementById('confidenceValue').textContent = preset.signalConfidence + '%';
                
                document.getElementById('apiHealth').value = preset.apiHealth;
                document.getElementById('killSwitch').value = preset.killSwitch;
                
                document.getElementById('positionSizePercent').value = preset.positionSizePercent;
                document.getElementById('positionSizePercentInput').value = preset.positionSizePercent;
                document.getElementById('positionValue').textContent = preset.positionSizePercent + '%';
            });
        });
    }

    // Setup form submission
    function setupFormSubmission() {
        const form = document.getElementById('demo-form');
        
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            runCapitalShield();
        });
    }

    // Get current form inputs
    function getInputs() {
        return {
            drawdownPercent: parseFloat(document.getElementById('drawdownPercent').value),
            volatilityRegime: document.getElementById('volatilityRegime').value,
            slippageBps: parseFloat(document.getElementById('slippageBps').value),
            signalConfidence: parseFloat(document.getElementById('signalConfidence').value),
            apiHealth: document.getElementById('apiHealth').value,
            killSwitch: document.getElementById('killSwitch').value,
            positionSizePercent: parseFloat(document.getElementById('positionSizePercent').value)
        };
    }

    // Evaluate gate stack
    function evaluateGates(inputs) {
        const triggeredRules = [];
        
        for (const rule of GATE_RULES) {
            if (rule.check(inputs)) {
                triggeredRules.push({
                    id: rule.id,
                    name: rule.name,
                    code: rule.code,
                    message: rule.getMessage(inputs)
                });
            }
        }
        
        return {
            decision: triggeredRules.length > 0 ? 'BLOCK' : 'ALLOW',
            triggeredRules: triggeredRules
        };
    }

    // Run Capital Shield evaluation
    function runCapitalShield() {
        const inputs = getInputs();
        const result = evaluateGates(inputs);
        renderOutput(result, inputs);
    }

    // Render output panel
    function renderOutput(result, inputs) {
        const panel = document.getElementById('output-panel');
        
        const decisionClass = result.decision === 'ALLOW' ? 'decision-allow' : 'decision-block';
        
        // Build reason codes HTML
        const reasonCodesHtml = GATE_RULES.map(rule => {
            const triggered = result.triggeredRules.some(r => r.id === rule.id);
            const message = triggered 
                ? result.triggeredRules.find(r => r.id === rule.id).message
                : 'Passed';
            
            return `
                <li class="reason-item ${triggered ? 'triggered' : ''}">
                    <strong>${rule.name}</strong> (<code>${rule.code}</code>): ${message}
                </li>
            `;
        }).join('');
        
        // Build inputs snapshot HTML
        const snapshotHtml = `
            <div class="snapshot-item">
                <div class="snapshot-label">Drawdown</div>
                <div class="snapshot-value">${inputs.drawdownPercent}%</div>
            </div>
            <div class="snapshot-item">
                <div class="snapshot-label">Volatility</div>
                <div class="snapshot-value">${inputs.volatilityRegime}</div>
            </div>
            <div class="snapshot-item">
                <div class="snapshot-label">Slippage</div>
                <div class="snapshot-value">${inputs.slippageBps} bps</div>
            </div>
            <div class="snapshot-item">
                <div class="snapshot-label">Signal Confidence</div>
                <div class="snapshot-value">${inputs.signalConfidence}%</div>
            </div>
            <div class="snapshot-item">
                <div class="snapshot-label">API Health</div>
                <div class="snapshot-value">${inputs.apiHealth}</div>
            </div>
            <div class="snapshot-item">
                <div class="snapshot-label">Kill Switch</div>
                <div class="snapshot-value">${inputs.killSwitch}</div>
            </div>
            <div class="snapshot-item">
                <div class="snapshot-label">Position Size</div>
                <div class="snapshot-value">${inputs.positionSizePercent}%</div>
            </div>
        `;
        
        panel.innerHTML = `
            <div class="decision-badge ${decisionClass}">${result.decision}</div>
            
            <div class="reason-codes">
                <div class="reason-codes-title">Gate Evaluation Results</div>
                <ul class="reason-list">
                    ${reasonCodesHtml}
                </ul>
            </div>
            
            <div class="inputs-snapshot">
                <div class="snapshot-title">Inputs Snapshot</div>
                <div class="snapshot-grid">
                    ${snapshotHtml}
                </div>
            </div>
        `;
        
        // Scroll to output panel
        panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
