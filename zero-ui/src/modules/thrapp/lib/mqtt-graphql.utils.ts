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
