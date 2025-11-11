// app/layout.tsx


import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/toaster";  // Add this

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "VexaAI Data Analyst Pro",
  description: "AI-powered data analytics platform for business insights",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        {children}
        <Toaster />  {/* Add this */}
      </body>
    </html>
  );
}