# Protection Evidence & Interactive Demo Implementation Plan

**Date**: February 2026  
**Status**: Plan for Review  
**Goal**: Add tangible protection evidence and interactive integration demo to Capital Shield landing page

---

## ✅ Understanding Confirmation

### Protection-Focused Framing (Not Performance-Focused)
- ✅ **No return metrics**: No Sharpe ratios, win rates, profit factors, or equity curves showing "better performance"
- ✅ **Protection metrics only**: Drawdown prevention, trades blocked, capital preserved, losses avoided
- ✅ **Crisis scenarios**: Show what Capital Shield prevents during real crashes
- ✅ **Deterministic rules**: Emphasize fail-closed defaults, configurable thresholds, not ML predictions
- ✅ **Integration simplicity**: Show it's trivial to add (3 lines, 1 API call)

### Current Site Structure
- **Main page**: `index.html` (1,140 lines)
- **Demo page**: `demo.html` (already exists with risk scenario simulator)
- **Styling**: `styles.css` (existing design system)
- **JavaScript**: `app.js` (smooth scroll, form handling)
- **Crash test data**: Available in `boonmindx_capital_shield/crash_test_results/`

---

## 📋 Detailed Implementation Plan

### ELEMENT 1: Protection Evidence Section

#### Placement Recommendation
**Location**: After "Core Capabilities" section, before "Pricing" section  
**Section ID**: `#protection-evidence`  
**Rationale**: 
- Natural flow: Capabilities → Evidence → Pricing
- Users see what it does, then see proof, then see cost
- Maintains existing section order

#### Section Structure

```html
<!-- Protection Evidence -->
<section class="section protection-evidence-section" id="protection-evidence">
    <div class="container">
        <h2 class="section-title section-title-center">Protection Evidence: What Capital Shield Prevents</h2>
        <p class="section-subtitle" style="text-align: center; color: var(--text-muted); margin-bottom: 48px;">
            Real numbers from historical crisis simulations. Capital Shield blocks trades that violate risk rules before execution.
        </p>
        
        <!-- 1. Crisis Simulation Results -->
        <div class="crisis-results">
            <!-- May 2021 Crypto Crash -->
            <!-- March 2020 COVID Crash -->
            <!-- FTX Collapse (Nov 2022) -->
        </div>
        
        <!-- 2. Drawdown Comparison Chart -->
        <div class="drawdown-chart-container">
            <!-- Chart.js or SVG visualization -->
        </div>
        
        <!-- 3. Blocked Trade Log Example -->
        <div class="blocked-trades-table">
            <!-- Sample table with rejection codes -->
        </div>
        
        <!-- 4. Key Protection Metrics -->
        <div class="protection-metrics-grid">
            <!-- Max drawdown prevented -->
            <!-- Total trades blocked -->
            <!-- Capital preserved -->
            <!-- Time to recovery -->
            <!-- Largest single loss prevented -->
        </div>
        
        <!-- 5. Methodology Summary -->
        <div class="methodology-summary">
            <!-- Link to /technical for details -->
        </div>
        
        <!-- Disclaimers -->
        <div class="protection-disclaimers">
            <!-- Required disclaimers -->
        </div>
    </div>
</section>
```

#### Technical Implementation Details

