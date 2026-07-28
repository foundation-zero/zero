import { toUpperCamelCase } from "@/modules/common/lib/utils";
import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { ThrsDefinitions } from "@/modules/thrs/lib/consts";
import { PickKeys, SchemaDefinition, SensorComponentType } from "@/modules/thrs/types";
import { kebabCase } from "lodash";
import { getSensorDefinition, isCustomField, isSensorField, ModuleField } from "../../../providers";

const THRS_YARDTAG_PREFIX_REGEX = /^5000/;

export const fieldTooltip = <
  Type extends SensorComponentType | "custom",
  Module extends keyof ThrsDefinitions = keyof {
    [M in keyof ThrsDefinitions as PickKeys<
      ThrsDefinitions[M]["sensorValues"],
      SchemaDefinition<Type>
    > extends never
      ? never
      : M]: ThrsDefinitions[M];
  },
>(
  field: ModuleField<Type, Module>,
  content: Partial<TooltipContent>,
): TooltipContent => {
  if (isCustomField(field)) {
    return {
      yardTag: field[3].yardTag,
      technicalName: field[3].technicalName,
      ...content,
      title: field[3].title ?? content.title ?? "",
    };
  } else if (isSensorField(field)) {
    const definition = getSensorDefinition(field[1], field[2]);
    return {
      title: toUpperCamelCase(field[2]),
      yardTag: definition?.yardTag?.replace(THRS_YARDTAG_PREFIX_REGEX, ""),
      technicalName: kebabCase(field[2]), // TODO: should come from api
      mqttTopic: `.../${kebabCase(field[2])}`, // TODO: should come from api
      ...content,
    };
  } else {
    return "unreachable" as never;
  }
};
