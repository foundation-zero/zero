import { entriesOf } from "@/modules/common/lib/utils";
import { BREAKPOINTS } from "@/modules/common/stores/ui";
import { createContext } from "reka-ui";
import { VariableGroup } from "../../lib/consts.dashboards";
import { CardType, MaybeVariable, Variable, VariableUnit } from "../../types";
import { GAUGE_GRID_SIZE, NUMERIC_GRID_SIZE } from "./consts";
import { GridBreakpoints, VariableGridContext } from "./variable-grid.types";

export const toBreakpoints = (
  type: CardType,
  mapFn: (gridSize: number, breakpoint: GridBreakpoints) => string,
) =>
  entriesOf(type === "numerical" ? NUMERIC_GRID_SIZE : GAUGE_GRID_SIZE)
    .map(([breakpoint, size]) =>
      breakpoint === "" ? mapFn(size, breakpoint) : `${breakpoint}:${mapFn(size, breakpoint)}`,
    )
    .join(" ");

export const toGridSize = (type: CardType) =>
  toBreakpoints(type, (gridSize) => `grid-cols-${gridSize}`);

export const hasBoolUnit = (variable: Variable) => variable.variable.unit === VariableUnit.Bool;

export const getGridSize = (type: CardType) => {
  const currentBreakpoint = BREAKPOINTS.active().value;

  return type === "numerical"
    ? NUMERIC_GRID_SIZE[currentBreakpoint]
    : GAUGE_GRID_SIZE[currentBreakpoint];
};

export const getItemSize =
  (type: CardType) =>
  (variable: Variable): number => {
    if (variable.variable?.unit === VariableUnit.Bool) {
      return (type === "numerical" ? 2 : 1) / 3;
    } else {
      return 1;
    }
  };

export const getGroupVariables =
  (variables: MaybeVariable[], isDynamicDashboard: boolean) => (group: VariableGroup) =>
    group.variables
      .filter(([, includeInDynamic]) => includeInDynamic || !isDynamicDashboard)
      .map(([id]) => variables.find((v) => v.id === id))
      .filter((v): v is Variable => !!v && !!v.variable);

export const getGroupsWithVariables = (variables: MaybeVariable[], isDynamicDashboard: boolean) => {
  const _getGroupVariables = getGroupVariables(variables, isDynamicDashboard);

  return (group: VariableGroup): VariableGroup<Variable> => ({
    ...group,
    variables: _getGroupVariables(group),
  });
};

export const [getContext, provideContext] =
  createContext<VariableGridContext>("loads.variable-grid");
