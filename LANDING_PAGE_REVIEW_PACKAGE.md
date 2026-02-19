# Capital Shield Landing Page & Product Funnel Review Package

**Date**: February 2026  
**Purpose**: Complete overview for Claude to review landing page and conversion funnel

---

## 📍 Current Deployment URL

**Live URL**: `https://capital-shield.netlify.app/`  
**Status**: Configured but may not be deployed yet (URLs reference this domain throughout)

---

## 🎯 Main Landing Page Structure

### File Location
- **Primary File**: `/index.html` (1,140 lines)
- **Styling**: `/styles.css`
- **JavaScript**: `/app.js`

### Page Sections (in order):
1. **Header/Navigation** - Logo, nav links, "Request Beta Access" CTA
2. **Hero Section** (#overview)
3. **System Positioning** - Diagram showing where Capital Shield sits
4. **What It Is / What It Isn't**
5. **Key Capabilities** (#capabilities)
6. **Pricing** (#pricing) ⭐
7. **Technical Architecture** (#architecture)
8. **Beta Status & Roadmap** (#beta)
9. **Quickstart** (#quickstart)
10. **Licensing** (#licensing)
11. **FAQ** (#faq)
12. **Contact Form** (#contact) ⭐
13. **Disclaimer**
14. **Footer**

---

## 💰 Pricing Section Details

### Location
- **Section ID**: `#pricing`
- **Position**: After Capabilities, before Technical Architecture
- **Lines**: 639-800 in index.html

### Pricing Tiers Display

#### 1. **Starter Tier**
- **Monthly**: £49/month
- **Annual**: £490/year (2 months free)
- **Features**:
  - 10,000 API calls/day
  - Live API access
  - Usage-based overages available
- **CTA Button**: "Get Started" → Links to `#contact`
- **Target**: Solo systematic traders

#### 2. **Professional Tier** (Most Popular)
- **Monthly**: £199/month
- **Annual**: £1,990/year (2 months free)
- **Features**:
  - 100,000 API calls/day
  - Live API access
  - Usage-based overages available
  - Priority support
- **CTA Button**: "Get Started" → Links to `#contact`
- **Visual**: Has "Most Popular" badge, highlighted border
- **Target**: Prop traders and small funds

#### 3. **Enterprise Tier**
- **Price**: Custom
- **Features**:
  - Unlimited API calls
  - Live API access
  - Dedicated support
  - Custom SLA
- **CTA Button**: "Contact Sales" → Links to `#contact`
- **Target**: Funds and institutions

#### 4. **Simulation-Only License** (Below main tiers)
- **Pricing**: £19/month OR £149 one-time perpetual
- **Description**: "Validate the cost of safety before committing to full protection"
- **CTA**: "Learn More" → Links to `#contact`
- **Includes**: Full access to historical simulation engine only
- **Excludes**: Live API access

### Pricing Toggle
- **Feature**: Monthly/Annual toggle switch
- **Default**: Shows Monthly pricing
- **Annual Benefit**: "2 months free" highlighted
- **JavaScript**: `togglePricing()` function in `app.js`

### Overage Information
- **Rate**: £0.0001 per additional API call beyond daily limit
- **Billing**: Calculated monthly, added to next invoice
- **Cap Option**: Users can set hard cap to prevent surprise bills

---

## 🚀 Signup/CTA Flow Analysis

### All CTAs Lead to Contact Form

**Current Flow**: Every "Get Started", "Sign Up", "Join Beta", or "Contact Sales" button links to `#contact` (the contact form section on the same page).

### CTA Locations & Text:

1. **Header** (Line 304):
   - Text: "Request Beta Access"
   - Link: `#contact`
   - Style: `btn btn-primary btn-small`

2. **Hero Section** (Lines 334-337):
   - "View Risk Demo" → `/demo` (separate page)
   - "Join Controlled Beta" → `#contact`
   - "Read the Docs" → `#quickstart`
   - "View on GitHub" → External GitHub link

3. **Pricing Section** (Lines 694, 738, 774, 790):
   - Starter: "Get Started" → `#contact`
   - Professional: "Get Started" → `#contact`
   - Enterprise: "Contact Sales" → `#contact`
   - Simulation-Only: "Learn More" → `#contact`

4. **Beta Section** (Line 907):
   - "Join Beta" → `#contact`

5. **Licensing Section** (Line 977):
   - "Discuss licensing" → `mailto:info@boonmind.io?subject=Licensing%20Inquiry`

### Contact Form Details

**Location**: `#contact` section (Lines 1047-1104)

**Form Fields**:
1. Name (required)
2. Email (required)
3. Primary Trading Stack (required)
4. Biggest Risk Management Pain Point (required, textarea)
5. Current biggest risk worry? (optional dropdown)
   - Options: Runaway algorithm, Silent failures, Regime shifts, Other
6. Additional Information (optional, textarea)

**Form Submission**:
- **Method**: POST
- **Action**: `/thanks/` (Netlify form handler)
- **Handler**: Netlify Forms (`data-netlify="true"`)
- **Honeypot**: `bot-field` for spam protection
- **Button Text**: "Apply for Beta Access"

**Post-Submission**:
- Redirects to `/thanks/` page
- Netlify processes form submission
- Email sent to configured Netlify email

### ⚠️ Current Flow Issue

**Problem**: All pricing CTAs go to the same contact form, not to Stripe checkout or a dedicated signup flow.

**Expected Flow** (per implementation brief):
- User clicks "Get Started" on pricing tier
- Should redirect to Stripe checkout OR contact form with tier pre-selected
- Currently: Just scrolls to generic contact form

**Missing**:
- No Stripe checkout integration in frontend
- No tier pre-selection in contact form
- No dedicated signup page
- No API key generation flow

---

## 📝 Key Copy & Messaging

### Hero Section

**H1**: "Capital Shield: The Deterministic Safety Layer for Algorithmic Trading"

**Subtitle**: "Block runaway algorithms before execution. Enforce max drawdown, volatility, and regime risk rules with our API-first, strategy-agnostic risk gateway."

**Key Value Props**:
- "Capital Shield is not a trading strategy. It does not predict markets or generate alpha."
- "It is a deterministic safety layer that evaluates proposed trades and blocks those that violate predefined risk, regime, or capital-preservation rules."
- "This risk-first infrastructure protects capital, not generates returns."

**Badges**:
- Controlled Beta
- API-first
- Strategy-agnostic
- Q1 2026 public release

### Value Proposition Table

**"The Cost of Being Unshielded"** comparison table:
- Unshielded: Strategy signal → Immediate Execution
- Shielded: Strategy signal → Safety Gates → ALLOW/BLOCK → Execution

### What It Is / What It Isn't

**What It Is**:
- Execution + risk gateway
- Deterministic safety rails
- Strategy-agnostic design
- Simulation/validation harness

**What It Isn't**:
- Not a strategy
- Not a signal generator
- No profit claims
- Not financial advice

### Key Differentiators

1. **Strategy-agnostic** - Works with any trading strategy
2. **Deterministic** - Same inputs produce same outputs
3. **Pre-execution** - Blocks trades BEFORE they reach market
4. **Structured rejection** - Machine-readable codes (DD_BREACH, VOL_BREACH)
5. **Risk-first** - Infrastructure, not alpha generation

### Target Audience Messaging

**Who It's For**:
- Quant developers at multi-strategy funds
- Trading system architects building execution stacks
- Solo systematic traders protecting substantial capital
- Prop trading firms requiring risk infrastructure

### Pain Points Addressed

1. **Runaway algorithms** - Prevents catastrophic losses
2. **Silent failures** - Structured logging and rejection reasons
3. **Regime-blind execution** - Regime guard blocks trades in adverse conditions
4. **Risk logic buried in code** - Centralized, strategy-agnostic safety gates

---

## 🎨 Design & UX Notes

### Color Scheme
- Primary Accent: `#2EA8FF` (blue)
- Secondary Accent: `#7C5CFF` (purple)
- Background: Dark (`#071225`, `#0B1B33`)
- Text: Light (`#EAF2FF`)

### Button Styles
- `btn-primary`: Primary CTA (blue background)
- `btn-secondary`: Secondary CTA (outlined)
- `btn-small`: Smaller variant

### Responsive Design
- Mobile-friendly
- Uses CSS Grid for layouts
- Smooth scroll navigation

---

## 🔗 Navigation Flow

### Header Navigation Links:
- Overview → `#overview`
- Capabilities → `#capabilities`
- Architecture → `#architecture`
- Interactive Demo → `/demo`
- Quickstart → `#quickstart`
- Beta → `#beta`
- Licensing → `#licensing`
- Contact → `#contact`
- Technical → `technical.html`

### Internal Linking:
- Multiple links to `#contact` throughout
- Links to `/demo` for interactive demo
- Links to `technical.html` for technical docs
- Links to GitHub repository

---

## 📊 Conversion Funnel Analysis

### Current Funnel:

1. **Landing** → Hero section with value prop
2. **Education** → Capabilities, What It Is/Isn't, System Positioning
3. **Pricing** → Three tiers + simulation-only option
4. **CTA** → "Get Started" buttons
5. **Contact Form** → Generic beta signup form
6. **Submission** → Redirects to `/thanks/` page

### Funnel Gaps:

1. **No tier selection** - Contact form doesn't capture which tier user selected
2. **No payment flow** - No Stripe checkout integration visible
3. **No immediate value** - No free trial or demo access
4. **Generic form** - Same form for all tiers (Starter, Professional, Enterprise)
5. **No API key generation** - No post-signup flow to get API key

### Recommended Improvements:

1. Add tier parameter to contact form (hidden field)
2. Create Stripe checkout links for Starter/Professional
3. Add "Start Free Trial" option
4. Create dedicated signup page with tier selection
5. Add post-signup API key generation flow

---

## 📧 Contact Information

- **Email**: info@boonmind.io
- **Company**: BoonMindX
- **Founder**: Carl Boon
- **Location**: Manchester, UK
- **Status**: Controlled Beta (Public release Q1 2026)

---

## 🔍 Technical Implementation Notes

### Form Handling
- Uses Netlify Forms
- Honeypot spam protection
- Form validation in JavaScript (`app.js`)
- Redirects to `/thanks/` on success

### Pricing Toggle
- JavaScript function: `togglePricing()`
- Toggles between `.pricing-monthly` and `.pricing-annual` elements
- Smooth transition animation

### Smooth Scrolling
- Anchor links use smooth scroll behavior
- Header offset for fixed navigation

---

## 📋 Summary for Review

### Strengths:
✅ Clear value proposition  
✅ Strong differentiation (not a trading bot)  
✅ Professional design  
✅ Comprehensive information architecture  
✅ Good SEO optimization  
✅ Mobile responsive  

### Areas for Improvement:
⚠️ All CTAs lead to same generic form  
⚠️ No Stripe checkout integration visible  
⚠️ No tier pre-selection in form  
⚠️ No immediate value (free trial/demo access)  
⚠️ Contact form doesn't capture pricing tier selection  
⚠️ No post-signup API key generation flow  

### Key Questions:
1. Should pricing CTAs go directly to Stripe checkout?
2. Should contact form include tier selection?
3. Should there be a free trial option?
4. What happens after form submission? (API key delivery?)
5. Should Enterprise tier have different flow (Calendly/email)?

---

*Document prepared for Claude review*  
*Last updated: February 2026*
