import { TooltipComponentContext } from "@/modules/heat-system/components/tooltip";
import { MimicComponentType } from "@/modules/heat-system/types";

export type MimicComponentFieldsMap = {
  [Type in MimicComponentType]: Record<string, TooltipComponentContext<Type>>;
};

export const toFieldsMap = <FieldMap extends Partial<MimicComponentFieldsMap>>(
  fieldMap: FieldMap,
): FieldMap => fieldMap;

export const toInstance = <Type extends MimicComponentType>(data: TooltipComponentContext<Type>) =>
  data;
