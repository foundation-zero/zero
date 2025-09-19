const animate = require("tailwindcss-animate");

/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  prefix: "",
  content: [
    "./src/**/*.{ts,tsx,vue}",
    "./docs/**/*.{md,vue,ts,js}",
    "./docs/.vitepress/**/*.{vue,ts,js}",
  ],

  plugins: [animate],
};
