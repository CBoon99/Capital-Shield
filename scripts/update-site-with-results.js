/**
 * Parse simulation results and update HTML/JS files with real calculated data
 */

const fs = require('fs');
const path = require('path');

// Read simulation results
const resultsPath = path.join(__dirname, '..', 'simulation-results.json');
const results = JSON.parse(fs.readFileSync(resultsPath, 'utf8'));

// Extract key metrics
const may2021 = results.results[0];
const march2020 = results.results[1];
const ftx2022 = results.results[2];

// Calculate capital preserved (difference in lowest values)
const may2021CapitalPreserved = Math.max(0, may2021.shielded.lowestValue - may2021.unshielded.lowestValue);
const march2020CapitalPreserved = Math.max(0, march2020.shielded.lowestValue - march2020.unshielded.lowestValue);
const ftx2022CapitalPreserved = Math.max(0, ftx2022.shielded.lowestValue - ftx2022.unshielded.lowestValue);

// Calculate total capital preserved
const totalCapitalPreserved = may2021CapitalPreserved + march2020CapitalPreserved + ftx2022CapitalPreserved;

// Get blocked trade breakdowns
const may2021Blocked = may2021.shielded.blockedByReason;
const march2020Blocked = march2020.shielded.blockedByReason;
const ftx2022Blocked = ftx2022.shielded.blockedByReason;

// Get sample blocked trades
const may2021SampleTrades = may2021.shielded.blockedLog.slice(0, 5);
const march2020SampleTrades = march2020.shielded.blockedLog.slice(0, 5);
const ftx2022SampleTrades = ftx2022.shielded.blockedLog.slice(0, 5);

// Calculate combined metrics
const worstDrawdown = Math.min(
    may2021.unshielded.maxDrawdown,
    march2020.unshielded.maxDrawdown,
    ftx2022.unshielded.maxDrawdown
);

const shieldedDrawdown = Math.min(
    may2021.shielded.maxDrawdown,
    march2020.shielded.maxDrawdown,
    ftx2022.shielded.maxDrawdown
);

// Find largest single loss prevented
const allBlockedTrades = [
    ...may2021.shielded.blockedLog,
    ...march2020.shielded.blockedLog,
    ...ftx2022.shielded.blockedLog
];
const largestLossPrevented = allBlockedTrades.length > 0 
    ? Math.max(...allBlockedTrades.map(t => t.estimatedLoss || 0))
    : 0;

console.log('=== EXTRACTED METRICS ===\n');
console.log('May 2021:');
console.log(`  Unshielded Max DD: ${(may2021.unshielded.maxDrawdown * 100).toFixed(1)}%`);
console.log(`  Shielded Max DD: ${(may2021.shielded.maxDrawdown * 100).toFixed(1)}%`);
console.log(`  Trades Blocked: ${may2021.shielded.tradesBlocked}`);
console.log(`  Capital Preserved: £${may2021CapitalPreserved.toFixed(0)}`);
console.log(`  Blocked Breakdown: DD=${may2021Blocked.DD_BREACH}, VOL=${may2021Blocked.VOL_BREACH}, REGIME=${may2021Blocked.REGIME_GUARD}`);

console.log('\nMarch 2020:');
console.log(`  Unshielded Max DD: ${(march2020.unshielded.maxDrawdown * 100).toFixed(1)}%`);
console.log(`  Shielded Max DD: ${(march2020.shielded.maxDrawdown * 100).toFixed(1)}%`);
console.log(`  Trades Blocked: ${march2020.shielded.tradesBlocked}`);
console.log(`  Capital Preserved: £${march2020CapitalPreserved.toFixed(0)}`);
console.log(`  Blocked Breakdown: DD=${march2020Blocked.DD_BREACH}, VOL=${march2020Blocked.VOL_BREACH}, REGIME=${march2020Blocked.REGIME_GUARD}`);

console.log('\nFTX 2022:');
console.log(`  Unshielded Max DD: ${(ftx2022.unshielded.maxDrawdown * 100).toFixed(1)}%`);
console.log(`  Shielded Max DD: ${(ftx2022.shielded.maxDrawdown * 100).toFixed(1)}%`);
console.log(`  Trades Blocked: ${ftx2022.shielded.tradesBlocked}`);
console.log(`  Capital Preserved: £${ftx2022CapitalPreserved.toFixed(0)}`);
console.log(`  Blocked Breakdown: DD=${ftx2022Blocked.DD_BREACH}, VOL=${ftx2022Blocked.VOL_BREACH}, REGIME=${ftx2022Blocked.REGIME_GUARD}`);

console.log('\n=== COMBINED METRICS ===');
console.log(`Total Trades Blocked: ${results.totalTradesBlocked}`);
console.log(`Total Capital Preserved: £${totalCapitalPreserved.toFixed(0)}`);
console.log(`Worst Drawdown: ${(worstDrawdown * 100).toFixed(1)}%`);
console.log(`Shielded Drawdown: ${(shieldedDrawdown * 100).toFixed(1)}%`);
console.log(`Largest Loss Prevented: £${largestLossPrevented.toFixed(0)}`);

// Export data for updating HTML/JS
const exportData = {
    may2021: {
        unshieldedDD: may2021.unshielded.maxDrawdown * 100,
        shieldedDD: may2021.shielded.maxDrawdown * 100,
        tradesBlocked: may2021.shielded.tradesBlocked,
        capitalPreserved: may2021CapitalPreserved,
        blockedBreakdown: may2021Blocked,
        sampleTrades: may2021SampleTrades,
        chartData: may2021.chartData
    },
    march2020: {
        unshieldedDD: march2020.unshielded.maxDrawdown * 100,
        shieldedDD: march2020.shielded.maxDrawdown * 100,
        tradesBlocked: march2020.shielded.tradesBlocked,
        capitalPreserved: march2020CapitalPreserved,
        blockedBreakdown: march2020Blocked,
        sampleTrades: march2020SampleTrades,
        chartData: march2020.chartData
    },
    ftx2022: {
        unshieldedDD: ftx2022.unshielded.maxDrawdown * 100,
        shieldedDD: ftx2022.shielded.maxDrawdown * 100,
        tradesBlocked: ftx2022.shielded.tradesBlocked,
        capitalPreserved: ftx2022CapitalPreserved,
        blockedBreakdown: ftx2022Blocked,
        sampleTrades: ftx2022SampleTrades,
        chartData: ftx2022.chartData
    },
    combined: {
        totalTradesBlocked: results.totalTradesBlocked,
        totalCapitalPreserved: totalCapitalPreserved,
        worstDrawdown: worstDrawdown * 100,
        shieldedDrawdown: shieldedDrawdown * 100,
        largestLossPrevented: largestLossPrevented
    }
};

const exportPath = path.join(__dirname, '..', 'site-update-data.json');
fs.writeFileSync(exportPath, JSON.stringify(exportData, null, 2));
console.log(`\n\nExport data saved to: ${exportPath}`);

module.exports = exportData;
