import { TooltipComponentContext } from "@/modules/thrapp/components/tooltip";
import { MimicComponentType } from "@/modules/thrapp/types";
import { MimicComponentFieldsMap } from "./modules.types";

export const toFieldsMap = <FieldMap extends Partial<MimicComponentFieldsMap>>(
  fieldMap: FieldMap,
): FieldMap => fieldMap;

export const toInstance = <Type extends MimicComponentType>(data: TooltipComponentContext<Type>) =>
  data;
