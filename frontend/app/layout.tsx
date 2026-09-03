import type { Metadata } from "next";
import { GeistSans } from "geist/font/sans";
import { GeistMono } from "geist/font/mono";
import "./globals.css";

export const metadata: Metadata = {
  title: "VentureOS -- AI-Powered Startup Strategy Room",
  description:
    "Submit your startup idea and let specialised AI agents analyse your market, product, finances, and investment potential.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${GeistSans.variable} ${GeistMono.variable}`}>
      <body className="bg-vo-black text-vo-white antialiased">{children}</body>
    </html>
  );
}
