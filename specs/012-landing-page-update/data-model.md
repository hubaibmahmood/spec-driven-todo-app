# Data Model: Landing Page Component Structure

**Feature**: 012-landing-page-update
**Date**: 2025-12-29
**Type**: UI Component Architecture

## Overview

This document defines the component structure, props, state, and composition for the updated landing page. Since this is a frontend-only feature with no database entities, the "data model" describes the React component hierarchy and data flow.

## Component Hierarchy

```
HomePage (page.tsx)
  └── LandingPage (LandingPage.tsx) ← PRIMARY UPDATE
       ├── NavigationBar
       │    ├── Logo
       │    ├── LoginLink
       │    └── GetStartedButton (CTA #1)
       │
       ├── HeroSection
       │    ├── Badge (Version indicator)
       │    ├── Headline (AI-focused value prop)
       │    ├── Subheadline
       │    ├── CTAButtonPrimary (CTA #2)
       │    └── CTAButtonSecondary
       │
       ├── DashboardPreview
       │    ├── WindowControls
       │    ├── Sidebar (mockup)
       │    ├── Header (mockup)
       │    └── MainContent (mockup)
       │         ├── StatsGrid (4 cards)
       │         ├── FilterBar
       │         └── TaskList (3 items)
       │
       ├── FeaturesSection ← MAJOR UPDATE
       │    ├── SectionHeader
       │    └── FeatureGrid
       │         ├── FeatureCard (AI-Powered Assistant) ← NEW
       │         ├── FeatureCard (Visual Dashboard) ← NEW
       │         ├── FeatureCard (Real-Time Updates) ← NEW
       │         └── FeatureCard (Secure & Private) ← NEW
       │
       ├── BottomCTA
       │    └── GetStartedButton (CTA #3)
       │
       └── Footer
            ├── Logo
            └── FooterLinks
```

## Component Specifications

### 1. LandingPage (Root Component)

**File**: `frontend/app/LandingPage.tsx`

**Purpose**: Main landing page component with authentication detection and redirect logic

**Props**: None (top-level component)

**State**:
```typescript
interface LandingPageState {
  // Auth state (from better-auth useSession hook)
  session: Session | null;
  isPending: boolean;
}
```

**Hooks**:
```typescript
import { useSession } from "@/lib/auth-client";
import { useRouter } from "next/navigation";

const { data: session, isPending } = useSession();
const router = useRouter();
```

**Behavior**:
- On mount: Check session status
- If authenticated: Redirect to /dashboard (useEffect)
- If pending: Show loading spinner or skeleton
- If unauthenticated: Render full landing page

**TypeScript Interface**:
```typescript
interface LandingPageProps {}

const LandingPage: React.FC<LandingPageProps> = () => {
  const { data: session, isPending } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (session && !isPending) {
      router.push("/dashboard");
    }
  }, [session, isPending, router]);

  if (isPending) return <LoadingSpinner />;
  if (session) return null; // Redirecting

  return (
    <div className="min-h-screen bg-white">
      {/* Component sections */}
    </div>
  );
};
```

---

### 2. HeroSection (Inline Component)

**Purpose**: Above-the-fold hero section with AI-focused value proposition

**Content Structure**:
```typescript
interface HeroContent {
  badge: {
    text: string;        // "New V2.0 Available"
    animated: boolean;   // Pulse animation
  };
  headline: {
    text: string;        // "Organize your work with AI-powered assistance"
    highlightText: string; // "AI-powered assistance" (gradient)
  };
  subheadline: string;   // Value proposition description
  ctaPrimary: CTAButton;
  ctaSecondary: CTAButton;
}
```

**Required Updates**:
- **Headline**: Update from "Organize your work, amplify your impact" to emphasize AI
  - New: "Organize your work with **AI-powered assistance**"
  - Gradient on "AI-powered assistance"
- **Subheadline**: Update from generic productivity to AI benefits
  - New: "Let AI help you manage tasks, prioritize smartly, and reach your goals faster. Simple enough for personal use, powerful enough for teams."

---

### 3. FeaturesSection (NEW Component)

**Purpose**: Showcase 4 key features with benefit-focused descriptions

**Props**:
```typescript
interface FeaturesSectionProps {
  features: Feature[];
}

interface Feature {
  id: string;              // "ai-assistant", "dashboard", "realtime", "security"
  icon: LucideIcon;        // MessageSquare, LayoutDashboard, Zap, Shield
  iconColor: string;       // Tailwind color class
  iconBgColor: string;     // Tailwind bg color class
  title: string;           // "AI-Powered Assistant"
  description: string;     // Benefit-focused description (FR-007)
}
```

**Features Data** (from spec FR-002):
```typescript
const FEATURES: Feature[] = [
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
```

**FeatureCard Component**:
```typescript
interface FeatureCardProps {
  feature: Feature;
}

const FeatureCard: React.FC<FeatureCardProps> = ({ feature }) => {
  const Icon = feature.icon;

  return (
    <div className="bg-white p-8 rounded-2xl border border-slate-100 shadow-sm hover:shadow-lg transition-all duration-300 group">
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
};
```