**1. Crisis Simulation Results Cards**
- **Layout**: 3-column grid (responsive: 1 column on mobile)
- **Data Source**: You provide actual numbers (I'll create structure)
- **Display**:
  - Crisis name + date
  - Unshielded max drawdown vs Shielded max drawdown
  - Number of trades blocked (with breakdown by rejection code)
  - Capital preserved (£ amount)
- **Styling**: Use existing `.capability-card` class pattern

**2. Drawdown Comparison Chart**
- **Library**: Chart.js (already used in dashboard)
- **Type**: Line chart
- **Data**: You provide equity curve data points
- **Lines**:
  - Unshielded (red, crashes hard)
  - Shielded (blue, capped at limit)
  - Limit threshold (dashed line)
- **Responsive**: Canvas-based, scales with container

**3. Blocked Trade Log Example**
- **Format**: HTML table (styled to match existing tables)
- **Columns**: Timestamp, Signal, Rejection Code, Reason, Would-Have-Lost
- **Data**: You provide sample data (I'll format)
- **Styling**: Use existing table styles from "Cost of Being Unshielded"

**4. Key Protection Metrics**
- **Layout**: 5-card grid (responsive: 2-3 columns on mobile)
- **Metrics**:
  - Max drawdown prevented: `-62% → -10%` (example)
  - Total trades blocked: `247 trades` (example)
  - Capital preserved: `£52,000 on £100K account` (example)
  - Time to recovery: `Shielded: 3 days vs Unshielded: 47 days` (example)
  - Largest single loss prevented: `£6,100` (example)
- **Styling**: Use existing stat card pattern

**5. Methodology Summary**
- **Content**: Brief explanation linking to `/technical`
- **Key points**:
  - Deterministic rules (not ML)
  - Configurable thresholds
  - Fail-closed defaults
- **Link**: "See technical architecture for details" → `/technical`

**6. Disclaimers**
- **Placement**: Bottom of section, subtle styling
- **Content**:
  - "Simulated results based on historical data. Past performance does not guarantee future results."
  - "Capital Shield reduces risk but cannot prevent all losses. Not financial advice."
  - "User is responsible for configuring appropriate risk limits for their strategy."

---

### ELEMENT 2: Interactive Integration Demo

#### Placement Recommendation
**Option A (Preferred)**: Enhance existing `/demo` page  
**Option B**: Add widget to hero section on homepage  
**Option C**: Add as new section after hero, before "System Positioning"

**Recommendation**: **Option A** - Enhance `/demo` page because:
- Demo page already exists with risk scenario simulator
- Keeps homepage focused on value prop
- Users can deep-dive when ready
- Can add prominent link from hero: "Try Interactive Demo"

#### Implementation Approach

**Current Demo Page Analysis**:
- Already has interactive risk scenario simulator
- Shows gate evaluation results
- Has preset scenarios (flash crash, choppy noise, healthy trend)
- Uses client-side JavaScript (no API calls)

**Enhancement Plan**:
1. **Add "API Integration Demo" Tab/Section** to existing demo page
2. **Create Simple API Sandbox Widget**:
   - Inputs: Signal (BUY/SELL), Asset, Current Drawdown %, 24h Volatility %, Max DD Limit
   - Button: "Check Trade"
   - Output: ALLOW/BLOCK with rejection code and reason
   - **Implementation**: Client-side JavaScript simulation (no real API call needed for demo)

**Alternative: Code Snippet with Copy Button**
- If API sandbox is too complex, show integration code
- 3-line example with copy button
- Link to full API docs

**Alternative: Integration Architecture Diagram**
- SVG diagram showing Capital Shield in trading stack
- Already exists in "System Positioning" section
- Can enhance with interactive hover states

---

## 🎨 Design & Styling Approach

### Maintain Existing Design
- ✅ Use existing CSS classes (`.section`, `.container`, `.capability-card`, etc.)
- ✅ Match existing color scheme (`var(--accent)`, `var(--text-muted)`, etc.)
- ✅ Use existing typography (Inter font, existing sizes)
- ✅ Follow existing spacing patterns (48px margins, 32px padding)
- ✅ No new CSS classes unless absolutely necessary

### Responsive Design
- ✅ Mobile-first: Stack cards vertically on small screens
- ✅ Charts: Responsive canvas (Chart.js handles this)
- ✅ Tables: Horizontal scroll on mobile (or card layout)
- ✅ Grid layouts: Use CSS Grid with `auto-fit` for flexibility

---

## 🔧 Technical Implementation Steps

### Step 1: Create Protection Evidence Section
1. Add new section to `index.html` after Capabilities (line ~637)
2. Create HTML structure for:
   - Crisis results cards
   - Chart container
   - Blocked trades table
   - Protection metrics grid
   - Methodology summary
   - Disclaimers
3. Add placeholder data (you'll replace with real data)
4. Style using existing classes

### Step 2: Add Chart.js (if not already loaded)
- Check if Chart.js is loaded (used in dashboard)
- If not, add CDN link: `<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>`
- Create chart initialization function
- Load chart data from placeholder (you'll provide real data)

### Step 3: Enhance Demo Page
1. Add "API Integration Demo" section to `demo.html`
2. Create simple form with trade inputs
3. Add client-side JavaScript to simulate API response
4. Display ALLOW/BLOCK decision with rejection codes
5. Style to match existing demo page

### Step 4: Add Navigation Links
1. Add "Protection Evidence" to header nav (optional)
2. Add link from hero: "See Protection Evidence" → `#protection-evidence`
3. Add link from Capabilities section: "View Evidence" → `#protection-evidence`

---

## 📊 Data Requirements (From You)

### Crisis Simulation Data Needed:
For each crisis (May 2021 Crypto, March 2020 COVID, FTX Collapse):
1. **Unshielded max drawdown**: e.g., `-62%`
2. **Shielded max drawdown**: e.g., `-10%`
3. **Trades blocked**: Total number, e.g., `247`
4. **Breakdown by rejection code**:
   - DD_BREACH: `142 trades`
   - VOL_BREACH: `68 trades`
   - REGIME_GUARD: `37 trades`
5. **Capital preserved**: e.g., `£52,000 on £100K account`
6. **Equity curve data**: Array of portfolio values over time (for chart)

### Blocked Trade Log Sample:
Need 5-10 example rows:
- Timestamp
- Signal (BUY/SELL)
- Asset
- Rejection Code
- Reason (human-readable)
- Would-Have-Lost (£ amount)

### Protection Metrics:
- Max drawdown prevented: `-62% → -10%`
- Total trades blocked: `247 trades`
- Capital preserved: `£52,000`
- Time to recovery: `3 days vs 47 days`
- Largest single loss prevented: `£6,100`

---

## 🚧 Challenges & Solutions

### Challenge 1: Chart Rendering
**Solution**: Use Chart.js (already in dashboard)
- Lightweight, responsive
- Easy to style to match site theme
- Can use static data (no API needed)

### Challenge 2: API Sandbox
**Solution**: Client-side JavaScript simulation
- No real API call needed for demo
- Deterministic logic matches production behavior
- Fast, no network dependency
- Can add note: "This is a simulation. Production uses REST API."

### Challenge 3: Data Format
**Solution**: 
- Use placeholder data in HTML/JS
- You provide real data in same format
- Easy to swap placeholders for real data

### Challenge 4: Mobile Responsiveness
**Solution**:
- Use CSS Grid with `auto-fit` for cards
- Chart.js is responsive by default
- Tables: Horizontal scroll or card layout on mobile
- Test on mobile viewport

### Challenge 5: Maintaining Existing Design
**Solution**:
- Strictly use existing CSS classes
- Match existing patterns (spacing, colors, typography)
- No new design elements
- Reuse existing components (cards, tables, sections)

---

## 📝 Implementation Checklist

### Phase 1: Structure (I'll do this)
- [ ] Add Protection Evidence section to `index.html`
- [ ] Create HTML structure for all sub-sections
- [ ] Add placeholder data
- [ ] Style using existing classes
- [ ] Add disclaimers

### Phase 2: Charts & Visualizations (I'll do this)
- [ ] Add Chart.js if needed
- [ ] Create drawdown comparison chart
- [ ] Add placeholder chart data
- [ ] Make responsive

### Phase 3: Interactive Demo (I'll do this)
- [ ] Enhance `/demo` page with API integration demo
- [ ] Create simple form widget
- [ ] Add client-side simulation logic
- [ ] Style to match existing demo

### Phase 4: Data Integration (You provide data)
- [ ] Replace placeholder crisis data with real numbers
- [ ] Replace placeholder chart data with real equity curves
- [ ] Replace placeholder blocked trades with real examples
- [ ] Replace placeholder metrics with real calculations

### Phase 5: Testing (Manual)
- [ ] Test on desktop browsers
- [ ] Test on mobile devices
- [ ] Verify all links work
- [ ] Verify charts render correctly
- [ ] Verify interactive demo works
- [ ] Check disclaimers are visible

---

## 🎯 Success Criteria

After implementation, a potential buyer should:
1. ✅ See concrete numbers on what Capital Shield prevents (drawdown, losses avoided)
2. ✅ Understand integration is trivial (3 lines of code, 1 API call)
3. ✅ Be able to try it themselves (interactive demo)
4. ✅ Trust the product because evidence is protection-focused, not "get rich" focused

---

## 📋 Next Steps

1. **Review this plan** - Confirm approach and placement
2. **Provide data** - Crisis simulation results, blocked trades, metrics
3. **I implement** - Structure, styling, placeholders
4. **You review** - Check design and flow
5. **Data swap** - Replace placeholders with real data
6. **Final testing** - Mobile, browsers, links

---

## ❓ Questions for You

1. **Data availability**: Do you have real crisis simulation data ready, or should I create realistic placeholders?
2. **Chart preference**: Chart.js (dynamic) or static SVG (simpler, no JS)?
3. **Demo location**: Enhance `/demo` page or add widget to homepage?
4. **Crisis selection**: Are May 2021 Crypto, March 2020 COVID, FTX Collapse the right ones, or different crises?
5. **Timeline**: Should I proceed with placeholders now, or wait for real data?

---

*Plan prepared for review before implementation*  
*Ready to proceed once approved*
