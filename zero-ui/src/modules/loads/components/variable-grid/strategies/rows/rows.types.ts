import { Variable } from "../../../../types";
import BrokenRowsLayout from "./BrokenRowsLayout.vue";
import UnbrokenRowsLayout from "./UnbrokenRowsLayout.vue";

export type RowLayout = typeof BrokenRowsLayout | typeof UnbrokenRowsLayout;

export type VariableWithSize = [variable: Variable, size: number];
export type RowPartitioner = (sizeToAdd: number) => number;
export type ItemSizeFn = (variable: Variable) => number;
