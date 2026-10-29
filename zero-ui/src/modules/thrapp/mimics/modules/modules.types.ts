import { TooltipComponentContext } from "@/modules/thrapp/components/tooltip";
import { MimicComponentType } from "@/modules/thrapp/types";

export type MimicComponentFieldsMap = {
  [Type in MimicComponentType]: Record<string, TooltipComponentContext<Type>>;
};
