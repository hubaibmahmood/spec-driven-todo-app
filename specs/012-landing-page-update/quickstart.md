# Quickstart Guide: Landing Page Update

**Feature**: 012-landing-page-update
**Date**: 2025-12-29
**Audience**: Developers implementing the feature

## Overview

This guide provides step-by-step instructions for implementing the landing page update feature, including local development setup, testing, and deployment.

---

## Prerequisites

- Node.js 20+ installed
- Git repository access
- Branch `012-landing-page-update` checked out
- Environment variables configured (if needed)

---

## Development Setup

### 1. Install Dependencies

```bash
cd frontend
npm install  # or pnpm install
```

**Dependencies** (already in package.json):
- next@16.0.9
- react@19.2.1
- lucide-react@0.560.0
- better-auth@1.4.6
- tailwindcss@4

### 2. Start Development Server

```bash
npm run dev
```

**Expected output**:
```
  ▲ Next.js 16.0.9
  - Local:        http://localhost:3000
  - Ready in 2.1s
```

### 3. View Landing Page

Navigate to: `http://localhost:3000`

**Expected behavior**:
- If NOT logged in: Landing page renders
- If logged in: Auto-redirect to `/dashboard`

---

## Implementation Workflow

### Phase 1: Write Tests (RED)

**TDD Requirement**: Write tests BEFORE implementation

#### 1.1. Create Test Files

```bash
mkdir -p frontend/__tests__/landing-page
cd frontend/__tests__/landing-page

# Create test files
touch LandingPage.test.tsx
touch landing-cta.test.tsx
touch landing-responsive.test.tsx
touch landing-e2e.spec.ts
```

#### 1.2. Write Component Tests

**File**: `frontend/__tests__/landing-page/LandingPage.test.tsx`

```typescript
import { render, screen, waitFor } from '@testing-library/react';
import { useRouter } from 'next/navigation';
import { useSession } from '@/lib/auth-client';
import LandingPage from '@/app/LandingPage';

jest.mock('next/navigation');
jest.mock('@/lib/auth-client');

describe('LandingPage', () => {
  it('redirects authenticated users to /dashboard', async () => {
    const mockPush = jest.fn();
    (useRouter as jest.Mock).mockReturnValue({ push: mockPush });
    (useSession as jest.Mock).mockReturnValue({
      data: { user: { id: '1' } },
      isPending: false
    });

    render(<LandingPage />);

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/dashboard');
    });
  });

  it('renders landing page for unauthenticated users', () => {
    (useSession as jest.Mock).mockReturnValue({
      data: null,
      isPending: false
    });

    render(<LandingPage />);

    expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
    expect(screen.getByText(/AI-powered/i)).toBeInTheDocument();
  });

  it('renders 4 feature cards', () => {
    (useSession as jest.Mock).mockReturnValue({
      data: null,
      isPending: false
    });

    render(<LandingPage />);

    expect(screen.getByText('AI-Powered Assistant')).toBeInTheDocument();
    expect(screen.getByText('Visual Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Real-Time Updates')).toBeInTheDocument();
    expect(screen.getByText('Secure & Private')).toBeInTheDocument();
  });
});
```

#### 1.3. Write CTA Tests

**File**: `frontend/__tests__/landing-page/landing-cta.test.tsx`

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import LandingPage from '@/app/LandingPage';

jest.mock('@/lib/auth-client', () => ({
  useSession: () => ({ data: null, isPending: false })
}));

