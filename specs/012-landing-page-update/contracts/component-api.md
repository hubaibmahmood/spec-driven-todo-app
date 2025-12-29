# Component API Contracts

**Feature**: 012-landing-page-update
**Date**: 2025-12-29
**Version**: 1.0.0

## Overview

This document defines the API contracts for all components in the updated landing page. These contracts serve as the interface specification between components and are used to validate implementation during testing.

---

## 1. LandingPage Component

**File**: `frontend/app/LandingPage.tsx`

### Contract

```typescript
interface LandingPageProps {}

const LandingPage: React.FC<LandingPageProps> = () => {
  // Implementation
};

export default LandingPage;
```

### Behavior Contract

**Authentication Detection**:
- MUST use `useSession` hook from `@/lib/auth-client`
- MUST redirect authenticated users to `/dashboard`
- MUST NOT render landing content if user is authenticated
- MUST show loading state while session check is pending

**Rendering Contract**:
- IF `isPending === true`: MUST render loading spinner or return null
- IF `session !== null`: MUST redirect to `/dashboard` and return null
- IF `session === null && !isPending`: MUST render full landing page

**Testing Contract**:
```typescript
describe("LandingPage", () => {
  it("redirects authenticated users to /dashboard", () => {
    // Mock useSession to return { data: mockSession, isPending: false }
    // Expect router.push("/dashboard") to be called
  });

  it("shows loading state while session is pending", () => {
    // Mock useSession to return { data: null, isPending: true }
    // Expect loading indicator or null render
  });

  it("renders landing page for unauthenticated users", () => {
    // Mock useSession to return { data: null, isPending: false }
    // Expect full landing page to render
  });
});
```

---

## 2. Feature Interface

**File**: `frontend/types/landing.ts`

### Contract

```typescript
import { LucideIcon } from "lucide-react";

export interface Feature {
  id: string;              // Unique identifier (kebab-case)
  icon: LucideIcon;        // Lucide icon component
  iconColor: string;       // Tailwind text color class (e.g., "text-indigo-600")
  iconBgColor: string;     // Tailwind bg color class (e.g., "bg-indigo-50")
  title: string;           // Feature title (max 50 chars)
  description: string;     // Benefit-focused description (max 200 chars)
}
```

### Validation Rules

- `id`: MUST be unique across all features, lowercase kebab-case
- `title`: MUST be 3-50 characters
- `description`: MUST be 10-200 characters, benefit-focused (no technical jargon)
- `iconColor`: MUST be valid Tailwind text-* class
- `iconBgColor`: MUST be valid Tailwind bg-* class, lighter shade than iconColor

### Example Data

```typescript
const AI_ASSISTANT_FEATURE: Feature = {
  id: "ai-assistant",
  icon: MessageSquare,
  iconColor: "text-indigo-600",
  iconBgColor: "bg-indigo-50",
  title: "AI-Powered Assistant",
  description: "Get intelligent suggestions, automated task organization, and natural language task creation. Your personal productivity copilot."
};
```

---

## 3. FeatureCard Component

**File**: `frontend/app/LandingPage.tsx` (inline component)

### Contract

```typescript
interface FeatureCardProps {
  feature: Feature;
}

const FeatureCard: React.FC<FeatureCardProps> = ({ feature }) => {
  // Implementation
};
```

### Rendering Contract

**MUST render**:
1. Icon container with hover scale animation
2. Feature title (h3 element)
3. Feature description (p element)
4. Proper ARIA attributes for accessibility

**CSS Classes**:
- Container: `bg-white p-8 rounded-2xl border border-slate-100 shadow-sm hover:shadow-lg transition-all group`
- Icon wrapper: `w-12 h-12 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform`
- Title: `text-xl font-bold text-slate-900 mb-3`
- Description: `text-slate-500 leading-relaxed`

### Accessibility Contract

