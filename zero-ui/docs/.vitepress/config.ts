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
      { text: "Mimics", link: "/mimics/" },
    ],

    sidebar: [
      {
        text: "Getting Started",
        items: [
          { text: "Introduction", link: "/" },
          { text: "Figma MCP Bridge", link: "/figma-mcp-bridge" },
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
          { text: "Indicator Light", link: "/components/indicator-light" },
          { text: "Info Tooltip", link: "/components/info-tooltip" },
          { text: "Input", link: "/components/input" },
          { text: "Labeled Input", link: "/components/labeled-input" },
          { text: "Loads Card", link: "/components/loads-card" },
          { text: "Variable Card", link: "/components/variable-card" },
          { text: "Mast Lock", link: "/components/mast-lock" },
          { text: "Popover", link: "/components/popover" },
          { text: "Position Card", link: "/components/position-card" },
          { text: "Select", link: "/components/select" },
          { text: "TWA Selector", link: "/components/twa-selector" },
          { text: "TWS Selector", link: "/components/tws-selector" },
        ],
      },

      {
        text: "Mimics",
        items: [
          { text: "Overview", link: "/mimics/" },
          { text: "Authoring New Components", link: "/mimics/authoring-workflow" },
          { text: "Updating Components", link: "/mimics/updating-components" },
        ],
      },
      {
        text: "Actuated Components",
        items: [
          { text: "Actuated Valve", link: "/mimics/actuated-valve" },
          { text: "Pump", link: "/mimics/pump" },
          { text: "Heat Exchanger", link: "/mimics/heat-exchanger" },
          { text: "Pipe Heat Exchanger", link: "/mimics/pipe-heat-exchanger" },
        ],
      },
      {
        text: "Manual Components",
        items: [
          { text: "Manual Valve", link: "/mimics/manual-valve" },
          { text: "Check Valve", link: "/mimics/check-valve" },
          { text: "Pressure Gauge", link: "/mimics/pressure-gauge" },
        ],
      },
      {
        text: "Sensors",
        items: [
          { text: "Temperature Sensor", link: "/mimics/temperature-sensor" },
          { text: "Flow Sensor", link: "/mimics/flow-sensor" },
          { text: "Pressure Sensor", link: "/mimics/pressure-sensor" },
          { text: "Level Sensor", link: "/mimics/level-sensor" },
        ],
      },
      {
        text: "Modules",
        items: [
          { text: "Overview", link: "/mimics/modules/" },
          { text: "Dhw Module", link: "/mimics/modules/dhw-module" },
        ],
      },
    ],

    socialLinks: [{ icon: "github", link: "https://github.com/foundation-zero/zero" }],
  },

  vite: {
    resolve: {
      alias: {
        "@": new URL("../../src", import.meta.url).pathname,
        "@env": new URL("../../src/settings", import.meta.url).pathname,
        "@common": new URL("../../src/modules/common", import.meta.url).pathname,
      },
    },
    define: {
      __VUE_PROD_DEVTOOLS__: "false",
    },
    ssr: {
      noExternal: ["vue-i18n", "lodash"],
    },
  },
});
