import { inject, provide, Ref } from "vue";

export interface ValueFormContext {
  isDirty: Ref<boolean>;
  error: Ref<string | undefined>;
  isPending: Ref<boolean>;
  isEditable: Ref<boolean>;
  hasFocus?: boolean;
  submit(): void;
  undo(): void;
}

export const provideValueForm = (form: ValueFormContext) => provide("ValueForm", form);
export const injectValueForm = <Ctx extends ValueFormContext = ValueFormContext>() =>
  inject<Ctx | undefined>("ValueForm", undefined);
export const provideHideEditorIfNotEditable = (value: boolean) =>
  provide("HideEditorIfNotEditable", value);
export const injectHideEditorIfNotEditable = () => inject<boolean>("HideEditorIfNotEditable", true);
