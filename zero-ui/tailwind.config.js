const animate = require("tailwindcss-animate");

/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  prefix: "",
  content: ["./src/**/*.{ts,tsx,vue}"],

  plugins: [animate],
};
