import urql from "@urql/vue";
import { createPinia } from "pinia";
import { createApp } from "vue";
import App from "./App.vue";
import "./assets/index.css";
import client from "./graphql/client";
import i18n from "./i18n";
import router from "./router";

const store = createPinia();

createApp(App).use(store).use(router).use(urql, client).use(i18n).mount("#app");
