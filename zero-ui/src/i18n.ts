import { createI18n } from "vue-i18n";
import { fromKeys } from "./modules/common/lib/utils";

const SUPPORTED_LOCALES = ["en"] as const;
type SupportedLocale = (typeof SUPPORTED_LOCALES)[number];
type LocaleMessages = Record<string, string>;
type LocaleFiles = Record<string, LocaleMessages>;
type Locales = Record<SupportedLocale, LocaleFiles>;

// SOURCE: https://medium.com/@mbesagil/i18n-structure-combining-json-files-with-vue-js-ae35d745be2c
const imports: Locales = {
  en: import.meta.glob([`@/modules/**/i18n/en/*.json`, `@/modules/**/i18n/en.json`], {
    eager: true,
    import: "default",
  }),
};

const getLocaleMessages = (): Record<SupportedLocale, LocaleMessages> =>
  fromKeys(SUPPORTED_LOCALES, (locale) =>
    Object.values(imports[locale]).reduce((message, current) => ({ ...message, ...current }), {}),
  );

const i18n = createI18n({
  legacy: false,
  locale: "en",
  fallbackLocale: "en",
  messages: getLocaleMessages(),
});

export default i18n;