describe('Landing Page CTAs', () => {
  it('renders Get Started CTAs in 3 locations', () => {
    render(<LandingPage />);

    const ctaButtons = screen.getAllByText(/Get Started/i);
    expect(ctaButtons).toHaveLength(3); // Nav, Hero, Bottom
  });

  it('tracks CTA clicks in Google Analytics', () => {
    const mockGtag = jest.fn();
    (window as any).gtag = mockGtag;

    render(<LandingPage />);
    const heroCTA = screen.getAllByText(/Get Started/i)[1]; // Hero button

    fireEvent.click(heroCTA);

    expect(mockGtag).toHaveBeenCalledWith('event', 'cta_click', {
      event_category: 'Landing Page',
      event_label: expect.any(String),
      value: 1
    });
  });
});
```

#### 1.4. Run Tests (Expect FAILURE)

```bash
npm test -- landing-page
```

**Expected**: All tests should FAIL (RED phase) ✅

---

### Phase 2: Implement Changes (GREEN)

#### 2.1. Update LandingPage.tsx - Add Auth Redirect

**File**: `frontend/app/LandingPage.tsx`

```typescript
"use client";

import React, { useEffect } from "react";
import { useSession } from "@/lib/auth-client";
import { useRouter } from "next/navigation";
import { /* existing imports */ } from "lucide-react";
import Link from "next/link";

const LandingPage: React.FC = () => {
  const { data: session, isPending } = useSession();
  const router = useRouter();

  // Redirect authenticated users to dashboard
  useEffect(() => {
    if (session && !isPending) {
      router.push("/dashboard");
    }
  }, [session, isPending, router]);

  // Show loading or nothing while redirecting
  if (isPending) return <div className="min-h-screen bg-white" />;
  if (session) return null; // Redirecting...

  return (
    <div className="min-h-screen bg-white font-sans text-slate-900">
      {/* Rest of component */}
    </div>
  );
};

export default LandingPage;
```

#### 2.2. Update Hero Section - AI-Focused Messaging

**Find and replace in** `frontend/app/LandingPage.tsx`:

**OLD**:
```typescript
<h1 className="text-5xl sm:text-7xl font-extrabold tracking-tight text-slate-900 mb-8 leading-[1.1]">
  Organize your work, <br className="hidden sm:block" />
  <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600">
    amplify your impact.
  </span>
</h1>

<p className="text-xl text-slate-500 mb-10 leading-relaxed max-w-2xl mx-auto font-medium">
  Momentum helps you manage projects, track tasks, and reach new
  productivity peaks. Simple enough for personal use, powerful enough
  for teams.
</p>
```

**NEW**:
```typescript
<h1 className="text-5xl sm:text-7xl font-extrabold tracking-tight text-slate-900 mb-8 leading-[1.1]">
  Organize your work with <br className="hidden sm:block" />
  <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600">
    AI-powered assistance.
  </span>
</h1>

<p className="text-xl text-slate-500 mb-10 leading-relaxed max-w-2xl mx-auto font-medium">
  Let AI help you manage tasks, prioritize smartly, and reach your goals faster.
  Simple enough for personal use, powerful enough for teams.
</p>
```

#### 2.3. Update Features Section - 4 Key Features

**Find and replace** the features section (around line 424-477):

**OLD** (3 generic features):
```typescript
<div className="grid grid-cols-1 md:grid-cols-3 gap-8">
  <div className="bg-white p-8...">
    <Layers ... />
    <h3>Smart Organization</h3>
    <p>Categorize with tags...</p>
  </div>
  {/* 2 more generic features */}
</div>
```

**NEW** (4 specific features):
```typescript
import { MessageSquare, LayoutDashboard, Zap, Shield } from "lucide-react";

const FEATURES = [
  {
    id: "ai-assistant",
    icon: MessageSquare,
    iconColor: "text-indigo-600",
    iconBgColor: "bg-indigo-50",
    title: "AI-Powered Assistant",
    description: "Get intelligent suggestions, automated task organization, and natural language task creation. Your personal productivity copilot."
  },
  {
    id: "dashboard",
    icon: LayoutDashboard,
    iconColor: "text-emerald-600",
    iconBgColor: "bg-emerald-50",
    title: "Visual Dashboard",
    description: "See your productivity at a glance with beautiful charts, real-time statistics, and organized task views that keep you focused."
  },
  {
    id: "realtime",
    icon: Zap,
    iconColor: "text-amber-600",
    iconBgColor: "bg-amber-50",
    title: "Real-Time Updates",
    description: "Changes sync instantly across all your devices. Work seamlessly from desktop, mobile, or tablet without missing a beat."
  },
  {
    id: "security",
    icon: Shield,
    iconColor: "text-blue-600",
    iconBgColor: "bg-blue-50",
    title: "Secure & Private",
    description: "Your data is encrypted and secure. Industry-standard authentication keeps your tasks and projects private and protected."
  }
];

