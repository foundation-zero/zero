import { defineConfig } from "vitepress";

export default defineConfig({
  title: "Zero UI Components",
  description: "Component library documentation for Zero UI",
  base: "/zero-ui/",

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
          { text: "Installation", link: "/installation" },
        ],
      },
      {
        text: "Components",
        items: [
          { text: "Badge", link: "/components/badge" },
          { text: "Button", link: "/components/button" },
          { text: "Input", link: "/components/input" },
        ],
      },
    ],

    socialLinks: [{ icon: "github", link: "https://github.com/foundation-zero/zero" }],
  },

  vite: {
    resolve: {
      alias: {
        "@": new URL("../../src", import.meta.url).pathname,
      },
    },
  },
});
