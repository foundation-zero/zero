import type { Theme } from "vitepress";
import type { App } from "vue";

// Import our custom layout and styles
import "../../../src/assets/index.css";
import { Badge } from "../../../src/components/ui/badge";
import { Button } from "../../../src/components/ui/button";
import { Input } from "../../../src/components/ui/input";
import {
  MultiSelectTrigger,
  MultiSelectValue,
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectItemText,
  SelectLabel,
  SelectScrollDownButton,
  SelectScrollUpButton,
  SelectSeparator,
  SelectTrigger,
  SelectValue,
} from "../../../src/components/ui/select";
import Layout from "./Layout.vue";

// Import VitePress styles wrapped in CSS layers
import "./styles/vitepress-layered.css";

import i18n from "../../../src/i18n";

const theme: Theme = {
  Layout,
  enhanceApp({ app }: { app: App }) {
    // Install i18n
    app.use(i18n);

    // Register our UI components globally
    app.component("Badge", Badge);
    app.component("Button", Button);
    app.component("Input", Input);

    // Register Select components
    app.component("Select", Select);
    app.component("SelectContent", SelectContent);
    app.component("SelectGroup", SelectGroup);
    app.component("SelectItem", SelectItem);
    app.component("SelectItemText", SelectItemText);
    app.component("SelectLabel", SelectLabel);
    app.component("SelectScrollDownButton", SelectScrollDownButton);
    app.component("SelectScrollUpButton", SelectScrollUpButton);
    app.component("SelectSeparator", SelectSeparator);
    app.component("SelectTrigger", SelectTrigger);
    app.component("SelectValue", SelectValue);
    app.component("MultiSelectTrigger", MultiSelectTrigger);
    app.component("MultiSelectValue", MultiSelectValue);
  },
};

export default theme;
