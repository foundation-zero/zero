import urql from "@urql/vue";
import { createPinia } from "pinia";
import { createApp } from "vue";
import App from "./App.vue";
import "./assets/index.css";
import client from "./graphql/client";
import i18n from "./i18n";
import router from "./router";
import { withGuards } from "./router/guards";

const store = createPinia();

createApp(App).use(store).use(withGuards(router)).use(urql, client).use(i18n).mount("#app");
