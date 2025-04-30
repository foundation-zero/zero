const animate = require("tailwindcss-animate");
const plugin = require("tailwindcss/plugin");

/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  safelist: ["dark", "grid-cols-1", "grid-cols-2", "grid-cols-3"],
  prefix: "",

  content: ["./src/**/*.{ts,tsx,vue}"],

  theme: {
    container: {
      center: true,
      padding: "2rem",
    },
    extend: {
      transformOrigin: {
        "left-right": "0% 50%",
      },
      screens: {
        "2xl": "1400px",
        tablet: "768px",
      },
      fontSize: {
        "2xs": ["0.625rem", { lineHeight: "1rem" }],
        "3xs": ["0.5rem", { lineHeight: "0.75rem" }],
        "4xs": ["0.375rem", { lineHeight: "0.625rem" }],
        "5xs": ["0.25rem", { lineHeight: "0.375rem" }],
        rxs: ["0.75em", { lineHeight: "1em" }],
        rsm: ["0.875em", { lineHeight: "1.25em" }],
        rbase: ["1em", { lineHeight: "1.5em" }],
        rlg: ["1.125em", { lineHeight: "1.75em" }],
        rxl: ["1.25em", { lineHeight: "1.75em" }],
        r4xl: ["2.25em", { lineHeight: "2.5em" }],
        r6xl: ["3.75em", { lineHeight: 1 }],
      },
      colors: {
        "background-dark": "rgba(28, 28, 30, 1.00)",
        "background-light": "rgba(242, 241, 246, 1.00)",
        "border-light": "rgba(209, 209, 211, 1.00)",
        "border-dark": "rgba(49, 49, 51, 1.00)",
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        xl: "calc(var(--radius) + 4px)",
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        progress: {
          "0%": { transform: " translateX(0) scaleX(0)" },
          "40%": { transform: "translateX(0) scaleX(0.4)" },
          "100%": { transform: "translateX(100%) scaleX(0.5)" },
        },
        "accordion-down": {
          from: { height: 0 },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: 0 },
        },
        "collapsible-down": {
          from: { height: 0 },
          to: { height: "var(--radix-collapsible-content-height)" },
        },
        "collapsible-up": {
          from: { height: "var(--radix-collapsible-content-height)" },
          to: { height: 0 },
        },
      },
      animation: {
        progress: "progress 1s infinite linear",
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        "collapsible-down": "collapsible-down 0.2s ease-in-out",
        "collapsible-up": "collapsible-up 0.2s ease-in-out",
      },
    },
  },
  plugins: [
    animate,
    plugin(function ({ addVariant }) {
      addVariant("mobile", "&.mobile-only");
      addVariant("desktop", "&.desktop-only");
    }),
  ],
};
