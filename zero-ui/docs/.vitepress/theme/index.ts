import type { Theme } from "vitepress";
import type { App } from "vue";

// Import our custom layout and styles
import "../../../src/assets/index.css";
import { Badge } from "../../../src/components/ui/shadcn/badge";
import { Input } from "../../../src/components/ui/shadcn/input";
import Layout from "./Layout.vue";

// Import VitePress styles wrapped in CSS layers
import "./styles/vitepress-layered.css";

const theme: Theme = {
  Layout,
  enhanceApp({ app }: { app: App }) {
    // Register our UI components globally
    app.component("Badge", Badge);
    app.component("Input", Input);
  },
};

export default theme;
