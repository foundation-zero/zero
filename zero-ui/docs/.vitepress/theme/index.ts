import DefaultTheme from "vitepress/theme";
import "../../../src/assets/index.css";

export default {
  extends: DefaultTheme,
  enhanceApp({ app: _app }) {
    // Register global components here if needed
  },
};
