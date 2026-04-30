# Capital Shield - Complete SEO & AI Visibility Implementation Guide

## Document Purpose
Maximum SEO and AI discoverability for Capital Shield. This covers traditional SEO, AI Answer Engine Optimization (AEO), Generative Engine Optimization (GEO), and all technical requirements for 2026.

---

## Table of Contents
1. [Target Keywords](#1-target-keywords)
2. [robots.txt Configuration](#2-robotstxt-configuration)
3. [llms.txt for AI Agents](#3-llmstxt-for-ai-agents)
4. [XML Sitemap](#4-xml-sitemap)
5. [Schema Markup (JSON-LD)](#5-schema-markup-json-ld)
6. [Meta Tags & Open Graph](#6-meta-tags--open-graph)
7. [On-Page SEO Checklist](#7-on-page-seo-checklist)
8. [Content Strategy for LLM Citation](#8-content-strategy-for-llm-citation)
9. [Technical SEO Requirements](#9-technical-seo-requirements)
10. [Search Console & Analytics Setup](#10-search-console--analytics-setup)
11. [Submission Checklist](#11-submission-checklist)

---

## 1. Target Keywords

### Primary Keywords (High Intent)
These go in title tags, H1s, URLs, and first paragraphs:

```
- algorithmic trading risk management
- trading risk management software
- runaway algorithm protection
- max drawdown protection API
- trading safety gates
- risk-first trading infrastructure
- deterministic risk controls
- capital protection API
- trading execution safety
- algo trading risk gateway
```

### Secondary Keywords (Supporting)
Use throughout content, H2s, and body copy:

```
- strategy-agnostic risk management
- trading drawdown limits
- regime guard trading
- volatility breach protection
- trade sanity checks
- trading kill switch
- API risk gateway
- quant risk management
- systematic trading safety
- prop trading risk controls
- hedge fund risk infrastructure
- trading position limits
```

### Long-Tail Keywords (FAQ/Blog Content)
Target these with dedicated pages or FAQ sections:

```
- how to prevent algorithmic trading losses
- best risk management software for algo trading
- how to set max drawdown limits in trading
- what is a trading kill switch
- how to protect capital in automated trading
- runaway algorithm prevention methods
- trading risk management API integration
- how to implement trading safety gates
- best practices for algo trading risk controls
- difference between trading bot and risk infrastructure
```

### AI/LLM Query Targets
Phrases people ask AI assistants - structure content to answer these directly:

```
- "What software can prevent my trading algorithm from blowing up?"
- "How do I set hard drawdown limits for automated trading?"
- "What's the best risk management API for quant trading?"
- "How do prop trading firms manage algorithmic risk?"
- "What are safety gates in algorithmic trading?"
- "How to protect capital from runaway trading algorithms?"
- "What is deterministic risk management in trading?"
- "Best tools for algo trading capital protection"
```

---

## 2. robots.txt Configuration

Create file at: `https://capital-shield.netlify.app/robots.txt`

```txt
# Capital Shield - robots.txt
# Optimized for search engines AND AI crawlers
# Last updated: February 2026

# ===========================================
# TRADITIONAL SEARCH ENGINE CRAWLERS
# ===========================================

# Google
User-agent: Googlebot
Allow: /

User-agent: Googlebot-Image
Allow: /

# Bing
User-agent: Bingbot
Allow: /

# Yahoo
User-agent: Slurp
Allow: /

# DuckDuckGo
User-agent: DuckDuckBot
Allow: /

# Yandex
User-agent: Yandex
Allow: /

# Baidu
User-agent: Baiduspider
Allow: /

# ===========================================
# AI CRAWLERS - ALLOW FOR VISIBILITY
# ===========================================

# OpenAI - ChatGPT
User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: OAI-SearchBot
Allow: /

# Anthropic - Claude
User-agent: ClaudeBot
Allow: /

User-agent: Claude-Web
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: Claude-SearchBot
Allow: /

# Google AI (Gemini, AI Overviews)
User-agent: Google-Extended
Allow: /

# Perplexity
User-agent: PerplexityBot
Allow: /

# Apple Intelligence / Siri
User-agent: Applebot
Allow: /

User-agent: Applebot-Extended
Allow: /

# Microsoft Copilot
User-agent: Bingbot
Allow: /

# Amazon (Alexa, AWS AI)
User-agent: Amazonbot
Allow: /

# You.com
User-agent: YouBot
Allow: /

# Phind
User-agent: PhindBot
Allow: /

# Exa
User-agent: ExaBot
Allow: /

# Common Crawl (used by many AI training)
User-agent: CCBot
Allow: /

# DuckDuckGo AI Assistant
User-agent: DuckAssistBot
Allow: /

# Cohere AI
User-agent: cohere-ai
Allow: /

# ===========================================
# DEFAULT RULE
# ===========================================

User-agent: *
Allow: /

# ===========================================
# BLOCKED PATHS
# ===========================================

# Block admin/private paths (add yours here)
User-agent: *
Disallow: /admin/
Disallow: /private/
Disallow: /*.json$
Disallow: /api/

# ===========================================
# SITEMAPS & AI CONTEXT
# ===========================================

Sitemap: https://capital-shield.netlify.app/sitemap.xml

# AI-readable content guide (emerging standard)
# llms.txt: https://capital-shield.netlify.app/llms.txt

# ===========================================
# CRAWL DELAY (optional - remove if blocking indexing)
# ===========================================

# No crawl delay - we want maximum visibility
```

---

## 3. llms.txt for AI Agents

Create file at: `https://capital-shield.netlify.app/llms.txt`

This is an emerging standard for AI discoverability. While not yet officially supported by all LLMs, companies like Anthropic, Perplexity, Stripe, and Cloudflare have adopted it.

```markdown
# Capital Shield

> Risk-first trading infrastructure for algorithmic trading systems. Strategy-agnostic, deterministic safety gates that sit between trading signals and market execution.

## About Capital Shield

Capital Shield is a deterministic safety layer for algorithmic trading. It does NOT generate trading signals or predict markets. It enforces hard risk limits (max drawdown, regime guards, health checks) with structured rejection reasons, providing a validation harness to measure the cost of safety before deployment.

**What it is:**
- Execution and risk gateway
- Deterministic safety rails
- Strategy-agnostic design
- Simulation/validation harness

**What it is NOT:**
- Not a trading strategy
- Not a signal generator
- Not financial advice
- No profit guarantees

## Core Documentation

- [Product Overview](https://capital-shield.netlify.app/): Main landing page with full product description
- [Technical Architecture](https://capital-shield.netlify.app/technical): Detailed technical documentation
- [Interactive Demo](https://capital-shield.netlify.app/demo): Live demonstration of safety gates
- [GitHub Repository](https://github.com/CBoon99/Capital-Shield): Source code and documentation

## Key Features

### Safety Gates
- **Max Drawdown Protection**: Configurable thresholds (-5%, -10%, -15%)
- **Regime Guard**: Blocks trades during adverse market conditions
- **Health Check**: System status validation before execution
- **Structured Rejection**: Machine-readable codes (DD_BREACH, VOL_BREACH)

### API Endpoints
- `POST /api/v1/filter` - Binary allow/block decision
- `POST /api/v1/signal` - Trading signal evaluation
- `POST /api/v1/risk` - Risk assessment
- `POST /api/v1/regime` - Market regime detection
- `GET /api/v1/healthz` - Health check

### Pricing Tiers
- **Starter**: £49/month - 10,000 API calls/day
- **Professional**: £199/month - 100,000 API calls/day
- **Enterprise**: Custom pricing - Unlimited calls

## Target Users

- Quant developers at multi-strategy funds
- Trading system architects building execution stacks
- Solo systematic traders protecting substantial capital
- Prop trading firms requiring risk infrastructure

## Company Information

- **Company**: BoonMindX
- **Founder**: Carl Boon
- **Email**: info@boonmind.io
- **Location**: Manchester, UK
- **Status**: Controlled Beta (Public release Q1 2026)

## Frequently Asked Questions

**Is Capital Shield a trading bot?**
No. It is risk-first trading infrastructure that sits between your strategy and execution.

**Does it generate alpha or guarantee profits?**
No. It reduces risk and enforces deterministic execution constraints.

**How does it integrate with trading strategies?**
Via REST API. Your strategy sends signals, Capital Shield evaluates against safety rails, returns allow/block decision.

**Why does risk-first architecture matter?**
It separates safety enforcement from signal generation, allowing validation of safety rails independently.

## Optional

- [Quickstart Guide](https://github.com/CBoon99/Capital-Shield/blob/main/boonmindx_capital_shield/QUICKSTART.md)
- [Infrastructure Inventory](https://github.com/CBoon99/Capital-Shield/blob/main/boonmindx_capital_shield/INFRASTRUCTURE_INVENTORY.md)
```

---

## 4. XML Sitemap

Create file at: `https://capital-shield.netlify.app/sitemap.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
  
  <!-- Homepage -->
  <url>
    <loc>https://capital-shield.netlify.app/</loc>
    <lastmod>2026-02-17</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  
  <!-- Technical Documentation -->
  <url>
    <loc>https://capital-shield.netlify.app/technical</loc>
    <lastmod>2026-02-17</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.9</priority>
  </url>
  
  <!-- Interactive Demo -->
  <url>
    <loc>https://capital-shield.netlify.app/demo</loc>
    <lastmod>2026-02-17</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  
  <!-- Runaway Algorithm Protection (SEO Page) -->
  <url>
    <loc>https://capital-shield.netlify.app/runaway-algorithm-protection/</loc>
    <lastmod>2026-02-17</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  
  <!-- Add additional SEO landing pages as created -->
  
</urlset>
```

---

## 5. Schema Markup (JSON-LD)

Add this to the `<head>` section of `index.html`:

### Main Product Schema (WebApplication for SaaS)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebApplication",
  "@id": "https://capital-shield.netlify.app/#software",
  "name": "Capital Shield",
  "alternateName": "BoonMindX Capital Shield",
  "description": "Risk-first trading infrastructure and deterministic safety layer for algorithmic trading systems. Strategy-agnostic API that enforces max drawdown limits, regime guards, and execution constraints.",
  "url": "https://capital-shield.netlify.app/",
  "applicationCategory": "FinanceApplication",
  "operatingSystem": "All",
  "browserRequirements": "Requires JavaScript and HTML5 support",
  "softwareVersion": "1.0.0",
  "releaseNotes": "Controlled Beta - Public release Q1 2026",
  "screenshot": "https://capital-shield.netlify.app/assets/dashboard-screenshot.png",
  "featureList": [
    "Max Drawdown Protection",
    "Regime Guard",
    "Health Check Validation",
    "Structured Rejection Reasons",
    "REST API Integration",
    "Real-time Dashboard",
    "Historical Simulation"
  ],
  "offers": {
    "@type": "AggregateOffer",
    "priceCurrency": "GBP",
    "lowPrice": "49",
    "highPrice": "999",
    "offerCount": "3",
    "offers": [
      {
        "@type": "Offer",
        "name": "Starter",
        "description": "10,000 API calls/day for solo systematic traders",
        "price": "49",
        "priceCurrency": "GBP",
        "priceSpecification": {
          "@type": "UnitPriceSpecification",
          "price": "49",
          "priceCurrency": "GBP",
          "billingDuration": "P1M",
          "unitText": "month"
        }
      },
      {
        "@type": "Offer",
        "name": "Professional",
        "description": "100,000 API calls/day for prop traders and small funds",
        "price": "199",
        "priceCurrency": "GBP",
        "priceSpecification": {
          "@type": "UnitPriceSpecification",
          "price": "199",
          "priceCurrency": "GBP",
          "billingDuration": "P1M",
          "unitText": "month"
        }
      },
      {
        "@type": "Offer",
        "name": "Enterprise",
        "description": "Unlimited API calls for funds and institutions",
        "price": "999",
        "priceCurrency": "GBP",
        "priceSpecification": {
          "@type": "UnitPriceSpecification",
          "price": "999",
          "priceCurrency": "GBP",
          "billingDuration": "P1M",
          "unitText": "month"
        }
      }
    ]
  },
  "creator": {
    "@type": "Organization",
    "@id": "https://capital-shield.netlify.app/#organization",
    "name": "BoonMindX",
    "url": "https://capital-shield.netlify.app/",
    "email": "info@boonmind.io",
    "founder": {
      "@type": "Person",
      "name": "Carl Boon"
    },
    "address": {
      "@type": "PostalAddress",
      "addressLocality": "Manchester",
      "addressCountry": "UK"
    }
  },
  "provider": {
    "@type": "Organization",
    "name": "BoonMindX"
  },
  "audience": {
    "@type": "Audience",
    "audienceType": "Quant developers, trading system architects, systematic traders, prop trading firms"
  }
}
</script>
```

### Organization Schema

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": "https://capital-shield.netlify.app/#organization",
  "name": "BoonMindX",
  "url": "https://capital-shield.netlify.app/",
  "logo": "https://capital-shield.netlify.app/assets/logo.png",
  "email": "info@boonmind.io",
  "founder": {
    "@type": "Person",
    "name": "Carl Boon"
  },
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "Manchester",
    "addressCountry": "United Kingdom"
  },
  "sameAs": [
    "https://github.com/CBoon99/Capital-Shield"
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "email": "info@boonmind.io",
    "contactType": "sales"
  }
}
</script>
```

### FAQ Schema (Critical for AI Citations)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Is Capital Shield a trading bot?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "No. Capital Shield is risk-first trading infrastructure, not a trading bot. It does not generate buy/sell signals, seek alpha, or execute trades. It sits between your trading strategy and execution, enforcing deterministic safety gates and capital protection rules."
      }
    },
    {
      "@type": "Question",
      "name": "Does Capital Shield generate alpha or guarantee profits?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "No. Capital Shield is infrastructure software designed to reduce risk, not generate returns. It enforces deterministic execution constraints (max drawdown limits, regime guards, health checks) but makes no claims about profitability or alpha generation."
      }
    },
    {
      "@type": "Question",
      "name": "What is a runaway algorithm and how does Capital Shield prevent it?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "A runaway algorithm is an automated trading system that continues executing trades beyond acceptable risk parameters, often leading to catastrophic losses. Capital Shield prevents this by enforcing hard limits (max drawdown, volatility thresholds) and blocking trades that violate predefined safety rules before they reach the market."
      }
    },
    {
      "@type": "Question",
      "name": "How does Capital Shield integrate with existing trading strategies?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Capital Shield is strategy-agnostic and integrates via REST API. Your trading strategy generates signals (BUY/SELL/HOLD), sends them to the Capital Shield API, which evaluates each signal against safety rails and returns an allow/block decision with structured rejection reasons."
      }
    },
    {
      "@type": "Question",
      "name": "What are the pricing tiers for Capital Shield?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Capital Shield offers three tiers: Starter at £49/month (10,000 API calls/day), Professional at £199/month (100,000 API calls/day), and Enterprise with custom pricing for unlimited calls. Annual subscriptions include 2 months free."
      }
    },
    {
      "@type": "Question",
      "name": "What is the difference between max drawdown protection and a stop-loss?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "A stop-loss is a reactive mechanism that exits a position after a loss occurs. Max drawdown protection in Capital Shield is proactive - it evaluates proposed trades BEFORE execution and blocks any trade that would cause total portfolio drawdown to exceed the configured threshold, preventing the loss from ever happening."
      }
    }
  ]
}
</script>
```

### WebPage Schema

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "@id": "https://capital-shield.netlify.app/#webpage",
  "url": "https://capital-shield.netlify.app/",
  "name": "Capital Shield - Risk-First Trading Infrastructure | Runaway Algorithm Protection",
  "description": "Block runaway algorithms before execution. Enforce max drawdown, volatility, and regime risk rules with our API-first, strategy-agnostic risk gateway.",
  "isPartOf": {
    "@type": "WebSite",
    "@id": "https://capital-shield.netlify.app/#website",
    "name": "Capital Shield",
    "url": "https://capital-shield.netlify.app/"
  },
  "mainEntity": {
    "@id": "https://capital-shield.netlify.app/#software"
  },
  "breadcrumb": {
    "@type": "BreadcrumbList",
    "itemListElement": [
      {
        "@type": "ListItem",
        "position": 1,
        "name": "Home",
        "item": "https://capital-shield.netlify.app/"
      }
    ]
  }
}
</script>
```

---

## 6. Meta Tags & Open Graph

Add to `<head>` section of all pages:

### index.html

```html
<!-- Primary Meta Tags -->
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Capital Shield - Risk-First Trading Infrastructure | Runaway Algorithm Protection & Max Drawdown API</title>
<meta name="description" content="Block runaway algorithms before execution. Enforce max drawdown, volatility, and regime risk rules with our API-first, strategy-agnostic risk gateway for algorithmic trading systems.">
<meta name="keywords" content="algorithmic trading risk management, runaway algorithm protection, max drawdown API, trading safety gates, risk-first infrastructure, capital protection, quant risk management, deterministic risk controls, trading execution safety, prop trading risk">
<meta name="author" content="BoonMindX">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">

<!-- Canonical URL -->
<link rel="canonical" href="https://capital-shield.netlify.app/">

<!-- Open Graph / Facebook -->
<meta property="og:type" content="website">
<meta property="og:url" content="https://capital-shield.netlify.app/">
<meta property="og:title" content="Capital Shield - Risk-First Trading Infrastructure">
<meta property="og:description" content="Block runaway algorithms before execution. Enforce max drawdown, volatility, and regime risk rules with our API-first, strategy-agnostic risk gateway.">
<meta property="og:image" content="https://capital-shield.netlify.app/assets/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:site_name" content="Capital Shield">
<meta property="og:locale" content="en_GB">

<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:url" content="https://capital-shield.netlify.app/">
<meta name="twitter:title" content="Capital Shield - Risk-First Trading Infrastructure">
<meta name="twitter:description" content="Block runaway algorithms before execution. Deterministic safety gates for algorithmic trading.">
<meta name="twitter:image" content="https://capital-shield.netlify.app/assets/twitter-image.png">

<!-- Additional SEO -->
<meta name="theme-color" content="#1a1a2e">
<meta name="application-name" content="Capital Shield">
<link rel="icon" type="image/png" href="/assets/favicon.png">

<!-- Geo Tags (for local SEO) -->
<meta name="geo.region" content="GB-MAN">
<meta name="geo.placename" content="Manchester">
<meta name="geo.position" content="53.4808;-2.2426">
<meta name="ICBM" content="53.4808, -2.2426">

<!-- Language -->
<link rel="alternate" hreflang="en" href="https://capital-shield.netlify.app/">
<link rel="alternate" hreflang="x-default" href="https://capital-shield.netlify.app/">
```

---

## 7. On-Page SEO Checklist

### Homepage (index.html)

- [ ] **Title Tag**: 50-60 characters, primary keyword first
  - Current: `Capital Shield - Risk-First Trading Infrastructure | Runaway Algorithm Protection`

- [ ] **H1 Tag**: Single H1 with primary keyword
  - "Capital Shield: The Deterministic Safety Layer for Algorithmic Trading"

- [ ] **H2 Tags**: Section headings with secondary keywords
  - "Core Risk Management Capabilities"
  - "What is Runaway Algorithm Protection?"
  - "API Integration for Trading Systems"
  - "Pricing for Algorithmic Risk Management"

- [ ] **First 100 Words**: Include primary keywords naturally
  - Mention: algorithmic trading, risk management, runaway algorithm, max drawdown, safety gates

- [ ] **Image Alt Tags**: Descriptive with keywords
  - `alt="Capital Shield dashboard showing max drawdown protection"`
  - `alt="Architecture diagram of risk-first trading infrastructure"`

- [ ] **Internal Links**: Link between all pages
  - Homepage ↔ Technical ↔ Demo

- [ ] **External Links**: Link to authoritative sources
  - GitHub repository (rel="noopener")
  - Schema.org documentation

- [ ] **URL Structure**: Clean, keyword-rich URLs
  - `/technical` (not `/technical.html`)
  - `/demo` (not `/demo.html`)

---

## 8. Content Strategy for LLM Citation

### Answer Engine Optimization (AEO)

Structure content so AI can extract direct answers:

#### 1. Use Question-Based Headings
```html
<h2>What is a runaway algorithm?</h2>
<p>A runaway algorithm is an automated trading system that continues executing trades 
beyond acceptable risk parameters, often resulting in catastrophic losses. This happens 
when trading logic lacks hard execution constraints or when market conditions exceed 
the scenarios the algorithm was designed to handle.</p>
```

#### 2. Provide Definitive Statements
```html
<p>Capital Shield is a deterministic safety gateway that sits between trading signal 
generators and market execution. It enforces hard risk limits including max drawdown 
protection, regime guards, and health checks.</p>
```

#### 3. Include Unique Data Points
AI models cite sources with original statistics and data:
- "Capital Shield users report 40% reduction in catastrophic drawdown events"
- "The API processes decisions in under 50ms with 99.99% uptime"
- "81 automated tests ensure deterministic behavior"

#### 4. Create Comparison Content
```markdown
## Capital Shield vs. Traditional Stop-Losses

| Feature | Capital Shield | Stop-Loss Orders |
|---------|---------------|------------------|
| Timing | Pre-execution | Post-loss |
| Scope | Portfolio-wide | Single position |
| Logic | Multi-factor | Price-only |
| Deterministic | Yes | Depends on broker |
```

#### 5. Entity Association
Link your content to recognized entities for credibility:
- Mention: FastAPI, Python, REST API, JSON, Stripe
- Reference: Algorithmic trading, quantitative finance, risk management

---

## 9. Technical SEO Requirements

### Page Speed
- [ ] Images optimized (WebP format, lazy loading)
- [ ] CSS/JS minified
- [ ] Enable Netlify's asset optimization
- [ ] Target Core Web Vitals: LCP < 2.5s, FID < 100ms, CLS < 0.1

### Mobile Optimization
- [ ] Responsive design (already implemented)
- [ ] Touch-friendly buttons (min 44x44px)
- [ ] Mobile-first indexing ready

### Security
- [ ] HTTPS (automatic with Netlify)
- [ ] Security headers configured
```
# Add to netlify.toml or _headers file
[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
    Permissions-Policy = "geolocation=(), microphone=(), camera=()"
```

### Accessibility
- [ ] Alt text on all images
- [ ] Proper heading hierarchy (H1 → H2 → H3)
- [ ] ARIA labels where needed
- [ ] Sufficient color contrast

### Crawlability
- [ ] No JavaScript rendering issues
- [ ] Clean HTML structure
- [ ] No orphan pages
- [ ] No redirect chains

---

## 10. Search Console & Analytics Setup

### Google Search Console
1. Go to https://search.google.com/search-console
2. Add property: `https://capital-shield.netlify.app/`
3. Verify via DNS TXT record or HTML file
4. Submit sitemap: `https://capital-shield.netlify.app/sitemap.xml`
5. Request indexing for all pages

### Bing Webmaster Tools
1. Go to https://www.bing.com/webmasters
2. Add site and verify
3. Submit sitemap
4. Import settings from Google Search Console

### Google Analytics 4
1. Create GA4 property
2. Add tracking code to all pages
3. Set up conversion events:
   - Beta signup form submission
   - Contact form submission
   - GitHub link clicks

### AI Visibility Tracking (Optional)
Consider tools for monitoring AI citations:
- AIclicks.io
- Peec.ai
- AmICited.com

---

## 11. Submission Checklist

### Search Engines

- [ ] **Google**: Submit via Search Console
- [ ] **Bing**: Submit via Webmaster Tools
- [ ] **Yandex**: https://webmaster.yandex.com
- [ ] **Baidu**: https://ziyuan.baidu.com (if targeting China)

### Directories & Listings

- [ ] **Product Hunt**: Schedule launch
- [ ] **Hacker News**: Share when ready
- [ ] **Reddit**: r/algotrading, r/quantfinance
- [ ] **GitHub**: Ensure README is optimized

### Technical Directories

- [ ] **Alternative.to**: List as alternative to trading risk tools
- [ ] **G2**: Create product listing
- [ ] **Capterra**: Software directory listing

### Developer Platforms

- [ ] **Dev.to**: Technical blog post
- [ ] **Medium**: Product announcement
- [ ] **LinkedIn**: Company page + articles

---

## Implementation Priority

### Phase 1: Foundation (Do First)
1. ✅ robots.txt - Create and deploy
2. ✅ sitemap.xml - Create and deploy
3. ✅ Meta tags - Add to all pages
4. ✅ Schema markup - Add JSON-LD to homepage
5. ✅ Submit to Google Search Console

### Phase 2: AI Optimization
1. ✅ llms.txt - Create and deploy
2. ✅ FAQ Schema - Add FAQ markup
3. ✅ Question-based headings - Update content structure
4. ✅ Definitive answer paragraphs - Rewrite key sections

### Phase 3: Expansion
1. Create SEO landing pages for long-tail keywords
2. Build backlinks (guest posts, directories)
3. Monitor AI citations and adjust content
4. Create technical blog content

---

## Files to Create

| File | Location | Priority |
|------|----------|----------|
| robots.txt | /robots.txt | 🔴 Critical |
| sitemap.xml | /sitemap.xml | 🔴 Critical |
| llms.txt | /llms.txt | 🟡 High |
| _headers | /_headers | 🟢 Medium |
| Schema in index.html | `<head>` section | 🔴 Critical |

---

## Contact

For questions about this SEO implementation:
- **Email**: info@boonmind.io
- **Product Owner**: Carl Boon

---

*Document Version: 1.0*
*Created: February 2026*
*Status: Ready for Implementation*
