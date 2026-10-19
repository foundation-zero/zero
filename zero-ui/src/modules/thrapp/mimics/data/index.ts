import { TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { ModuleField } from "../providers";
import tooltips from "./tooltips.json";

export const toContext = <P, T extends Partial<Record<MimicComponentType, P>>>(input: T): T => {
  return input;
};

export const tooltipContexts = toContext(tooltips.contexts);

export type TooltipContexts = typeof tooltipContexts;
export type TooltipRegisterKey = keyof typeof tooltips.register;

export type RegisterField<Type extends MimicComponentType = MimicComponentType> =
  keyof TooltipContexts[Type];

export type TooltipContextMap = {
  register: Record<string, RegisterField>;
  contexts: {
    [Type in MimicComponentType]: {
      [K in RegisterField<Type>]: TooltipComponentContext<Type> | TooltipComponentContext<Type>[];
    };
  };
};

const firstOrUndefined = <T>(
  value: T | T[] | undefined,
  arrayIndexIfDuplicate = 0,
): T | undefined => {
  if (Array.isArray(value)) {
    return value[arrayIndexIfDuplicate];
  }
  return value;
};

const defaultContext: TooltipComponentContext = {
  controllerState: {},
  controls: {},
  custom: {},
  parameters: {},
  sensors: {},
  source: undefined,
  tooltip: {
    title: "Unknown yard tag or module field",
  },
};

export const getTooltipContext =
  <Type extends MimicComponentType>(type: Type) =>
  (registerField: RegisterField<Type>, arrayIndexIfMultiple = 0): TooltipComponentContext<Type> => {
    const context = firstOrUndefined(tooltipContexts[type][registerField], arrayIndexIfMultiple);

    return {
      registerField,
      type,
      ...defaultContext,
      ...(context ?? {}),
    } as TooltipComponentContext<Type>;
  };

export const getTooltipContexts = <
  Type extends MimicComponentType,
  Fields extends RegisterField<Type>[],
>(
  type: Type,
  contextFields: Fields,
  arrayIndexIfMultiple = 0,
): {
  [K in Fields[number]]: TooltipComponentContext<Type>;
} => {
  const result: Partial<Record<Fields[number], TooltipComponentContext<Type>>> = {};
  const getContext = getTooltipContext(type);

  for (const field of contextFields) {
    result[field] = getContext(field, arrayIndexIfMultiple);
  }

  return result as { [K in Fields[number]]: TooltipComponentContext<Type> };
};

export const findTooltipContext = <Type extends MimicComponentType = MimicComponentType>(
  key: TooltipRegisterKey | RegisterField<Type> | string | ModuleField,
): TooltipComponentContext<Type>[] => {
  const contextField =
    tooltips.register[
      Array.isArray(key)
        ? (`${key[1]}:${key[2]}` as TooltipRegisterKey)
        : (key as TooltipRegisterKey)
    ];

  if (contextField === undefined) {
    return [];
  }

  const [type, ...yardTagParts] = contextField.split("/");
  const yardTag = yardTagParts.join("/");
  const context = tooltipContexts[type as Type][yardTag as RegisterField<Type>];

  const ctxs = Array.isArray(context) ? context : context !== undefined ? [context] : [];

  return ctxs.map((ctx) => ({ ...defaultContext, ...ctx }));
};
