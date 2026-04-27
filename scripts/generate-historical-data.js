/**
 * Generate realistic historical price data based on known crash characteristics
 * Since CoinGecko free API only covers last 365 days, we'll generate realistic data
 */

const fs = require('fs');
const path = require('path');

// Generate realistic price series for a crash with hourly data points
function generateCrashPriceSeries(startPrice, endPrice, days, volatility = 0.02) {
    const prices = [];
    const totalReturn = (endPrice - startPrice) / startPrice;
    const hours = days * 24;
    const hourlyReturn = Math.pow(1 + totalReturn, 1 / hours);
    
    let currentPrice = startPrice;
    const startTimestamp = new Date('2021-05-12').getTime();
    
    for (let i = 0; i <= hours; i++) {
        // Add volatility/noise - higher during crash
        const progress = i / hours;
        const crashIntensity = Math.sin(progress * Math.PI); // Peak in middle
        const noise = (Math.random() - 0.5) * volatility * (1 + crashIntensity * 2);
        
        currentPrice = currentPrice * (hourlyReturn + noise);
        
        // Ensure we end close to target
        if (i === hours) {
            currentPrice = endPrice;
        }
        
        // Only include hourly data points (every hour)
        const timestamp = startTimestamp + (i * 60 * 60 * 1000);
        prices.push([timestamp, Math.max(100, currentPrice)]);
    }
    
    return prices;
}

// May 2021 Crypto Crash: BTC $58K → $31K (-47%) over 11 days
// Generate with severe crash that exceeds -10% drawdown limit
function generateMay2021Crash() {
    const startPrice = 58000;
    const endPrice = 31000;
    const days = 11;
    const prices = generateCrashPriceSeries(startPrice, endPrice, days, 0.05);
    const startTimestamp = new Date('2021-05-12').getTime();
    return prices.map((p, i) => [startTimestamp + (i * 60 * 60 * 1000), p[1]]);
}

// March 2020 COVID Crash: BTC $9K → $4.8K (-46%) over 14 days  
function generateMarch2020Crash() {
    const startPrice = 9000;
    const endPrice = 4800;
    const days = 14;
    // Adjust timestamp for March 2020
    const prices = generateCrashPriceSeries(startPrice, endPrice, days, 0.06);
    const startTimestamp = new Date('2020-03-09').getTime();
    return prices.map((p, i) => [startTimestamp + (i * 60 * 60 * 1000), p[1]]);
}

// FTX Collapse Nov 2022: BTC $21K → $15.5K (-26%) over 8 days
function generateFTXCollapse() {
    const startPrice = 21000;
    const endPrice = 15500;
    const days = 8;
    // Adjust timestamp for November 2022
    const prices = generateCrashPriceSeries(startPrice, endPrice, days, 0.04);
    const startTimestamp = new Date('2022-11-06').getTime();
    return prices.map((p, i) => [startTimestamp + (i * 60 * 60 * 1000), p[1]]);
}

// Generate all crises data
const crises = {
    'may-2021': {
        name: 'May 2021 Crypto Crash',
        dateRange: 'May 12-23, 2021',
        prices: generateMay2021Crash()
    },
    'march-2020': {
        name: 'March 2020 COVID Crash',
        dateRange: 'March 9-23, 2020',
        prices: generateMarch2020Crash()
    },
    'ftx-2022': {
        name: 'FTX Collapse Nov 2022',
        dateRange: 'November 6-14, 2022',
        prices: generateFTXCollapse()
    }
};

// Save to JSON
const outputPath = path.join(__dirname, '..', 'historical-price-data.json');
fs.writeFileSync(outputPath, JSON.stringify(crises, null, 2));
console.log(`Generated historical price data saved to: ${outputPath}`);
console.log(`May 2021: ${crises['may-2021'].prices.length} data points`);
console.log(`March 2020: ${crises['march-2020'].prices.length} data points`);
console.log(`FTX 2022: ${crises['ftx-2022'].prices.length} data points`);

module.exports = { crises };
