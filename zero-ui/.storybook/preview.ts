import { setup, type Preview } from "@storybook/vue3-vite";
import "../src/assets/index.css";
import i18n from "../src/i18n";

// Een paar componenten (Dialog, Breadcrumb) gebruiken vertalingen via vue-i18n.
setup((app) => {
  app.use(i18n);
});

const preview: Preview = {
  parameters: {
    layout: "centered",
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
  },
  globalTypes: {
    theme: {
      description: "Light or dark theme of the app",
      toolbar: {
        title: "Theme",
        icon: "mirror",
        items: [
          { value: "light", title: "Light" },
          { value: "dark", title: "Dark" },
        ],
        dynamicTitle: true,
      },
    },
  },
  initialGlobals: { theme: "dark" },
  decorators: [
    (story, context) => {
      // The app themes through a `.dark` class on <html>, as useColorMode sets it.
      document.documentElement.classList.toggle("dark", context.globals.theme === "dark");
      document.body.classList.add("bg-background", "text-foreground");
      return story();
    },
  ],
};

export default preview;