// In FeaturesSection:
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
  {FEATURES.map((feature) => {
    const Icon = feature.icon;
    return (
      <div key={feature.id} className="bg-white p-8 rounded-2xl border border-slate-100 shadow-sm hover:shadow-lg transition-all duration-300 group">
        <div className={`w-12 h-12 ${feature.iconBgColor} rounded-xl flex items-center justify-center ${feature.iconColor} mb-6 group-hover:scale-110 transition-transform`}>
          <Icon className="w-6 h-6" aria-hidden="true" />
        </div>
        <h3 className="text-xl font-bold text-slate-900 mb-3">
          {feature.title}
        </h3>
        <p className="text-slate-500 leading-relaxed">
          {feature.description}
        </p>
      </div>
    );
  })}
</div>
```

#### 2.4. Add CTA Click Tracking

**Wrap CTA Links** with click handlers:

```typescript
const handleCTAClick = (location: string) => {
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('event', 'cta_click', {
      event_category: 'Landing Page',
      event_label: location,
      value: 1
    });
  }
};

// Update each CTA:
<Link
  href="/register"
  onClick={() => handleCTAClick('hero')}
  className="..."
>
  Get Started
</Link>
```

#### 2.5. Run Tests (Expect SUCCESS)

```bash
npm test -- landing-page
```

**Expected**: All tests should PASS (GREEN phase) ✅

---

### Phase 3: Refactor & Accessibility (REFACTOR)

#### 3.1. Add Accessibility Improvements

```typescript
// Add aria-labels to icons
<Icon className="w-6 h-6" aria-hidden="true" />

// Ensure proper heading hierarchy
<h2 className="text-3xl md:text-4xl font-extrabold text-slate-900 mb-6">
  Designed for modern workflows
</h2>

// Add focus indicators (in global CSS if needed)
```

#### 3.2. Run Lighthouse Audit

```bash
npm run build
npm run start

# In Chrome DevTools:
# 1. Open Lighthouse
# 2. Run audit (Desktop + Mobile)
# 3. Check Accessibility score ≥ 90
```

#### 3.3. Test Responsive Layout

Test at these widths:
- 320px (iPhone SE)
- 375px (iPhone 12/13)
- 768px (iPad)
- 1024px (Desktop)
- 1920px (Large Desktop)

**Checklist**:
- [ ] No horizontal scrolling at 320px
- [ ] Feature cards stack properly on mobile
- [ ] Dashboard preview scales or adapts
- [ ] All CTAs remain visible and clickable

---

## Testing Guide

### Unit Tests

```bash
# Run all landing page tests
npm test -- landing-page

# Run with coverage
npm test -- landing-page --coverage
```

**Expected Coverage**:
- Statements: ≥ 80%
- Branches: ≥ 75%
- Functions: ≥ 80%
- Lines: ≥ 80%

### E2E Tests (Playwright)

```bash
# Run Playwright tests
npx playwright test landing-e2e.spec.ts

# Run with UI mode
npx playwright test --ui
```

**Example E2E Test**:

```typescript
// frontend/__tests__/landing-page/landing-e2e.spec.ts
import { test, expect } from '@playwright/test';

