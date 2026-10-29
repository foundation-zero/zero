import { sum, unzip, zip } from "lodash";
import { getGridSize, getItemSize, GridGroup, hasBoolUnit } from "../..";
import { VariableGroup } from "../../../../lib/consts.dashboards";
import { CardType, Variable } from "../../../../types";
import { ItemSizeFn, RowPartitioner, VariableWithSize } from "./rows.types";

const createRowPartitioner = (gridSize: number): RowPartitioner => {
  let rowSpaceAlreadyTaken = 0;
  let currentRowIndex = 0;

  return (sizeToAdd: number) => {
    if (rowSpaceAlreadyTaken + sizeToAdd > gridSize) {
      rowSpaceAlreadyTaken = sizeToAdd;
      currentRowIndex++;
    } else {
      rowSpaceAlreadyTaken += sizeToAdd;
    }

    return currentRowIndex;
  };
};

const createSubGroups =
  (partition: RowPartitioner, getItemSize: ItemSizeFn) =>
  (group: VariableGroup<Variable>): GridGroup[] => {
    const variablesWithSizes = zip(
      group.variables,
      group.variables.map(getItemSize),
    ) as VariableWithSize[];

    const partitionedVariables = Object.groupBy(variablesWithSizes, ([, size]) => partition(size));

    return Object.values(partitionedVariables).map((variablesWithSizes) => {
      const [variables, sizes] = unzip(variablesWithSizes!);

      return {
        size: sum(sizes),
        group,
        variables,
        hasBooleans: variables.some(hasBoolUnit),
      };
    });
  };

export const createBrokenRowGroups = (
  groups: VariableGroup<Variable>[],
  cardType: CardType,
): GridGroup[] => {
  const gridSize = getGridSize(cardType);
  const partitioner = createRowPartitioner(gridSize);
  const _getItemSize = getItemSize(cardType);
  const _createSubGroups = createSubGroups(partitioner, _getItemSize);

  return groups.flatMap(_createSubGroups);
};

export const createUnbrokenRowGroups = (
  groups: VariableGroup<Variable>[],
  gridSize: number,
): GridGroup[] =>
  groups.map((group) => ({
    size: gridSize,
    group,
    variables: group.variables,
    hasBooleans: group.variables.some(hasBoolUnit),
  }));
