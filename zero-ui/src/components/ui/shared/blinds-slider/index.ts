import { BlindsControl } from "@/@types";
import { inject, Ref } from "vue";

export { default as BlindsSlider } from "./BlindsSlider.vue";

export type BlindsControlContext = {
  value: Ref<number>;
  commit: () => void;
  disabled: Ref<boolean>;
  editable: Ref<boolean>;
  control: Ref<BlindsControl>;
};

export const getContext = (): BlindsControlContext => {
  const value = inject("value") as Ref<number>;
  const commit = inject("commit") as () => void;
  const disabled = inject("disabled") as Ref<boolean>;
  const editable = inject("editable") as Ref<boolean>;
  const control = inject("control") as Ref<BlindsControl>;

  if (!value || !commit || !disabled || !editable || !control) {
    throw new Error("BlindsControl components must be used within a BlindsControlProvider");
  }

  return { value, commit, disabled, editable, control };
};
