import { ChartDataType, Stamped } from "@/modules/common/types";
import { ModuleDefinition, THRSModule } from "@/modules/thrapp/types/thrs";
import { DEFINITIONS } from "./consts";
import { MQTT_GRAPHQL_DEFINITIONS } from "./definitions.generated";

export type ThrsDefinitions<T extends Record<string, ModuleDefinition> = typeof DEFINITIONS> = T;

export type ThrsModules<
  TDefinitions extends Record<string, ModuleDefinition> = typeof DEFINITIONS,
> = {
  [K in keyof TDefinitions]: THRSModule<TDefinitions[K]>;
};

export type ComponentRecord<
  T extends Record<string, Stamped<ChartDataType>> = Record<string, Stamped<ChartDataType>>,
> = T;

type MqttGraphqlThrsModules = ThrsModules<typeof MQTT_GRAPHQL_DEFINITIONS>;

/**
 * thrapp's modules as the MQTT GraphQL API serves them: every module of the generated definitions,
 * with the parts the query selected, each with the components the API has a value for.
 */
export type MqttGraphqlModules = {
  [Module in keyof MqttGraphqlThrsModules]: {
    [Part in keyof MqttGraphqlThrsModules[Module]]?: Partial<MqttGraphqlThrsModules[Module][Part]>;
  };
};