- Icon MUST have `aria-hidden="true"` (decorative)
- Title MUST be h3 element (semantic heading)
- Description MUST be readable by screen readers (no aria-hidden)

### Testing Contract

```typescript
describe("FeatureCard", () => {
  it("renders feature title and description", () => {
    // Render with mock feature data
    // Expect title and description to be visible
  });

  it("renders icon with correct styling", () => {
    // Render with mock feature
    // Expect icon container to have iconBgColor and iconColor classes
  });

  it("applies hover animation classes", () => {
    // Render and hover over card
    // Expect scale-110 transition on icon
  });

  it("is accessible to screen readers", () => {
    // Run accessibility audit
    // Expect no violations for heading hierarchy and text content
  });
});
```

---

## 4. CTAButton Component

**File**: `frontend/app/LandingPage.tsx` (inline component) or `frontend/components/CTAButton.tsx` (if extracted)

### Contract

```typescript
interface CTAButtonProps {
  href: string;                    // Destination URL
  variant: "primary" | "secondary"; // Visual style variant
  location: "nav" | "hero" | "bottom"; // Analytics tracking location
  children: React.ReactNode;       // Button text/content
  className?: string;              // Additional Tailwind classes (optional)
}

const CTAButton: React.FC<CTAButtonProps> = (props) => {
  // Implementation
};
```

### Behavior Contract

**Click Handling**:
- MUST track click event in Google Analytics if `window.gtag` is available
- MUST navigate to `href` using Next.js `Link` component
- MUST NOT break if `gtag` is undefined (graceful degradation)

**Styling Contract**:
- Primary variant: `bg-indigo-600 hover:bg-indigo-700 text-white shadow-xl`
- Secondary variant: `bg-white hover:bg-slate-50 text-slate-700 border border-slate-200`
- All variants: MUST have hover translate-y animation (`hover:-translate-y-1`)

### Analytics Event Contract

```typescript
// When clicked, MUST fire this event (if gtag exists):
window.gtag('event', 'cta_click', {
  event_category: 'Landing Page',
  event_label: location,  // "nav" | "hero" | "bottom"
  value: 1
});
```

### Testing Contract

```typescript
describe("CTAButton", () => {
  it("navigates to correct href on click", () => {
    // Render with href="/register"
    // Click button
    // Expect navigation to /register
  });

  it("tracks CTA click in Google Analytics", () => {
    // Mock window.gtag
    // Render with location="hero"
    // Click button
    // Expect gtag called with correct parameters
  });

  it("gracefully handles missing gtag", () => {
    // Delete window.gtag
    // Render and click button
    // Expect no errors thrown
  });

  it("applies correct styling for primary variant", () => {
    // Render with variant="primary"
    // Expect indigo-600 background class
  });

  it("applies correct styling for secondary variant", () => {
    // Render with variant="secondary"
    // Expect white background and border classes
  });
});
```

---

## 5. HeroSection (Inline Component)

**File**: `frontend/app/LandingPage.tsx`

### Content Contract

```typescript
interface HeroSectionContent {
  badge: {
    text: string;        // "New V2.0 Available"
    animated: boolean;   // true (pulse animation)
  };
  headline: {
    main: string;        // "Organize your work with"
    highlight: string;   // "AI-powered assistance"
  };
  subheadline: string;   // Value proposition (max 200 chars)
  ctaPrimary: string;    // "Get Started"
  ctaSecondary: string;  // "Sign in"
}
```

### Rendering Contract

**MUST include**:
1. Badge with pulse animation indicator
2. h1 element with main headline (SEO critical)
3. Gradient text on AI-focused portion
4. Subheadline paragraph
5. Two CTA buttons (primary and secondary)

**Accessibility**:
- h1 MUST be the first heading on page
- Badge animation MUST respect `prefers-reduced-motion`
- CTA buttons MUST be keyboard accessible (Tab + Enter)

### Testing Contract

