import { entriesOf } from "@/modules/common/lib/utils";
import { BREAKPOINTS, BreakpointsZero } from "@/modules/common/stores/ui";
import { last, sum } from "lodash";
import { createContext } from "reka-ui";
import { Ref } from "vue";
import { VariableGroup } from "../../lib/consts.dashboards";
import { CardType, MaybeVariable, Variable, VariableUnit } from "../../types";

export { default as VariableGrid } from "./VariableGrid.vue";
export { default as VariableGridGroup } from "./VariableGridGroup.vue";
export { default as VariableGridHeader } from "./VariableGridHeader.vue";
export { default as VariableGridHeaderLabel } from "./VariableGridHeaderLabel.vue";
export { default as VariableGridHeaderTitle } from "./VariableGridHeaderTitle.vue";
export { default as VariableGridItem } from "./VariableGridItem.vue";

export type VariableGridContext = {
  type: Ref<CardType>;
};

export type GridBreakpoints = keyof BreakpointsZero | "";

export const NUMERIC_GRID_SIZE: Record<GridBreakpoints, number> = {
  "": 2,
  sm: 3,
  md: 4,
  lg: 5,
  xl: 7,
  "2xl": 9,
  "3xl": 11,
  "4xl": 13,
};

export const GAUGE_GRID_SIZE: Record<GridBreakpoints, number> = {
  "": 2,
  sm: 2,
  md: 4,
  lg: 4,
  xl: 6,
  "2xl": 8,
  "3xl": 10,
  "4xl": 12,
};

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

export const toGroupInnerSize = (type: CardType, innerSize: number, multiplier: number = 1) =>
  toBreakpoints(
    type,
    (gridSize) => `grid-cols-${Math.min(innerSize * multiplier, gridSize * multiplier)}`,
  );

export const toGroupOuterSize = (type: CardType, outerSize: number) =>
  toBreakpoints(type, (gridSize) => `col-span-${Math.min(outerSize, gridSize)}`);

export interface GridGroup {
  name: string;
  totalAmount: number;
  size: number;
  gridCols: string;
  gridSpan: string;
  variables: Variable[];
}

export const getGridSize = (type: CardType) => {
  const currentBreakpoint = BREAKPOINTS.active().value;

  if (currentBreakpoint === "") {
    return 0;
  } else {
    return type === "numerical"
      ? NUMERIC_GRID_SIZE[currentBreakpoint]
      : GAUGE_GRID_SIZE[currentBreakpoint];
  }
};

export const getItemSize =
  (type: CardType) =>
  (variable: Variable): number => {
    // Assumption: mast locks are never grouped with other variable types
    // Mast lock is 2/3 size of numerical card
    if (variable.variable?.unit === VariableUnit.Bool) {
      return 2 / 3;
    }
    // In case of numerical view: each card has size 1
    else if (type === "numerical") {
      return 1;
    } else if (
      variable.variable?.scaleMin !== undefined &&
      variable.variable?.scaleMax !== undefined &&
      (variable.variable?.unit === VariableUnit.Ratio ||
        variable.variable?.unit === VariableUnit.Tonne)
    ) {
      return 2;
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

export const createGridGroups = (
  groups: VariableGroup[],
  cardType: CardType,
  isDynamicDashboard: boolean,
  allVariables: MaybeVariable[],
): GridGroup[] => {
  let currentRowSize = 0;
  const gridSize = getGridSize(cardType);

  const _getItemSize = getItemSize(cardType);
  const _getGroupVariables = getGroupVariables(allVariables, isDynamicDashboard);

  const mapToSubGroup =
    (name: string, groupVariables: Variable[]) =>
    (variables: Variable[]): GridGroup => {
      const onOffs = variables.filter(
        ({ variable }) => variable?.unit === VariableUnit.Bool,
      ).length;
      const groupSize = Math.ceil(sum(variables.map(_getItemSize)));

      return {
        name: name,
        totalAmount: groupVariables.length,
        size: groupSize,
        gridCols: toGroupInnerSize(cardType, groupSize, onOffs > 0 ? 3 : 1),
        gridSpan: toGroupOuterSize(cardType, groupSize),
        variables,
      };
    };

  const createSubGroups = (group: VariableGroup): GridGroup[] => {
    const groupVariables = _getGroupVariables(group);
    const _mapToSubGroup = mapToSubGroup(group.name, groupVariables);

    return groupVariables
      .reduce((subGroups, variable) => {
        const size = _getItemSize(variable);
        let lastSubGroup = last(subGroups) ?? [];

        if (currentRowSize + size > gridSize) {
          lastSubGroup = [variable];
          currentRowSize = size;
        } else {
          lastSubGroup.push(variable);
          currentRowSize += size;
        }

        return subGroups.includes(lastSubGroup) ? subGroups : [...subGroups, lastSubGroup];
      }, [] as Variable[][])
      .map(_mapToSubGroup);
  };

  return groups.flatMap(createSubGroups);
};

export const [getContext, provideContext] =
  createContext<VariableGridContext>("loads.variable-grid");
