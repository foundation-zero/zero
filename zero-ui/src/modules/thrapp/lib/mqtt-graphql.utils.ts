import { capitalizeFirst } from "@/modules/common/lib/utils";
import { gql } from "@urql/vue";
import { isThrsApiModule, ThrsApiModule } from "./consts";
import { MqttGraphqlModules } from "./consts.types";
import { MQTT_GRAPHQL_DEFINITIONS } from "./definitions.generated";

const isObject = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null && !Array.isArray(value);

/** The value at `path` in a response; `undefined` where the response has nothing there. */
export const valueAt = (response: unknown, path: readonly string[]): unknown =>
  path.reduce<unknown>((node, key) => (isObject(node) ? node[key] : undefined), response);

/**
 * Whether the response's query selected the part with components at `paths`: a component is
 * there, a value or null, or the topic holding them, such as the parameters, is null.
 */
const isQueried = (response: unknown, paths: (readonly string[])[]): boolean =>
  paths.some(
    (path) =>
      valueAt(response, path) !== undefined || valueAt(response, path.slice(0, -1)) === null,
  );

/**
 * thrapp's modules from an MQTT GraphQL response to the generated fragments. Every component of
 * the generated definitions is read at its path; one the API has no value for (`null`) is left
 * out, and anything else in the response is ignored. A part is there only if the response's query
 * selected it, so a view can tell a part it did not query from one without values.
 */
export function toThrsModules(response: unknown): MqttGraphqlModules {
  const modules = Object.fromEntries(
    Object.entries(MQTT_GRAPHQL_DEFINITIONS).map(([module, parts]) => [
      module,
      Object.fromEntries(
        Object.entries(parts)
          .map(([part, definitions]) => [part, Object.entries(definitions)] as const)
          .filter(([, components]) =>
            isQueried(
              response,
              components.map(([, { path }]) => path),
            ),
          )
          .map(([part, components]) => [
            part,
            Object.fromEntries(
              components.flatMap(([component, { path }]) => {
                const value = valueAt(response, path);
                return value == undefined ? [] : [[component, value]];
              }),
            ),
          ]),
      ),
    ]),
  );
  // The fragments select exactly each definition's fields, so a value has its definition's type.
  return modules as MqttGraphqlModules;
}

export type ControllerInput = "parameters" | "controlValues";

const INPUT_TYPES: Record<ControllerInput, string> = {
  parameters: "Parameters",
  controlValues: "ControlValues",
};

// Only modules with a controller take parameters, control values and an automation mode.
function assertController(module: string): asserts module is ThrsApiModule {
  if (!isThrsApiModule(module)) {
    throw new Error(`${module} has no controller`);
  }
}

// A module's controller takes its parameters and control values on the MQTT GraphQL API, each
// as one input object; the API returns once the parameters are stored and once the AMCS has
// actuated the control values. Only modules with a controller have them; the API names their
// input types after the module. The response is not used: the view's query is refreshed instead.
export const controllerMutation = (module: string, part: ControllerInput) => {
  assertController(module);
  const inputType = `ThrsControl${capitalizeFirst(module)}${INPUT_TYPES[part]}Input`;
  return gql`
    mutation ($input: ${inputType}!) {
      thrs { controller { ${module} { ${part}(input: $input) { __typename } } } }
    }
  `;
};

// A module's automation mode. The API returns once the module has taken the switch; a switch to
// automatic while the AMCS is not advisory is not taken, and the mutation times out.
export function automationModeMutation(module: string) {
  assertController(module);
  return gql`
    mutation ($input: ThrsControlAutomationModeInput!) {
      thrs { controller { ${module} { automationMode(input: $input) { mode } } } }
    }
  `;
}

// A component's control values, each stamped with now, so thrs-control takes them as the newest
// setpoints.
export const stampedValues = (values: Record<string, unknown>) => {
  const timeStamp = new Date().toISOString();
  return Object.fromEntries(
    Object.entries(values).map(([name, value]) => [name, { value, timeStamp }]),
  );
};