```typescript
describe("HeroSection", () => {
  it("renders h1 with AI-focused headline", () => {
    // Expect h1 to contain "AI-powered assistance"
  });

  it("renders primary and secondary CTAs", () => {
    // Expect "Get Started" and "Sign in" buttons
  });

  it("respects prefers-reduced-motion for badge animation", () => {
    // Set prefers-reduced-motion: reduce
    // Expect no pulse animation
  });
});
```

---

## 6. FeaturesSection Component

**File**: `frontend/app/LandingPage.tsx` (inline component)

### Contract

```typescript
interface FeaturesSectionProps {
  features?: Feature[];  // Optional, defaults to FEATURES constant
}

const FeaturesSection: React.FC<FeaturesSectionProps> = ({ features = FEATURES }) => {
  // Implementation
};
```

### Rendering Contract

**MUST render**:
1. Section header (h2) with feature section title
2. Grid layout with responsive columns:
   - Mobile (< 768px): 1 column
   - Tablet/Desktop (≥ 768px): 3 columns
3. Exactly 4 FeatureCard components

**Feature Order** (as per spec FR-002):
1. AI-Powered Assistant (FIRST - priority feature)
2. Visual Dashboard
3. Real-Time Updates
4. Secure & Private

### Accessibility Contract

- Section MUST have semantic `<section>` tag
- h2 MUST be present for section title
- Grid layout MUST not break at 320px width
- All FeatureCards MUST be keyboard navigable

### Testing Contract

```typescript
describe("FeaturesSection", () => {
  it("renders exactly 4 feature cards", () => {
    // Render FeaturesSection
    // Expect 4 FeatureCard components
  });

  it("renders features in correct order", () => {
    // Expect first card to be "AI-Powered Assistant"
  });

  it("uses responsive grid layout", () => {
    // Render at 320px width: expect 1 column
    // Render at 768px width: expect 3 columns
  });

  it("is accessible with proper heading hierarchy", () => {
    // Expect h2 section title
    // Expect h3 for each feature card title
  });
});
```

---

## 7. FEATURES Data Constant

**File**: `frontend/app/LandingPage.tsx` or `frontend/constants/features.ts`

### Contract

```typescript
const FEATURES: readonly Feature[] = [
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
] as const;
```

### Validation

- MUST be readonly array (immutable)
- MUST contain exactly 4 features
- MUST follow Feature interface contract
- AI-Powered Assistant MUST be first in array

---

## Testing Summary

### Unit Tests Required

- [ ] LandingPage authentication redirect logic
- [ ] LandingPage loading state handling
- [ ] FeatureCard rendering with mock data
- [ ] FeatureCard accessibility compliance
- [ ] CTAButton click tracking
- [ ] CTAButton navigation
- [ ] FeaturesSection grid layout responsive behavior
- [ ] HeroSection content rendering

### Integration Tests Required

- [ ] End-to-end landing page render (unauthenticated user)
- [ ] Authenticated user redirect to /dashboard
- [ ] All 3 CTA buttons navigate correctly
- [ ] Mobile responsive layout (320px width)
- [ ] Keyboard navigation through all interactive elements

### Accessibility Tests Required

- [ ] Lighthouse accessibility score ≥ 90
- [ ] Screen reader navigation test
- [ ] Color contrast validation (all text ≥ 4.5:1)
- [ ] Keyboard-only navigation test

---

## Acceptance Criteria Mapping

| Requirement | Contract | Test Type |
|-------------|----------|-----------|
| FR-001 (AI headline) | HeroSection content contract | Unit |
| FR-002 (4 features) | FEATURES constant contract | Unit + Integration |
| FR-007 (Benefit focus) | Feature.description validation | Unit |
| FR-011 (Auth redirect) | LandingPage behavior contract | Integration |
| FR-013 (SSR) | Next.js rendering (auto) | E2E |
| FR-014 (Analytics) | CTAButton click tracking | Unit |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-29 | Initial component API contracts |
