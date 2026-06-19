import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/toaster";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AICL Web Editor",
  description: "Artificial Intelligence-Centered Language (AICL) Web Editor — Write, compile, verify, and audit AICL specifications. AX sub-language, 4 compile targets (Python/Rust/JS/Go), Proof of Origin.",
  keywords: ["AICL", "Artificial Intelligence-Centered Language", "AX", "Code Editor", "Compiler", "Proof of Origin", "CogNet"],
  authors: [{ name: "AICL Team" }],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-background text-foreground`}
      >
        {children}
        <Toaster />
      </body>
    </html>
  );
}
