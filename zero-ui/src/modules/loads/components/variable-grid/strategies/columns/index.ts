import { max, minBy, sum, sumBy, zip } from "lodash";
import { GridGroup, hasBoolUnit } from "../..";
import { VariableGroup } from "../../../../lib/consts.dashboards";
import { SailPositionGroup, Variable } from "../../../../types";
import FixedColumnsLayout from "./FixedColumnsLayout.vue";
import SmartColumnsLayout from "./SmartColumnsLayout.vue";

export type ColumnLayout = typeof SmartColumnsLayout | typeof FixedColumnsLayout;

export { default as FixedColumnsLayout } from "./FixedColumnsLayout.vue";
export { default as SmartColumnsLayout } from "./SmartColumnsLayout.vue";

export type ColumnGroup = {
  size: number;
  groups: GridGroup[];
};

export type PositionColumns<T> = [start: T, center: T, end: T];
export type ColumnPartitions = PositionColumns<VariableGroup<Variable>[]>;
export type SizedColumnPartitions = PositionColumns<ColumnGroup>;

export const MIN_COLUMN_SIZE = 1;

export const createColumnPartitions = (
  variableGroups: VariableGroup<Variable>[],
  positionGroups: SailPositionGroup[],
): ColumnPartitions => {
  const groupsByPosition = Object.groupBy(variableGroups, (group) => group.position);

  return positionGroups.map((positionGroup) =>
    positionGroup.positions.flatMap(({ position }) => groupsByPosition[position] ?? []),
  ) as ColumnPartitions;
};

const toGridGroup =
  (size: number) =>
  (group: VariableGroup<Variable>): GridGroup => ({
    size,
    group,
    variables: group.variables,
    hasBooleans: group.variables.some(hasBoolUnit),
  });

const toColumnGroup = ([variableGroups = [], columnSize = MIN_COLUMN_SIZE]: [
  variableGroups: VariableGroup<Variable>[] | undefined,
  columnSize: number | undefined,
]): ColumnGroup => ({
  size: columnSize,
  groups: variableGroups.map(toGridGroup(columnSize)),
});

/** Fixed columns */

export const createFixedColumnGroups = (
  partitions: ColumnPartitions,
  gridSize: number,
): SizedColumnPartitions => {
  const columnSpans = getSymmetricColumnSpans(gridSize);

  return zip(partitions, columnSpans).map(toColumnGroup) as SizedColumnPartitions;
};

export const getSymmetricColumnSpans = (gridSize: number): PositionColumns<number> => {
  const centerBonus = gridSize > 3 ? gridSize % 2 : 0;
  const startAndEnd = Math.round((gridSize - centerBonus) / 3);
  return [startAndEnd, gridSize - startAndEnd * 2 + centerBonus, startAndEnd];
};

/* Smart columns */

// This will brute-force all possible column span combinations and select the one that results in the lowest number of rows.
export const createSmartColumnGroups = (
  partitions: ColumnPartitions,
  gridSize: number,
): SizedColumnPartitions => {
  const columnWidthCombinations = getColumnWidthCombinations(gridSize);

  const firstCombinationWithBestScore = minBy(
    columnWidthCombinations,
    getHighestColumnRowCount(partitions),
  );

  if (!firstCombinationWithBestScore) {
    return createFixedColumnGroups(partitions, gridSize);
  }

  return zip(partitions, firstCombinationWithBestScore).map(toColumnGroup) as SizedColumnPartitions;
};

const createColumnSizes = (gridSize: number, otherColumns: number[]) =>
  Array.from({ length: gridSize - sum(otherColumns) }, (_, index) => MIN_COLUMN_SIZE + index);

export const getColumnWidthCombinations = (gridSize: number): PositionColumns<number>[] =>
  createColumnSizes(gridSize, [MIN_COLUMN_SIZE, MIN_COLUMN_SIZE]).flatMap((start) =>
    createColumnSizes(gridSize, [start, MIN_COLUMN_SIZE]).map(
      (center) => [start, center, gridSize - start - center] as PositionColumns<number>,
    ),
  );

export const getHighestColumnRowCount =
  (partitions: ColumnPartitions) => (columnWidths: PositionColumns<number>) => {
    const rowCounts = zip(partitions, columnWidths).map(
      ([groupsInColumn = [], columnWidth = MIN_COLUMN_SIZE]) =>
        sumBy(groupsInColumn, (group) => Math.ceil(group.variables.length / columnWidth)),
    );

    return max(rowCounts);
  };
