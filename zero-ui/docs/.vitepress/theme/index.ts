import type { Theme } from "vitepress";
import type { App } from "vue";

// Import our custom layout and styles
import "../../../src/assets/index.css";
import { Badge } from "../../../src/components/ui/shadcn/badge";
import { Button } from "../../../src/components/ui/shadcn/button";
import { Input } from "../../../src/components/ui/shadcn/input";
import {
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
} from "../../../src/components/ui/shadcn/select";
import Layout from "./Layout.vue";

// Import VitePress styles wrapped in CSS layers
import "./styles/vitepress-layered.css";

const theme: Theme = {
  Layout,
  enhanceApp({ app }: { app: App }) {
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
  },
};

export default theme;
