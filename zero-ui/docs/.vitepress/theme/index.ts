import DefaultTheme from "vitepress/theme";
import type { App } from "vue";
import "../../../src/assets/index.css";
import { Badge } from "../../../src/components/ui/shadcn/badge";

export default {
  extends: DefaultTheme,
  enhanceApp({ app }: { app: App }) {
    // Register components globally for use in documentation examples
    app.component("Badge", Badge);
    // Temporarily disable Button component due to SSR issues
    // app.component("UIButton", Button);
  },
};
