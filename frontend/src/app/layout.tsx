import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "3-Day Swift & SwiftUI Masterclass",
  description: "Exclusive event for AIML students at Parul University.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} dark antialiased h-full`}
    >
      <body className="min-h-full flex flex-col bg-black text-[#f5f5f7] selection:bg-[#FF5257] selection:text-white font-sans" style={{ fontFamily: "var(--font-inter), sans-serif" }}>
        {children}
      </body>
    </html>
  );
}
