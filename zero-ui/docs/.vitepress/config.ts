import { defineConfig } from "vitepress";

export default defineConfig({
  title: "Zero UI Components",
  description: "Component library documentation for Zero UI",
  base: "/zero-ui/",

  appearance: true, // Enable dark mode toggle

  themeConfig: {
    nav: [
      { text: "Home", link: "/" },
      { text: "Components", link: "/components/" },
    ],

    sidebar: [
      {
        text: "Getting Started",
        items: [
          { text: "Introduction", link: "/" },
          { text: "Typography", link: "/typography" },
          { text: "Colors", link: "/colors" },
        ],
      },
      {
        text: "Colors",
        items: [
          { text: "Primitives", link: "/colors/primitives" },
          { text: "Semantic", link: "/colors/semantic" },
          { text: "Components", link: "/colors/components" },
        ],
      },
      {
        text: "Components",
        items: [
          { text: "Badge", link: "/components/badge" },
          { text: "Button", link: "/components/button" },
          { text: "Input", link: "/components/input" },
          { text: "Labeled Input", link: "/components/labeled-input" },
          { text: "Popover", link: "/components/popover" },
          { text: "Select", link: "/components/select" },
        ],
      },
    ],

    socialLinks: [{ icon: "github", link: "https://github.com/foundation-zero/zero" }],
  },

  vite: {
    resolve: {
      alias: {
        "@": new URL("../../src", import.meta.url).pathname,
        "@common": new URL("../../src/modules/common", import.meta.url).pathname,
      },
    },
  },
});
