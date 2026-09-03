import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Primary background
        "vo-black": "#050505",
        "vo-dark": "#0D0D0D",
        // Primary red
        "vo-red": "#E10600",
        "vo-red-hover": "#FF1A14",
        // Text
        "vo-white": "#F5F5F5",
        "vo-muted": "#A1A1A1",
        // Borders
        "vo-border": "#262626",
        "vo-border-hover": "#404040",
      },
      fontFamily: {
        sans: ["var(--font-geist-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-geist-mono)", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
