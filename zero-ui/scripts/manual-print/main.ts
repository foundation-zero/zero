import "@/assets/index.css";
import { checkManual, ManualDocument } from "@/modules/thrapp/components/manual";
import fragment from "virtual:manual-fragment";
import { createApp, h } from "vue";
import "./print.css";

// render-manual names the module, from the fragment's file name, for checkManual.
const module = new URLSearchParams(location.search).get("module") ?? "";

const markRendered = async () => {
  const problems = await checkManual(fragment, module);
  await document.fonts.ready;
  document.body.dataset.problems = JSON.stringify(problems);
  document.body.dataset.rendered = "true";
};

createApp({
  render: () => h(ManualDocument, { html: fragment, printed: true, onRendered: markRendered }),
}).mount("#app");
