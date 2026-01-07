import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import GoogleAnalytics from "@/components/GoogleAnalytics";
import { AuthProvider } from "@/contexts/AuthContext";
import Script from "next/script";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "Momentum",
  description: "Task management dashboard",
  icons: {
    icon: '/favicon.svg',
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} antialiased font-sans`}>
        <GoogleAnalytics />
        <AuthProvider>
          {children}
        </AuthProvider>
        <Script
          src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js"
          async
        />
      </body>
    </html>
  );
}