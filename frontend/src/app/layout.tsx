import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import SupportButton from "@/components/support-button";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter"
});

export const metadata: Metadata = {
  title: "TechCorp - AI-Powered Customer Success",
  description: "Transform your customer support with intelligent automation. 24/7 support, instant responses, and 98% cost savings.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans antialiased`}>
        {children}
        <SupportButton />
      </body>
    </html>
  );
}
