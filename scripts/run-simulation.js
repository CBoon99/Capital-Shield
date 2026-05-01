/**
 * Coerentis Crisis Simulation Script
 * Fetches real historical data and runs unshielded vs shielded simulations
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

// Try to load historical data if available
let historicalData = null;
try {
    const dataPath = path.join(__dirname, '..', 'historical-price-data.json');
    if (fs.existsSync(dataPath)) {
        historicalData = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
        console.log('Loaded historical price data from file');
    }
} catch (e) {
    // Ignore if file doesn't exist
}

// Configuration
const STARTING_CAPITAL = 100000; // £100,000
const POSITION_SIZE = 0.10; // 10% per trade
const MAX_DRAWDOWN_LIMIT = -0.10; // -10%
const MAX_VOLATILITY_LIMIT = 0.80; // 80%

// Sleep function for rate limiting
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Fetch price data - use historical data if available, otherwise try CoinGecko
function fetchPriceData(coinId, fromTimestamp, toTimestamp, crisisKey) {
    // First try to use pre-generated historical data
    if (historicalData && crisisKey && historicalData[crisisKey]) {
        console.log(`Using pre-generated data for ${crisisKey}`);
        return Promise.resolve(historicalData[crisisKey].prices);
    }
    
    // Otherwise try CoinGecko (will likely fail for old data)
    return new Promise((resolve, reject) => {
        const url = `https://api.coingecko.com/api/v3/coins/${coinId}/market_chart/range?vs_currency=usd&from=${fromTimestamp}&to=${toTimestamp}`;
        
        const options = {
            headers: {
                'User-Agent': 'Coerentis-Simulation/1.0'
            }
        };
        
        https.get(url, options, (res) => {
            let data = '';
            
            res.on('data', (chunk) => {
                data += chunk;
            });
            
            res.on('end', () => {
                try {
                    const json = JSON.parse(data);
                    if (json.prices && json.prices.length > 0) {
                        resolve(json.prices);
                    } else {
                        console.error('API Response:', JSON.stringify(json, null, 2));
                        reject(new Error('No prices data in response'));
                    }
                } catch (e) {
                    reject(e);
                }
            });
        }).on('error', (err) => {
            reject(err);
        });
    });
}

// Calculate daily returns
function calculateReturns(prices) {
    const returns = [];
    for (let i = 1; i < prices.length; i++) {
        const dailyReturn = (prices[i][1] - prices[i-1][1]) / prices[i-1][1];
        returns.push({
            timestamp: prices[i][0],
            date: new Date(prices[i][0]).toISOString().split('T')[0],
            price: prices[i][1],
            return: dailyReturn
        });
    }
    return returns;
}

// Calculate rolling volatility (24h window, annualized)
function calculateVolatility(returns, window = 24) {
    const volatilities = [];
    for (let i = window; i < returns.length; i++) {
        const slice = returns.slice(i - window, i).map(r => r.return);
        const mean = slice.reduce((a, b) => a + b, 0) / slice.length;
        const variance = slice.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / slice.length;
        const vol = Math.sqrt(variance) * Math.sqrt(365) * 100; // Annualized %
        volatilities.push({ ...returns[i], volatility: vol });
    }
    return volatilities;
}

// Simple momentum strategy: buy when 24h return > 1%, sell when < -1%
// More sensitive to generate more trades
function generateSignals(data) {
    return data.map(d => ({
        ...d,
        signal: d.return > 0.01 ? 'BUY' : (d.return < -0.01 ? 'SELL' : 'HOLD')
    }));
}

// Run simulation WITHOUT Coerentis
function runUnshieldedSimulation(signals) {
    let capital = STARTING_CAPITAL;
    let position = 0;
    let peakCapital = STARTING_CAPITAL;
    let maxDrawdown = 0;
    let equityCurve = [{ date: signals[0]?.date || 'start', value: STARTING_CAPITAL }];
    let tradesExecuted = 0;

    for (const s of signals) {
        if (s.signal === 'BUY' && position === 0) {
            position = capital * POSITION_SIZE;
            capital -= position;
            tradesExecuted++;
        } else if (s.signal === 'SELL' && position > 0) {
            capital += position * (1 + s.return);
            position = 0;
            tradesExecuted++;
        }
        
        // Update position value
        if (position > 0) {
            position *= (1 + s.return);
        }
        
        const totalValue = capital + position;
        equityCurve.push({ date: s.date, value: totalValue });
        
        // Track drawdown
        peakCapital = Math.max(peakCapital, totalValue);
        const currentDrawdown = (totalValue - peakCapital) / peakCapital;
        maxDrawdown = Math.min(maxDrawdown, currentDrawdown);
    }

    return {
        equityCurve,
        maxDrawdown,
        tradesExecuted,
        finalValue: capital + position,
        lowestValue: Math.min(...equityCurve.map(e => e.value))
    };
}

// Run simulation WITH Coerentis
function runShieldedSimulation(signals) {
    let capital = STARTING_CAPITAL;
    let position = 0;
    let peakCapital = STARTING_CAPITAL;
    let maxDrawdown = 0;
    let equityCurve = [{ date: signals[0]?.date || 'start', value: STARTING_CAPITAL }];
    let tradesExecuted = 0;
    let tradesBlocked = 0;
    let blockedLog = [];
    const blockedByReason = { DD_BREACH: 0, VOL_BREACH: 0, REGIME_GUARD: 0 };

    for (const s of signals) {
        const totalValue = capital + position;
        const currentDrawdown = (totalValue - peakCapital) / peakCapital;
        
        // COERENTIS CHECK
        let blocked = false;
        let blockReason = null;
        let blockCode = null;
        
        // Regime guard: if volatility is very high (1.5x limit)
        const regimeThreshold = MAX_VOLATILITY_LIMIT * 1.5;
        if (s.volatility > regimeThreshold * 100 && s.signal === 'BUY') {
            blocked = true;
            blockCode = 'REGIME_GUARD';
            blockReason = `Crash regime detected (volatility ${s.volatility.toFixed(0)}% is ${(s.volatility / (MAX_VOLATILITY_LIMIT * 100)).toFixed(1)}x limit)`;
        } else if (currentDrawdown <= MAX_DRAWDOWN_LIMIT && s.signal === 'BUY') {
            blocked = true;
            blockCode = 'DD_BREACH';
            blockReason = `Drawdown ${(currentDrawdown * 100).toFixed(1)}% exceeds limit ${MAX_DRAWDOWN_LIMIT * 100}%`;
        } else if (s.volatility > MAX_VOLATILITY_LIMIT * 100 && s.signal === 'BUY') {
            blocked = true;
            blockCode = 'VOL_BREACH';
            blockReason = `Volatility ${s.volatility.toFixed(0)}% exceeds limit ${MAX_VOLATILITY_LIMIT * 100}%`;
        }
        
        if (blocked && s.signal === 'BUY') {
            tradesBlocked++;
            blockedByReason[blockCode]++;
            const estimatedLoss = Math.abs(s.return * (capital * POSITION_SIZE));
            blockedLog.push({
                timestamp: s.date,
                signal: s.signal,
                asset: 'BTC',
                code: blockCode,
                reason: blockReason,
                estimatedLoss: estimatedLoss
            });
        } else {
            // Execute trade
            if (s.signal === 'BUY' && position === 0) {
                position = capital * POSITION_SIZE;
                capital -= position;
                tradesExecuted++;
            } else if (s.signal === 'SELL' && position > 0) {
                capital += position * (1 + s.return);
                position = 0;
                tradesExecuted++;
            }
        }
        
        // Update position value
        if (position > 0) {
            position *= (1 + s.return);
        }
        
        const newTotalValue = capital + position;
        equityCurve.push({ date: s.date, value: newTotalValue });
        
        // Track drawdown
        peakCapital = Math.max(peakCapital, newTotalValue);
        const newDrawdown = (newTotalValue - peakCapital) / peakCapital;
        maxDrawdown = Math.min(maxDrawdown, newDrawdown);
    }

    return {
        equityCurve,
        maxDrawdown,
        tradesExecuted,
        tradesBlocked,
        blockedLog,
        blockedByReason,
        finalValue: capital + position,
        lowestValue: Math.min(...equityCurve.map(e => e.value))
    };
}

// Main execution
async function runAllSimulations() {
    const crises = [
        { name: 'May 2021 Crypto Crash', from: 1620604800, to: 1622505600, dateRange: 'May 12-23, 2021', key: 'may-2021' },
        { name: 'March 2020 COVID Crash', from: 1583020800, to: 1585699200, dateRange: 'March 9-23, 2020', key: 'march-2020' },
        { name: 'FTX Collapse Nov 2022', from: 1667260800, to: 1669075200, dateRange: 'November 6-14, 2022', key: 'ftx-2022' }
    ];

    const results = [];

    for (let i = 0; i < crises.length; i++) {
        const crisis = crises[i];
        console.log(`\n========== ${crisis.name} ==========\n`);
        
        try {
            const prices = await fetchPriceData('bitcoin', crisis.from, crisis.to, crisis.key);
            console.log(`Fetched ${prices.length} price points`);
            
            const returns = calculateReturns(prices);
            const withVolatility = calculateVolatility(returns);
            const signals = generateSignals(withVolatility);
            
            const unshielded = runUnshieldedSimulation(signals);
            const shielded = runShieldedSimulation(signals);
            
            const capitalPreserved = shielded.lowestValue - unshielded.lowestValue;
            
            console.log('UNSHIELDED:');
            console.log(`  Max Drawdown: ${(unshielded.maxDrawdown * 100).toFixed(1)}%`);
            console.log(`  Trades Executed: ${unshielded.tradesExecuted}`);
            console.log(`  Lowest Value: £${unshielded.lowestValue.toFixed(0)}`);
            console.log(`  Final Value: £${unshielded.finalValue.toFixed(0)}`);
            
            console.log('\nSHIELDED:');
            console.log(`  Max Drawdown: ${(shielded.maxDrawdown * 100).toFixed(1)}%`);
            console.log(`  Trades Executed: ${shielded.tradesExecuted}`);
            console.log(`  Trades Blocked: ${shielded.tradesBlocked}`);
            console.log(`  Blocked by DD_BREACH: ${shielded.blockedByReason.DD_BREACH}`);
            console.log(`  Blocked by VOL_BREACH: ${shielded.blockedByReason.VOL_BREACH}`);
            console.log(`  Blocked by REGIME_GUARD: ${shielded.blockedByReason.REGIME_GUARD}`);
            console.log(`  Lowest Value: £${shielded.lowestValue.toFixed(0)}`);
            console.log(`  Final Value: £${shielded.finalValue.toFixed(0)}`);
            console.log(`  Capital Preserved: £${capitalPreserved.toFixed(0)}`);
            
            console.log('\nBLOCKED TRADES (first 5):');
            shielded.blockedLog.slice(0, 5).forEach(b => {
                console.log(`  ${b.timestamp} | ${b.signal} ${b.asset} | ${b.code} | £${b.estimatedLoss.toFixed(0)}`);
            });
            
            // Store results
            results.push({
                name: crisis.name,
                dateRange: crisis.dateRange,
                unshielded: {
                    maxDrawdown: unshielded.maxDrawdown * 100,
                    tradesExecuted: unshielded.tradesExecuted,
                    lowestValue: unshielded.lowestValue,
                    finalValue: unshielded.finalValue,
                    equityCurve: unshielded.equityCurve
                },
                shielded: {
                    maxDrawdown: shielded.maxDrawdown * 100,
                    tradesExecuted: shielded.tradesExecuted,
                    tradesBlocked: shielded.tradesBlocked,
                    blockedByReason: shielded.blockedByReason,
                    lowestValue: shielded.lowestValue,
                    finalValue: shielded.finalValue,
                    equityCurve: shielded.equityCurve,
                    blockedLog: shielded.blockedLog
                },
                capitalPreserved: capitalPreserved,
                chartData: {
                    dates: unshielded.equityCurve.map(e => e.date),
                    unshielded: unshielded.equityCurve.map(e => e.value),
                    shielded: shielded.equityCurve.map(e => e.value)
                }
            });
            
            // Rate limiting delay
            if (i < crises.length - 1) {
                console.log('\nWaiting 3 seconds for rate limiting...');
                await sleep(3000);
            }
        } catch (error) {
            console.error(`Error processing ${crisis.name}:`, error.message);
        }
    }
    
    // Calculate combined metrics
    const totalTradesBlocked = results.reduce((sum, r) => sum + r.shielded.tradesBlocked, 0);
    const totalCapitalPreserved = results.reduce((sum, r) => sum + r.capitalPreserved, 0);
    const worstDrawdown = Math.min(...results.map(r => r.unshielded.maxDrawdown));
    const largestLossPrevented = Math.max(...results.flatMap(r => r.shielded.blockedLog.map(b => b.estimatedLoss)));
    
    const summary = {
        totalTradesBlocked,
        totalCapitalPreserved,
        worstDrawdown,
        largestLossPrevented,
        results
    };
    
    // Save results to JSON file
    const outputPath = path.join(__dirname, '..', 'simulation-results.json');
    fs.writeFileSync(outputPath, JSON.stringify(summary, null, 2));
    console.log(`\n\nResults saved to: ${outputPath}`);
    
    return summary;
}

// Run if executed directly
if (require.main === module) {
    runAllSimulations().catch(console.error);
}

module.exports = { runAllSimulations };
