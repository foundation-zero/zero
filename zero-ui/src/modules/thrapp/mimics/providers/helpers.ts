import { unstamp } from "@/modules/common/lib/utils";
import { Unstamp } from "@/modules/common/types";

export const extractFieldValue =
  <Key extends string>(key: Key) =>
  <V>(obj?: { [P in Key]: V }): Unstamp<V> | undefined =>
    obj?.[key] == undefined ? undefined : (unstamp(obj[key]) as Unstamp<V>);
