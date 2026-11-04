import "@/assets/index.css";
import { ManualDocument } from "@/modules/thrapp/components/manual";
import fragment from "virtual:manual-fragment";
import { createApp, h } from "vue";
import "./print.css";

const markRendered = async () => {
  await document.fonts.ready;
  document.body.dataset.rendered = "true";
};

createApp({
  render: () => h(ManualDocument, { html: fragment, onRendered: markRendered }),
}).mount("#app");