---

### 4. CTAButton (Reusable Component)

**Purpose**: Call-to-action button with consistent styling and analytics tracking

**Props**:
```typescript
interface CTAButtonProps {
  href: string;           // "/register" or "/login"
  variant: "primary" | "secondary";
  location: "nav" | "hero" | "bottom"; // For analytics tracking
  children: React.ReactNode;
  className?: string;     // Additional Tailwind classes
}
```

**Implementation**:
```typescript
const CTAButton: React.FC<CTAButtonProps> = ({
  href,
  variant,
  location,
  children,
  className = ""
}) => {
  const handleClick = () => {
    // Track CTA click in Google Analytics (FR-014)
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', 'cta_click', {
        event_category: 'Landing Page',
        event_label: location,
        value: 1
      });
    }
  };

  const baseStyles = variant === "primary"
    ? "bg-indigo-600 hover:bg-indigo-700 text-white shadow-xl shadow-indigo-500/30 hover:shadow-2xl"
    : "bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 hover:border-slate-300 shadow-sm";

  return (
    <Link
      href={href}
      onClick={handleClick}
      className={`px-8 py-4 font-bold rounded-2xl text-lg transition-all hover:-translate-y-1 flex items-center justify-center gap-2 ${baseStyles} ${className}`}
    >
      {children}
    </Link>
  );
};
```

---

### 5. DashboardPreview (Existing Component)

**Purpose**: Visual mockup of actual dashboard interface

**Props**: None (static mockup)

**Structure**: (No changes needed - current inline mockup is excellent)
- Window controls (Mac-style red/yellow/green dots)
- Sidebar navigation
- Header with notifications
- Main content area:
  - Greeting + New Task button
  - 4 stat cards (Total, Pending, High Priority, Completion %)
  - Filter tabs + search bar
  - Task list (3 items: 2 active, 1 completed)

**Accessibility Updates Needed**:
- Add `aria-label` to interactive mockup elements
- Add `role="img"` and `aria-label="Dashboard Preview"` to container
- Ensure sufficient color contrast in stat cards

---

## Component Props Summary Table

| Component | Props | State | Purpose |
|-----------|-------|-------|---------|
| `LandingPage` | None | `session`, `isPending` | Root component with auth redirect |
| `HeroSection` | Inline (no props) | None | Hero section with headline + CTAs |
| `FeaturesSection` | `features: Feature[]` | None | Feature grid container |
| `FeatureCard` | `feature: Feature` | None | Individual feature card |
| `CTAButton` | `href`, `variant`, `location`, `children` | None | Reusable CTA with tracking |
| `DashboardPreview` | None | None | Static mockup visualization |

---

## State Management

**No global state needed** - This is a static landing page with local component state only.

**Better-Auth Session State**:
```typescript
// Managed by better-auth React client
import { useSession } from "@/lib/auth-client";

const { data: session, isPending } = useSession();
// session: Session | null
// isPending: boolean (loading state)
```

---

## TypeScript Definitions

**Create new file**: `frontend/types/landing.ts`

```typescript
import { LucideIcon } from "lucide-react";

export interface Feature {
  id: string;
  icon: LucideIcon;
  iconColor: string;
  iconBgColor: string;
  title: string;
  description: string;
}

export interface CTAButtonProps {
  href: string;
  variant: "primary" | "secondary";
  location: "nav" | "hero" | "bottom";
  children: React.ReactNode;
  className?: string;
}

export interface FeatureCardProps {
  feature: Feature;
}

export interface FeaturesSectionProps {
  features: Feature[];
}

// Google Analytics types
declare global {
  interface Window {
    gtag?: (
      command: 'event',
      eventName: string,
      eventParams: {
        event_category: string;
        event_label: string;
        value: number;
      }
    ) => void;
  }
}
```

---

## Validation Rules

Since this is a presentational component (no forms), validation focuses on:

1. **Content Validation**:
   - All CTAs must have `href` attribute
   - All feature descriptions ≤200 characters (readability)
   - Heading hierarchy maintained (h1 → h2 → h3)

2. **Accessibility Validation**:
   - All icons have `aria-hidden="true"` or `aria-label`
   - Color contrast ≥4.5:1 for body text
   - Interactive elements keyboard accessible
   - Focus indicators visible

3. **Responsive Validation**:
   - No horizontal scrolling at 320px width
   - Feature cards stack vertically on mobile (1 column)
   - Dashboard preview scales or hides appropriately

---

## Integration Points

| Integration | Method | Purpose |
|-------------|--------|---------|
| **better-auth** | `useSession()` hook | Detect authenticated users |
| **Next.js Router** | `useRouter()` hook | Client-side redirect to /dashboard |
| **Google Analytics** | `window.gtag()` (optional) | Track CTA clicks (FR-014) |
| **Tailwind CSS** | Utility classes | Styling and responsive design |
| **Lucide React** | Icon components | Feature card icons |

---

## Next Steps

1. Generate API contracts in `contracts/` directory
2. Create quickstart.md with development setup
3. Update agent context with component patterns
