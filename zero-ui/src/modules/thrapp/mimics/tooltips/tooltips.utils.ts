import { tScoped } from "@/modules/common/lib/utils.ts";
import { useI18n } from "vue-i18n";

export const useTranslations = () => ({
  units: tScoped("units"),
  actions: tScoped("thrapp.tooltips.actions"),
  items: tScoped("thrapp.tooltips.items"),
  labels: tScoped("thrapp.tooltips.labels"),
  sources: tScoped("thrapp.tooltips.sources"),
  t: useI18n().t,
});
