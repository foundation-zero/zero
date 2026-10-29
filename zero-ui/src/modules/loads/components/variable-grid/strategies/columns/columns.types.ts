import { GridGroup } from "../..";
import { VariableGroup } from "../../../../lib/consts.dashboards";
import { Variable } from "../../../../types";
import FixedColumnsLayout from "./FixedColumnsLayout.vue";
import SmartColumnsLayout from "./SmartColumnsLayout.vue";

export type ColumnLayout = typeof SmartColumnsLayout | typeof FixedColumnsLayout;

export type ColumnGroup = {
  size: number;
  groups: GridGroup[];
};

export type PositionColumns<T> = [start: T, center: T, end: T];
export type ColumnPartitions = PositionColumns<VariableGroup<Variable>[]>;
export type SizedColumnPartitions = PositionColumns<ColumnGroup>;
