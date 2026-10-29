import { Blind } from "@/modules/domestic/types";
import { inject, Ref } from "vue";
import { BlindsControlContext } from "./blinds-slider.types";

export const getContext = (): BlindsControlContext => {
  const value = inject("value") as Ref<number>;
  const commit = inject("commit") as () => void;
  const disabled = inject("disabled") as Ref<boolean>;
  const editable = inject("editable") as Ref<boolean>;
  const control = inject("control") as Ref<Blind>;

  if (!value || !commit || !disabled || !editable || !control) {
    throw new Error("BlindsControl components must be used within a BlindsControlProvider");
  }

  return { value, commit, disabled, editable, control };
};
