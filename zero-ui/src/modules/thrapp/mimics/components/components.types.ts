import { Ratio } from "@/modules/thrapp/types/thrs";
import { Ref } from "vue";
import { ComponentOrientation, MimicComponentState } from "./components.consts";

export interface MimicComponentBaseProps {
  orientation?: ComponentOrientation;
  rotation?: Ratio;
  state?: MimicComponentState;
}

export interface MimicComponentProps {
  baseOrientation?: ComponentOrientation;
  id?: string;
  width: number;
  height: number;
}

export interface MimicComponentContext {
  stateColor: Ref<string>;
  state: Ref<MimicComponentState | undefined>;
  strokeWidth: Ref<number>;
  rotationDegrees: Ref<number>;
}
