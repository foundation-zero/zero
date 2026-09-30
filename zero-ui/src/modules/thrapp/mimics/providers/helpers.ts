import { unstamp } from "@/modules/common/lib/utils";
import { Unstamp } from "@/modules/common/types";
import { SensorAlarms } from "@/modules/thrsim/types";
import { MimicComponentState } from "../components";

export const extractFieldValue =
  <Key extends string>(key: Key) =>
  <V>(obj?: { [P in Key]: V }): Unstamp<V> | undefined =>
    obj?.[key] == undefined ? undefined : (unstamp(obj[key]) as Unstamp<V>);

export const componentStateFromAlarms = (
  state: MimicComponentState,
  sensor?: SensorAlarms,
): MimicComponentState => {
  if (
    sensor &&
    (sensor.anyFailureActive.value ||
      sensor.anyWarningActive.value ||
      sensor.externalOutOfRange.value ||
      sensor.feedbackFailure.value)
  )
    return MimicComponentState.Alarm;

  return state;
};
