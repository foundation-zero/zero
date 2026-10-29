import { inject, provide } from "vue";

export const provideMultiLineEditor = (value: boolean) => provide("multiLineEditor", value);
export const injectMultiLineEditor = () => inject<boolean>("multiLineEditor", false);