test('Landing page - unauthenticated user flow', async ({ page }) => {
  await page.goto('http://localhost:3000');

  // Check hero headline
  await expect(page.locator('h1')).toContainText('AI-powered assistance');

  // Check 4 features visible
  await expect(page.locator('text=AI-Powered Assistant')).toBeVisible();
  await expect(page.locator('text=Visual Dashboard')).toBeVisible();
  await expect(page.locator('text=Real-Time Updates')).toBeVisible();
  await expect(page.locator('text=Secure & Private')).toBeVisible();

  // Click primary CTA
  await page.click('text=Get Started');
  await expect(page).toHaveURL('/register');
});

test('Landing page - authenticated user redirect', async ({ page, context }) => {
  // Set auth cookie
  await context.addCookies([{
    name: 'better-auth.session_token',
    value: 'mock-session-token',
    domain: 'localhost',
    path: '/'
  }]);

  await page.goto('http://localhost:3000');

  // Should redirect to dashboard
  await expect(page).toHaveURL('/dashboard');
});
```

### Accessibility Tests

```bash
# Run Lighthouse CLI
npm install -g @lhci/cli
lhci autorun --collect.url=http://localhost:3000
```

**Manual Checks**:
1. Keyboard navigation (Tab through all CTAs)
2. Screen reader test (VoiceOver on Mac, NVDA on Windows)
3. Color contrast (WebAIM Contrast Checker)

---

## Deployment

### Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Lighthouse accessibility ≥ 90
- [ ] No console errors
- [ ] Mobile responsive verified
- [ ] Code reviewed and approved

### Build & Deploy

```bash
# Build production bundle
npm run build

# Test production build locally
npm run start

# Deploy (depends on hosting platform)
# Example for Netlify:
git push origin 012-landing-page-update
# Create PR → Merge → Auto-deploy
```

---

## Troubleshooting

### Issue: Tests failing with "useSession is not a function"

**Solution**: Mock better-auth hooks in test setup

```typescript
jest.mock('@/lib/auth-client', () => ({
  useSession: jest.fn(() => ({ data: null, isPending: false })),
  signIn: jest.fn(),
  signOut: jest.fn()
}));
```

### Issue: Lighthouse accessibility score < 90

**Common fixes**:
1. Add `aria-label` to icon-only buttons
2. Ensure heading hierarchy (h1 → h2 → h3)
3. Increase text contrast (use slate-600 instead of slate-400)
4. Add focus indicators to interactive elements

### Issue: Horizontal scroll on mobile

**Solution**: Check for fixed-width elements

```bash
# Search for fixed widths
grep -r "w-\[" frontend/app/LandingPage.tsx

# Replace with max-w-* or responsive classes
```

---

## Success Criteria Verification

| Criteria | How to Verify | Expected Result |
|----------|---------------|-----------------|
| SC-001 (AI identification) | User testing | 80% identify AI correctly |
| SC-002 (Feature recall) | User testing | 3/4 features recalled |
| SC-003 (Bounce rate < 60%) | Google Analytics | Track post-deploy |
| SC-004 (CTR increase 20%) | Google Analytics | Compare baseline |
| SC-005 (Load time < 2s) | Lighthouse | Performance score ≥ 90 |
| SC-006 (Find CTA in 5s) | User testing | 90% success rate |
| SC-007 (No scroll mobile) | Manual test | No horizontal scroll |
| SC-008 (Accessibility ≥ 90) | Lighthouse | Score ≥ 90 |

---

## Next Steps

After completing this feature:
1. Run `/sp.tasks` to generate implementation tasks
2. Execute tasks following TDD workflow (Red → Green → Refactor)
3. Create PR and request code review
4. Deploy to staging for QA testing
5. Monitor Google Analytics for success metrics

---

## References

- [Next.js 16 Documentation](https://nextjs.org/docs)
- [Better-Auth React Client](https://better-auth.com/docs/react)
- [WCAG 2.1 AA Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Lighthouse Accessibility Audit](https://developers.google.com/web/tools/lighthouse)
