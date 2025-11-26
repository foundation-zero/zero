import urql from "@urql/vue";
import { createPinia } from "pinia";
import { createApp } from "vue";
import App from "./App.vue";
import "./assets/index.css";
import i18n from "./i18n";
import client from "./modules/domestic/graphql/client";
import { withGuards } from "./modules/domestic/router/guards";
import router from "./router";

const store = createPinia();

createApp(App).use(store).use(withGuards(router)).use(urql, client).use(i18n).mount("#app");
