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
