import { Blind } from "@/modules/domestic/types";
import { Ref } from "vue";

export type BlindsControlContext = {
  value: Ref<number>;
  commit: () => void;
  disabled: Ref<boolean>;
  editable: Ref<boolean>;
  control: Ref<Blind>;
};
