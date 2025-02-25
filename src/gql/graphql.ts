/* eslint-disable */
import type { TypedDocumentNode as DocumentNode } from "@graphql-typed-document-node/core";
export type Maybe<T> = T | null;
export type InputMaybe<T> = Maybe<T>;
export type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
export type MakeOptional<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]?: Maybe<T[SubKey]> };
export type MakeMaybe<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]: Maybe<T[SubKey]> };
export type MakeEmpty<T extends { [key: string]: unknown }, K extends keyof T> = {
  [_ in K]?: never;
};
export type Incremental<T> =
  | T
  | { [P in keyof T]?: P extends " $fragmentName" | "__typename" ? T[P] : never };
/** All built-in and custom scalars, mapped to their actual values */
export type Scalars = {
  ID: { input: string; output: string };
  String: { input: string; output: string };
  Boolean: { input: boolean; output: boolean };
  Int: { input: number; output: number };
  Float: { input: number; output: number };
  Void: { input: any; output: any };
  blind_opacity: { input: any; output: any };
  timestamptz: { input: any; output: any };
};

/** Boolean expression to compare columns of type "blind_opacity". All fields are combined with logical 'AND'. */
export type BlindOpacityComparisonExp = {
  _eq?: InputMaybe<Scalars["blind_opacity"]["input"]>;
  _gt?: InputMaybe<Scalars["blind_opacity"]["input"]>;
  _gte?: InputMaybe<Scalars["blind_opacity"]["input"]>;
  _in?: InputMaybe<Array<Scalars["blind_opacity"]["input"]>>;
  _isNull?: InputMaybe<Scalars["Boolean"]["input"]>;
  _lt?: InputMaybe<Scalars["blind_opacity"]["input"]>;
  _lte?: InputMaybe<Scalars["blind_opacity"]["input"]>;
  _neq?: InputMaybe<Scalars["blind_opacity"]["input"]>;
  _nin?: InputMaybe<Array<Scalars["blind_opacity"]["input"]>>;
};

/** columns and relationships of "blinds" */
export type Blinds = {
  __typename?: "Blinds";
  group: Scalars["String"]["output"];
  id: Scalars["String"]["output"];
  level: Scalars["Float"]["output"];
  name: Scalars["String"]["output"];
  opacity?: Maybe<Scalars["blind_opacity"]["output"]>;
  roomId?: Maybe<Scalars["String"]["output"]>;
};

/** aggregated selection of "blinds" */
export type BlindsAggregate = {
  __typename?: "BlindsAggregate";
  aggregate?: Maybe<BlindsAggregateFields>;
  nodes: Array<Blinds>;
};

export type BlindsAggregateBoolExp = {
  count?: InputMaybe<BlindsAggregateBoolExpCount>;
};

/** aggregate fields of "blinds" */
export type BlindsAggregateFields = {
  __typename?: "BlindsAggregateFields";
  avg?: Maybe<BlindsAvgFields>;
  count: Scalars["Int"]["output"];
  max?: Maybe<BlindsMaxFields>;
  min?: Maybe<BlindsMinFields>;
  stddev?: Maybe<BlindsStddevFields>;
  stddevPop?: Maybe<BlindsStddevPopFields>;
  stddevSamp?: Maybe<BlindsStddevSampFields>;
  sum?: Maybe<BlindsSumFields>;
  varPop?: Maybe<BlindsVarPopFields>;
  varSamp?: Maybe<BlindsVarSampFields>;
  variance?: Maybe<BlindsVarianceFields>;
};

/** aggregate fields of "blinds" */
export type BlindsAggregateFieldsCountArgs = {
  columns?: InputMaybe<Array<BlindsSelectColumn>>;
  distinct?: InputMaybe<Scalars["Boolean"]["input"]>;
};

/** order by aggregate values of table "blinds" */
export type BlindsAggregateOrderBy = {
  avg?: InputMaybe<BlindsAvgOrderBy>;
  count?: InputMaybe<OrderBy>;
  max?: InputMaybe<BlindsMaxOrderBy>;
  min?: InputMaybe<BlindsMinOrderBy>;
  stddev?: InputMaybe<BlindsStddevOrderBy>;
  stddevPop?: InputMaybe<BlindsStddevPopOrderBy>;
  stddevSamp?: InputMaybe<BlindsStddevSampOrderBy>;
  sum?: InputMaybe<BlindsSumOrderBy>;
  varPop?: InputMaybe<BlindsVarPopOrderBy>;
  varSamp?: InputMaybe<BlindsVarSampOrderBy>;
  variance?: InputMaybe<BlindsVarianceOrderBy>;
};

/** aggregate avg on columns */
export type BlindsAvgFields = {
  __typename?: "BlindsAvgFields";
  level?: Maybe<Scalars["Float"]["output"]>;
};

/** order by avg() on columns of table "blinds" */
export type BlindsAvgOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** Boolean expression to filter rows from the table "blinds". All fields are combined with a logical 'AND'. */
export type BlindsBoolExp = {
  _and?: InputMaybe<Array<BlindsBoolExp>>;
  _not?: InputMaybe<BlindsBoolExp>;
  _or?: InputMaybe<Array<BlindsBoolExp>>;
  group?: InputMaybe<StringComparisonExp>;
  id?: InputMaybe<StringComparisonExp>;
  level?: InputMaybe<FloatComparisonExp>;
  name?: InputMaybe<StringComparisonExp>;
  opacity?: InputMaybe<BlindOpacityComparisonExp>;
  roomId?: InputMaybe<StringComparisonExp>;
};

/** aggregate max on columns */
export type BlindsMaxFields = {
  __typename?: "BlindsMaxFields";
  group?: Maybe<Scalars["String"]["output"]>;
  id?: Maybe<Scalars["String"]["output"]>;
  level?: Maybe<Scalars["Float"]["output"]>;
  name?: Maybe<Scalars["String"]["output"]>;
  opacity?: Maybe<Scalars["blind_opacity"]["output"]>;
  roomId?: Maybe<Scalars["String"]["output"]>;
};

/** order by max() on columns of table "blinds" */
export type BlindsMaxOrderBy = {
  group?: InputMaybe<OrderBy>;
  id?: InputMaybe<OrderBy>;
  level?: InputMaybe<OrderBy>;
  name?: InputMaybe<OrderBy>;
  opacity?: InputMaybe<OrderBy>;
  roomId?: InputMaybe<OrderBy>;
};

/** aggregate min on columns */
export type BlindsMinFields = {
  __typename?: "BlindsMinFields";
  group?: Maybe<Scalars["String"]["output"]>;
  id?: Maybe<Scalars["String"]["output"]>;
  level?: Maybe<Scalars["Float"]["output"]>;
  name?: Maybe<Scalars["String"]["output"]>;
  opacity?: Maybe<Scalars["blind_opacity"]["output"]>;
  roomId?: Maybe<Scalars["String"]["output"]>;
};

/** order by min() on columns of table "blinds" */
export type BlindsMinOrderBy = {
  group?: InputMaybe<OrderBy>;
  id?: InputMaybe<OrderBy>;
  level?: InputMaybe<OrderBy>;
  name?: InputMaybe<OrderBy>;
  opacity?: InputMaybe<OrderBy>;
  roomId?: InputMaybe<OrderBy>;
};

/** Ordering options when selecting data from "blinds". */
export type BlindsOrderBy = {
  group?: InputMaybe<OrderBy>;
  id?: InputMaybe<OrderBy>;
  level?: InputMaybe<OrderBy>;
  name?: InputMaybe<OrderBy>;
  opacity?: InputMaybe<OrderBy>;
  roomId?: InputMaybe<OrderBy>;
};

/** select columns of table "blinds" */
export enum BlindsSelectColumn {
  /** column name */
  Group = "group",
  /** column name */
  Id = "id",
  /** column name */
  Level = "level",
  /** column name */
  Name = "name",
  /** column name */
  Opacity = "opacity",
  /** column name */
  RoomId = "roomId",
}

/** aggregate stddev on columns */
export type BlindsStddevFields = {
  __typename?: "BlindsStddevFields";
  level?: Maybe<Scalars["Float"]["output"]>;
};

/** order by stddev() on columns of table "blinds" */
export type BlindsStddevOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** aggregate stddevPop on columns */
export type BlindsStddevPopFields = {
  __typename?: "BlindsStddevPopFields";
  level?: Maybe<Scalars["Float"]["output"]>;
};

/** order by stddevPop() on columns of table "blinds" */
export type BlindsStddevPopOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** aggregate stddevSamp on columns */
export type BlindsStddevSampFields = {
  __typename?: "BlindsStddevSampFields";
  level?: Maybe<Scalars["Float"]["output"]>;
};

/** order by stddevSamp() on columns of table "blinds" */
export type BlindsStddevSampOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** Streaming cursor of the table "blinds" */
export type BlindsStreamCursorInput = {
  /** Stream column input with initial value */
  initialValue: BlindsStreamCursorValueInput;
  /** cursor ordering */
  ordering?: InputMaybe<CursorOrdering>;
};

/** Initial value of the column from where the streaming should start */
export type BlindsStreamCursorValueInput = {
  group?: InputMaybe<Scalars["String"]["input"]>;
  id?: InputMaybe<Scalars["String"]["input"]>;
  level?: InputMaybe<Scalars["Float"]["input"]>;
  name?: InputMaybe<Scalars["String"]["input"]>;
  opacity?: InputMaybe<Scalars["blind_opacity"]["input"]>;
  roomId?: InputMaybe<Scalars["String"]["input"]>;
};

/** aggregate sum on columns */
export type BlindsSumFields = {
  __typename?: "BlindsSumFields";
  level?: Maybe<Scalars["Float"]["output"]>;
};

/** order by sum() on columns of table "blinds" */
export type BlindsSumOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** aggregate varPop on columns */
export type BlindsVarPopFields = {
  __typename?: "BlindsVarPopFields";
  level?: Maybe<Scalars["Float"]["output"]>;
};

/** order by varPop() on columns of table "blinds" */
export type BlindsVarPopOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** aggregate varSamp on columns */
export type BlindsVarSampFields = {
  __typename?: "BlindsVarSampFields";
  level?: Maybe<Scalars["Float"]["output"]>;
};

/** order by varSamp() on columns of table "blinds" */
export type BlindsVarSampOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** aggregate variance on columns */
export type BlindsVarianceFields = {
  __typename?: "BlindsVarianceFields";
  level?: Maybe<Scalars["Float"]["output"]>;
};

/** order by variance() on columns of table "blinds" */
export type BlindsVarianceOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** Boolean expression to compare columns of type "Boolean". All fields are combined with logical 'AND'. */
export type BooleanComparisonExp = {
  _eq?: InputMaybe<Scalars["Boolean"]["input"]>;
  _gt?: InputMaybe<Scalars["Boolean"]["input"]>;
  _gte?: InputMaybe<Scalars["Boolean"]["input"]>;
  _in?: InputMaybe<Array<Scalars["Boolean"]["input"]>>;
  _isNull?: InputMaybe<Scalars["Boolean"]["input"]>;
  _lt?: InputMaybe<Scalars["Boolean"]["input"]>;
  _lte?: InputMaybe<Scalars["Boolean"]["input"]>;
  _neq?: InputMaybe<Scalars["Boolean"]["input"]>;
  _nin?: InputMaybe<Array<Scalars["Boolean"]["input"]>>;
};

/** ordering argument of a cursor */
export enum CursorOrdering {
  /** ascending ordering of the cursor */
  Asc = "ASC",
  /** descending ordering of the cursor */
  Desc = "DESC",
}

/** Boolean expression to compare columns of type "Float". All fields are combined with logical 'AND'. */
export type FloatComparisonExp = {
  _eq?: InputMaybe<Scalars["Float"]["input"]>;
  _gt?: InputMaybe<Scalars["Float"]["input"]>;
  _gte?: InputMaybe<Scalars["Float"]["input"]>;
  _in?: InputMaybe<Array<Scalars["Float"]["input"]>>;
  _isNull?: InputMaybe<Scalars["Boolean"]["input"]>;
  _lt?: InputMaybe<Scalars["Float"]["input"]>;
  _lte?: InputMaybe<Scalars["Float"]["input"]>;
  _neq?: InputMaybe<Scalars["Float"]["input"]>;
  _nin?: InputMaybe<Array<Scalars["Float"]["input"]>>;
};

/** Boolean expression to compare columns of type "Int". All fields are combined with logical 'AND'. */
export type IntComparisonExp = {
  _eq?: InputMaybe<Scalars["Int"]["input"]>;
  _gt?: InputMaybe<Scalars["Int"]["input"]>;
  _gte?: InputMaybe<Scalars["Int"]["input"]>;
  _in?: InputMaybe<Array<Scalars["Int"]["input"]>>;
  _isNull?: InputMaybe<Scalars["Boolean"]["input"]>;
  _lt?: InputMaybe<Scalars["Int"]["input"]>;
  _lte?: InputMaybe<Scalars["Int"]["input"]>;
  _neq?: InputMaybe<Scalars["Int"]["input"]>;
  _nin?: InputMaybe<Array<Scalars["Int"]["input"]>>;
};

/** columns and relationships of "lighting_groups" */
export type LightingGroups = {
  __typename?: "LightingGroups";
  id: Scalars["String"]["output"];
  level: Scalars["Float"]["output"];
  name: Scalars["String"]["output"];
  roomId?: Maybe<Scalars["String"]["output"]>;
};

/** aggregated selection of "lighting_groups" */
export type LightingGroupsAggregate = {
  __typename?: "LightingGroupsAggregate";
  aggregate?: Maybe<LightingGroupsAggregateFields>;
  nodes: Array<LightingGroups>;
};

export type LightingGroupsAggregateBoolExp = {
  count?: InputMaybe<LightingGroupsAggregateBoolExpCount>;
};

/** aggregate fields of "lighting_groups" */
export type LightingGroupsAggregateFields = {
  __typename?: "LightingGroupsAggregateFields";
  avg?: Maybe<LightingGroupsAvgFields>;
  count: Scalars["Int"]["output"];
  max?: Maybe<LightingGroupsMaxFields>;
  min?: Maybe<LightingGroupsMinFields>;
  stddev?: Maybe<LightingGroupsStddevFields>;
  stddevPop?: Maybe<LightingGroupsStddevPopFields>;
  stddevSamp?: Maybe<LightingGroupsStddevSampFields>;
  sum?: Maybe<LightingGroupsSumFields>;
  varPop?: Maybe<LightingGroupsVarPopFields>;
  varSamp?: Maybe<LightingGroupsVarSampFields>;
  variance?: Maybe<LightingGroupsVarianceFields>;
};

/** aggregate fields of "lighting_groups" */
export type LightingGroupsAggregateFieldsCountArgs = {
  columns?: InputMaybe<Array<LightingGroupsSelectColumn>>;
  distinct?: InputMaybe<Scalars["Boolean"]["input"]>;
};

/** order by aggregate values of table "lighting_groups" */
export type LightingGroupsAggregateOrderBy = {
  avg?: InputMaybe<LightingGroupsAvgOrderBy>;
  count?: InputMaybe<OrderBy>;
  max?: InputMaybe<LightingGroupsMaxOrderBy>;
  min?: InputMaybe<LightingGroupsMinOrderBy>;
  stddev?: InputMaybe<LightingGroupsStddevOrderBy>;
  stddevPop?: InputMaybe<LightingGroupsStddevPopOrderBy>;
  stddevSamp?: InputMaybe<LightingGroupsStddevSampOrderBy>;
  sum?: InputMaybe<LightingGroupsSumOrderBy>;
  varPop?: InputMaybe<LightingGroupsVarPopOrderBy>;
  varSamp?: InputMaybe<LightingGroupsVarSampOrderBy>;
  variance?: InputMaybe<LightingGroupsVarianceOrderBy>;
};

/** aggregate avg on columns */
export type LightingGroupsAvgFields = {
  __typename?: "LightingGroupsAvgFields";
  level?: Maybe<Scalars["Float"]["output"]>;
};

/** order by avg() on columns of table "lighting_groups" */
export type LightingGroupsAvgOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** Boolean expression to filter rows from the table "lighting_groups". All fields are combined with a logical 'AND'. */
export type LightingGroupsBoolExp = {
  _and?: InputMaybe<Array<LightingGroupsBoolExp>>;
  _not?: InputMaybe<LightingGroupsBoolExp>;
  _or?: InputMaybe<Array<LightingGroupsBoolExp>>;
  id?: InputMaybe<StringComparisonExp>;
  level?: InputMaybe<FloatComparisonExp>;
  name?: InputMaybe<StringComparisonExp>;
  roomId?: InputMaybe<StringComparisonExp>;
};

/** aggregate max on columns */
export type LightingGroupsMaxFields = {
  __typename?: "LightingGroupsMaxFields";
  id?: Maybe<Scalars["String"]["output"]>;
  level?: Maybe<Scalars["Float"]["output"]>;
  name?: Maybe<Scalars["String"]["output"]>;
  roomId?: Maybe<Scalars["String"]["output"]>;
};

/** order by max() on columns of table "lighting_groups" */
export type LightingGroupsMaxOrderBy = {
  id?: InputMaybe<OrderBy>;
  level?: InputMaybe<OrderBy>;
  name?: InputMaybe<OrderBy>;
  roomId?: InputMaybe<OrderBy>;
};

/** aggregate min on columns */
export type LightingGroupsMinFields = {
  __typename?: "LightingGroupsMinFields";
  id?: Maybe<Scalars["String"]["output"]>;
  level?: Maybe<Scalars["Float"]["output"]>;
  name?: Maybe<Scalars["String"]["output"]>;
  roomId?: Maybe<Scalars["String"]["output"]>;
};

/** order by min() on columns of table "lighting_groups" */
export type LightingGroupsMinOrderBy = {
  id?: InputMaybe<OrderBy>;
  level?: InputMaybe<OrderBy>;
  name?: InputMaybe<OrderBy>;
  roomId?: InputMaybe<OrderBy>;
};

/** Ordering options when selecting data from "lighting_groups". */
export type LightingGroupsOrderBy = {
  id?: InputMaybe<OrderBy>;
  level?: InputMaybe<OrderBy>;
  name?: InputMaybe<OrderBy>;
  roomId?: InputMaybe<OrderBy>;
};

/** select columns of table "lighting_groups" */
export enum LightingGroupsSelectColumn {
  /** column name */
  Id = "id",
  /** column name */
  Level = "level",
  /** column name */
  Name = "name",
  /** column name */
  RoomId = "roomId",
}

/** aggregate stddev on columns */
export type LightingGroupsStddevFields = {
  __typename?: "LightingGroupsStddevFields";
  level?: Maybe<Scalars["Float"]["output"]>;
};

/** order by stddev() on columns of table "lighting_groups" */
export type LightingGroupsStddevOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** aggregate stddevPop on columns */
export type LightingGroupsStddevPopFields = {
  __typename?: "LightingGroupsStddevPopFields";
  level?: Maybe<Scalars["Float"]["output"]>;
};

/** order by stddevPop() on columns of table "lighting_groups" */
export type LightingGroupsStddevPopOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** aggregate stddevSamp on columns */
export type LightingGroupsStddevSampFields = {
  __typename?: "LightingGroupsStddevSampFields";
  level?: Maybe<Scalars["Float"]["output"]>;
};

/** order by stddevSamp() on columns of table "lighting_groups" */
export type LightingGroupsStddevSampOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** Streaming cursor of the table "lighting_groups" */
export type LightingGroupsStreamCursorInput = {
  /** Stream column input with initial value */
  initialValue: LightingGroupsStreamCursorValueInput;
  /** cursor ordering */
  ordering?: InputMaybe<CursorOrdering>;
};

/** Initial value of the column from where the streaming should start */
export type LightingGroupsStreamCursorValueInput = {
  id?: InputMaybe<Scalars["String"]["input"]>;
  level?: InputMaybe<Scalars["Float"]["input"]>;
  name?: InputMaybe<Scalars["String"]["input"]>;
  roomId?: InputMaybe<Scalars["String"]["input"]>;
};

/** aggregate sum on columns */
export type LightingGroupsSumFields = {
  __typename?: "LightingGroupsSumFields";
  level?: Maybe<Scalars["Float"]["output"]>;
};

/** order by sum() on columns of table "lighting_groups" */
export type LightingGroupsSumOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** aggregate varPop on columns */
export type LightingGroupsVarPopFields = {
  __typename?: "LightingGroupsVarPopFields";
  level?: Maybe<Scalars["Float"]["output"]>;
};

/** order by varPop() on columns of table "lighting_groups" */
export type LightingGroupsVarPopOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** aggregate varSamp on columns */
export type LightingGroupsVarSampFields = {
  __typename?: "LightingGroupsVarSampFields";
  level?: Maybe<Scalars["Float"]["output"]>;
};

/** order by varSamp() on columns of table "lighting_groups" */
export type LightingGroupsVarSampOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** aggregate variance on columns */
export type LightingGroupsVarianceFields = {
  __typename?: "LightingGroupsVarianceFields";
  level?: Maybe<Scalars["Float"]["output"]>;
};

/** order by variance() on columns of table "lighting_groups" */
export type LightingGroupsVarianceOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** column ordering options */
export enum OrderBy {
  /** in ascending order, nulls last */
  Asc = "ASC",
  /** in ascending order, nulls first */
  AscNullsFirst = "ASC_NULLS_FIRST",
  /** in ascending order, nulls last */
  AscNullsLast = "ASC_NULLS_LAST",
  /** in descending order, nulls first */
  Desc = "DESC",
  /** in descending order, nulls first */
  DescNullsFirst = "DESC_NULLS_FIRST",
  /** in descending order, nulls last */
  DescNullsLast = "DESC_NULLS_LAST",
}

/** columns and relationships of "rooms" */
export type Rooms = {
  __typename?: "Rooms";
  actualHumidity: Scalars["Float"]["output"];
  actualTemperature: Scalars["Float"]["output"];
  amplifierOn: Scalars["Boolean"]["output"];
  /** fetch data from the table: "blinds" */
  blinds: Array<Blinds>;
  /** fetch aggregated fields from the table: "blinds" */
  blindsAggregate?: BlindsAggregate;
  group: Scalars["String"]["output"];
  id: Scalars["String"]["output"];
  lastMovement?: Maybe<Scalars["timestamptz"]["output"]>;
  /** An array relationship */
  lightingGroups: Array<LightingGroups>;
  /** An aggregate relationship */
  lightingGroupsAggregate?: LightingGroupsAggregate;
  name: Scalars["String"]["output"];
  temperatureSetpoint: Scalars["Float"]["output"];
  thermalComfortIndex?: Maybe<Scalars["Float"]["output"]>;
};

/** columns and relationships of "rooms" */
export type RoomsBlindsArgs = {
  distinctOn?: InputMaybe<Array<BlindsSelectColumn>>;
  limit?: InputMaybe<Scalars["Int"]["input"]>;
  offset?: InputMaybe<Scalars["Int"]["input"]>;
  orderBy?: InputMaybe<Array<BlindsOrderBy>>;
  where?: InputMaybe<BlindsBoolExp>;
};

/** columns and relationships of "rooms" */
export type RoomsBlindsAggregateArgs = {
  distinctOn?: InputMaybe<Array<BlindsSelectColumn>>;
  limit?: InputMaybe<Scalars["Int"]["input"]>;
  offset?: InputMaybe<Scalars["Int"]["input"]>;
  orderBy?: InputMaybe<Array<BlindsOrderBy>>;
  where?: InputMaybe<BlindsBoolExp>;
};

/** columns and relationships of "rooms" */
export type RoomsLightingGroupsArgs = {
  distinctOn?: InputMaybe<Array<LightingGroupsSelectColumn>>;
  limit?: InputMaybe<Scalars["Int"]["input"]>;
  offset?: InputMaybe<Scalars["Int"]["input"]>;
  orderBy?: InputMaybe<Array<LightingGroupsOrderBy>>;
  where?: InputMaybe<LightingGroupsBoolExp>;
};

/** columns and relationships of "rooms" */
export type RoomsLightingGroupsAggregateArgs = {
  distinctOn?: InputMaybe<Array<LightingGroupsSelectColumn>>;
  limit?: InputMaybe<Scalars["Int"]["input"]>;
  offset?: InputMaybe<Scalars["Int"]["input"]>;
  orderBy?: InputMaybe<Array<LightingGroupsOrderBy>>;
  where?: InputMaybe<LightingGroupsBoolExp>;
};

/** aggregated selection of "rooms" */
export type RoomsAggregate = {
  __typename?: "RoomsAggregate";
  aggregate?: Maybe<RoomsAggregateFields>;
  nodes: Array<Rooms>;
};

/** aggregate fields of "rooms" */
export type RoomsAggregateFields = {
  __typename?: "RoomsAggregateFields";
  avg?: Maybe<RoomsAvgFields>;
  count: Scalars["Int"]["output"];
  max?: Maybe<RoomsMaxFields>;
  min?: Maybe<RoomsMinFields>;
  stddev?: Maybe<RoomsStddevFields>;
  stddevPop?: Maybe<RoomsStddevPopFields>;
  stddevSamp?: Maybe<RoomsStddevSampFields>;
  sum?: Maybe<RoomsSumFields>;
  varPop?: Maybe<RoomsVarPopFields>;
  varSamp?: Maybe<RoomsVarSampFields>;
  variance?: Maybe<RoomsVarianceFields>;
};

/** aggregate fields of "rooms" */
export type RoomsAggregateFieldsCountArgs = {
  columns?: InputMaybe<Array<RoomsSelectColumn>>;
  distinct?: InputMaybe<Scalars["Boolean"]["input"]>;
};

/** aggregate avg on columns */
export type RoomsAvgFields = {
  __typename?: "RoomsAvgFields";
  actualHumidity?: Maybe<Scalars["Float"]["output"]>;
  actualTemperature?: Maybe<Scalars["Float"]["output"]>;
  temperatureSetpoint?: Maybe<Scalars["Float"]["output"]>;
  thermalComfortIndex?: Maybe<Scalars["Float"]["output"]>;
};

/** Boolean expression to filter rows from the table "rooms". All fields are combined with a logical 'AND'. */
export type RoomsBoolExp = {
  _and?: InputMaybe<Array<RoomsBoolExp>>;
  _not?: InputMaybe<RoomsBoolExp>;
  _or?: InputMaybe<Array<RoomsBoolExp>>;
  actualHumidity?: InputMaybe<FloatComparisonExp>;
  actualTemperature?: InputMaybe<FloatComparisonExp>;
  amplifierOn?: InputMaybe<BooleanComparisonExp>;
  blinds?: InputMaybe<BlindsBoolExp>;
  blindsAggregate?: InputMaybe<BlindsAggregateBoolExp>;
  group?: InputMaybe<StringComparisonExp>;
  id?: InputMaybe<StringComparisonExp>;
  lastMovement?: InputMaybe<TimestamptzComparisonExp>;
  lightingGroups?: InputMaybe<LightingGroupsBoolExp>;
  lightingGroupsAggregate?: InputMaybe<LightingGroupsAggregateBoolExp>;
  name?: InputMaybe<StringComparisonExp>;
  temperatureSetpoint?: InputMaybe<FloatComparisonExp>;
  thermalComfortIndex?: InputMaybe<FloatComparisonExp>;
};

/** aggregate max on columns */
export type RoomsMaxFields = {
  __typename?: "RoomsMaxFields";
  actualHumidity?: Maybe<Scalars["Float"]["output"]>;
  actualTemperature?: Maybe<Scalars["Float"]["output"]>;
  group?: Maybe<Scalars["String"]["output"]>;
  id?: Maybe<Scalars["String"]["output"]>;
  lastMovement?: Maybe<Scalars["timestamptz"]["output"]>;
  name?: Maybe<Scalars["String"]["output"]>;
  temperatureSetpoint?: Maybe<Scalars["Float"]["output"]>;
  thermalComfortIndex?: Maybe<Scalars["Float"]["output"]>;
};

/** aggregate min on columns */
export type RoomsMinFields = {
  __typename?: "RoomsMinFields";
  actualHumidity?: Maybe<Scalars["Float"]["output"]>;
  actualTemperature?: Maybe<Scalars["Float"]["output"]>;
  group?: Maybe<Scalars["String"]["output"]>;
  id?: Maybe<Scalars["String"]["output"]>;
  lastMovement?: Maybe<Scalars["timestamptz"]["output"]>;
  name?: Maybe<Scalars["String"]["output"]>;
  temperatureSetpoint?: Maybe<Scalars["Float"]["output"]>;
  thermalComfortIndex?: Maybe<Scalars["Float"]["output"]>;
};

/** Ordering options when selecting data from "rooms". */
export type RoomsOrderBy = {
  actualHumidity?: InputMaybe<OrderBy>;
  actualTemperature?: InputMaybe<OrderBy>;
  amplifierOn?: InputMaybe<OrderBy>;
  blindsAggregate?: InputMaybe<BlindsAggregateOrderBy>;
  group?: InputMaybe<OrderBy>;
  id?: InputMaybe<OrderBy>;
  lastMovement?: InputMaybe<OrderBy>;
  lightingGroupsAggregate?: InputMaybe<LightingGroupsAggregateOrderBy>;
  name?: InputMaybe<OrderBy>;
  temperatureSetpoint?: InputMaybe<OrderBy>;
  thermalComfortIndex?: InputMaybe<OrderBy>;
};

/** select columns of table "rooms" */
export enum RoomsSelectColumn {
  /** column name */
  ActualHumidity = "actualHumidity",
  /** column name */
  ActualTemperature = "actualTemperature",
  /** column name */
  AmplifierOn = "amplifierOn",
  /** column name */
  Group = "group",
  /** column name */
  Id = "id",
  /** column name */
  LastMovement = "lastMovement",
  /** column name */
  Name = "name",
  /** column name */
  TemperatureSetpoint = "temperatureSetpoint",
  /** column name */
  ThermalComfortIndex = "thermalComfortIndex",
}

/** aggregate stddev on columns */
export type RoomsStddevFields = {
  __typename?: "RoomsStddevFields";
  actualHumidity?: Maybe<Scalars["Float"]["output"]>;
  actualTemperature?: Maybe<Scalars["Float"]["output"]>;
  temperatureSetpoint?: Maybe<Scalars["Float"]["output"]>;
  thermalComfortIndex?: Maybe<Scalars["Float"]["output"]>;
};

/** aggregate stddevPop on columns */
export type RoomsStddevPopFields = {
  __typename?: "RoomsStddevPopFields";
  actualHumidity?: Maybe<Scalars["Float"]["output"]>;
  actualTemperature?: Maybe<Scalars["Float"]["output"]>;
  temperatureSetpoint?: Maybe<Scalars["Float"]["output"]>;
  thermalComfortIndex?: Maybe<Scalars["Float"]["output"]>;
};

/** aggregate stddevSamp on columns */
export type RoomsStddevSampFields = {
  __typename?: "RoomsStddevSampFields";
  actualHumidity?: Maybe<Scalars["Float"]["output"]>;
  actualTemperature?: Maybe<Scalars["Float"]["output"]>;
  temperatureSetpoint?: Maybe<Scalars["Float"]["output"]>;
  thermalComfortIndex?: Maybe<Scalars["Float"]["output"]>;
};

/** Streaming cursor of the table "rooms" */
export type RoomsStreamCursorInput = {
  /** Stream column input with initial value */
  initialValue: RoomsStreamCursorValueInput;
  /** cursor ordering */
  ordering?: InputMaybe<CursorOrdering>;
};

/** Initial value of the column from where the streaming should start */
export type RoomsStreamCursorValueInput = {
  actualHumidity?: InputMaybe<Scalars["Float"]["input"]>;
  actualTemperature?: InputMaybe<Scalars["Float"]["input"]>;
  amplifierOn?: InputMaybe<Scalars["Boolean"]["input"]>;
  group?: InputMaybe<Scalars["String"]["input"]>;
  id?: InputMaybe<Scalars["String"]["input"]>;
  lastMovement?: InputMaybe<Scalars["timestamptz"]["input"]>;
  name?: InputMaybe<Scalars["String"]["input"]>;
  temperatureSetpoint?: InputMaybe<Scalars["Float"]["input"]>;
  thermalComfortIndex?: InputMaybe<Scalars["Float"]["input"]>;
};

/** aggregate sum on columns */
export type RoomsSumFields = {
  __typename?: "RoomsSumFields";
  actualHumidity?: Maybe<Scalars["Float"]["output"]>;
  actualTemperature?: Maybe<Scalars["Float"]["output"]>;
  temperatureSetpoint?: Maybe<Scalars["Float"]["output"]>;
  thermalComfortIndex?: Maybe<Scalars["Float"]["output"]>;
};

/** aggregate varPop on columns */
export type RoomsVarPopFields = {
  __typename?: "RoomsVarPopFields";
  actualHumidity?: Maybe<Scalars["Float"]["output"]>;
  actualTemperature?: Maybe<Scalars["Float"]["output"]>;
  temperatureSetpoint?: Maybe<Scalars["Float"]["output"]>;
  thermalComfortIndex?: Maybe<Scalars["Float"]["output"]>;
};

/** aggregate varSamp on columns */
export type RoomsVarSampFields = {
  __typename?: "RoomsVarSampFields";
  actualHumidity?: Maybe<Scalars["Float"]["output"]>;
  actualTemperature?: Maybe<Scalars["Float"]["output"]>;
  temperatureSetpoint?: Maybe<Scalars["Float"]["output"]>;
  thermalComfortIndex?: Maybe<Scalars["Float"]["output"]>;
};

/** aggregate variance on columns */
export type RoomsVarianceFields = {
  __typename?: "RoomsVarianceFields";
  actualHumidity?: Maybe<Scalars["Float"]["output"]>;
  actualTemperature?: Maybe<Scalars["Float"]["output"]>;
  temperatureSetpoint?: Maybe<Scalars["Float"]["output"]>;
  thermalComfortIndex?: Maybe<Scalars["Float"]["output"]>;
};

/** Boolean expression to compare columns of type "String". All fields are combined with logical 'AND'. */
export type StringComparisonExp = {
  _eq?: InputMaybe<Scalars["String"]["input"]>;
  _gt?: InputMaybe<Scalars["String"]["input"]>;
  _gte?: InputMaybe<Scalars["String"]["input"]>;
  /** does the column match the given case-insensitive pattern */
  _ilike?: InputMaybe<Scalars["String"]["input"]>;
  _in?: InputMaybe<Array<Scalars["String"]["input"]>>;
  /** does the column match the given POSIX regular expression, case insensitive */
  _iregex?: InputMaybe<Scalars["String"]["input"]>;
  _isNull?: InputMaybe<Scalars["Boolean"]["input"]>;
  /** does the column match the given pattern */
  _like?: InputMaybe<Scalars["String"]["input"]>;
  _lt?: InputMaybe<Scalars["String"]["input"]>;
  _lte?: InputMaybe<Scalars["String"]["input"]>;
  _neq?: InputMaybe<Scalars["String"]["input"]>;
  /** does the column NOT match the given case-insensitive pattern */
  _nilike?: InputMaybe<Scalars["String"]["input"]>;
  _nin?: InputMaybe<Array<Scalars["String"]["input"]>>;
  /** does the column NOT match the given POSIX regular expression, case insensitive */
  _niregex?: InputMaybe<Scalars["String"]["input"]>;
  /** does the column NOT match the given pattern */
  _nlike?: InputMaybe<Scalars["String"]["input"]>;
  /** does the column NOT match the given POSIX regular expression, case sensitive */
  _nregex?: InputMaybe<Scalars["String"]["input"]>;
  /** does the column NOT match the given SQL regular expression */
  _nsimilar?: InputMaybe<Scalars["String"]["input"]>;
  /** does the column match the given POSIX regular expression, case sensitive */
  _regex?: InputMaybe<Scalars["String"]["input"]>;
  /** does the column match the given SQL regular expression */
  _similar?: InputMaybe<Scalars["String"]["input"]>;
};

/** Boolean expression to compare columns of type "timestamptz". All fields are combined with logical 'AND'. */
export type TimestamptzComparisonExp = {
  _eq?: InputMaybe<Scalars["timestamptz"]["input"]>;
  _gt?: InputMaybe<Scalars["timestamptz"]["input"]>;
  _gte?: InputMaybe<Scalars["timestamptz"]["input"]>;
  _in?: InputMaybe<Array<Scalars["timestamptz"]["input"]>>;
  _isNull?: InputMaybe<Scalars["Boolean"]["input"]>;
  _lt?: InputMaybe<Scalars["timestamptz"]["input"]>;
  _lte?: InputMaybe<Scalars["timestamptz"]["input"]>;
  _neq?: InputMaybe<Scalars["timestamptz"]["input"]>;
  _nin?: InputMaybe<Array<Scalars["timestamptz"]["input"]>>;
};

export type BlindsAggregateBoolExpCount = {
  arguments?: InputMaybe<Array<BlindsSelectColumn>>;
  distinct?: InputMaybe<Scalars["Boolean"]["input"]>;
  filter?: InputMaybe<BlindsBoolExp>;
  predicate: IntComparisonExp;
};

export type LightingGroupsAggregateBoolExpCount = {
  arguments?: InputMaybe<Array<LightingGroupsSelectColumn>>;
  distinct?: InputMaybe<Scalars["Boolean"]["input"]>;
  filter?: InputMaybe<LightingGroupsBoolExp>;
  predicate: IntComparisonExp;
};

/** mutation root */
export type MutationRoot = {
  __typename?: "mutation_root";
  setAmplifier?: Maybe<Scalars["Void"]["output"]>;
  setBlind?: Maybe<Scalars["Void"]["output"]>;
  setLightingGroup?: Maybe<Scalars["Void"]["output"]>;
  setLightingGroups?: Maybe<Scalars["Void"]["output"]>;
  setRoomTemperatureSetpoint?: Maybe<Scalars["Void"]["output"]>;
};

/** mutation root */
export type MutationRootSetAmplifierArgs = {
  id: Scalars["ID"]["input"];
  on: Scalars["Boolean"]["input"];
};

/** mutation root */
export type MutationRootSetBlindArgs = {
  id: Scalars["ID"]["input"];
  level: Scalars["Float"]["input"];
};

/** mutation root */
export type MutationRootSetLightingGroupArgs = {
  id: Scalars["ID"]["input"];
  level: Scalars["Float"]["input"];
};

/** mutation root */
export type MutationRootSetLightingGroupsArgs = {
  ids: Array<Scalars["ID"]["input"]>;
  level: Scalars["Float"]["input"];
};

/** mutation root */
export type MutationRootSetRoomTemperatureSetpointArgs = {
  id: Scalars["ID"]["input"];
  temperature: Scalars["Int"]["input"];
};

export type QueryRoot = {
  __typename?: "query_root";
  /** fetch data from the table: "blinds" */
  blinds: Array<Blinds>;
  /** fetch aggregated fields from the table: "blinds" */
  blindsAggregate: BlindsAggregate;
  /** fetch data from the table: "blinds" using primary key columns */
  blindsByPk?: Maybe<Blinds>;
  /** An array relationship */
  lightingGroups: Array<LightingGroups>;
  /** An aggregate relationship */
  lightingGroupsAggregate: LightingGroupsAggregate;
  /** fetch data from the table: "lighting_groups" using primary key columns */
  lightingGroupsByPk?: Maybe<LightingGroups>;
  /** fetch data from the table: "rooms" */
  rooms: Array<Rooms>;
  /** fetch aggregated fields from the table: "rooms" */
  roomsAggregate: RoomsAggregate;
  /** fetch data from the table: "rooms" using primary key columns */
  roomsByPk?: Maybe<Rooms>;
  version: Scalars["String"]["output"];
};

export type QueryRootBlindsArgs = {
  distinctOn?: InputMaybe<Array<BlindsSelectColumn>>;
  limit?: InputMaybe<Scalars["Int"]["input"]>;
  offset?: InputMaybe<Scalars["Int"]["input"]>;
  orderBy?: InputMaybe<Array<BlindsOrderBy>>;
  where?: InputMaybe<BlindsBoolExp>;
};

export type QueryRootBlindsAggregateArgs = {
  distinctOn?: InputMaybe<Array<BlindsSelectColumn>>;
  limit?: InputMaybe<Scalars["Int"]["input"]>;
  offset?: InputMaybe<Scalars["Int"]["input"]>;
  orderBy?: InputMaybe<Array<BlindsOrderBy>>;
  where?: InputMaybe<BlindsBoolExp>;
};

export type QueryRootBlindsByPkArgs = {
  id: Scalars["String"]["input"];
};

export type QueryRootLightingGroupsArgs = {
  distinctOn?: InputMaybe<Array<LightingGroupsSelectColumn>>;
  limit?: InputMaybe<Scalars["Int"]["input"]>;
  offset?: InputMaybe<Scalars["Int"]["input"]>;
  orderBy?: InputMaybe<Array<LightingGroupsOrderBy>>;
  where?: InputMaybe<LightingGroupsBoolExp>;
};

export type QueryRootLightingGroupsAggregateArgs = {
  distinctOn?: InputMaybe<Array<LightingGroupsSelectColumn>>;
  limit?: InputMaybe<Scalars["Int"]["input"]>;
  offset?: InputMaybe<Scalars["Int"]["input"]>;
  orderBy?: InputMaybe<Array<LightingGroupsOrderBy>>;
  where?: InputMaybe<LightingGroupsBoolExp>;
};

export type QueryRootLightingGroupsByPkArgs = {
  id: Scalars["String"]["input"];
};

export type QueryRootRoomsArgs = {
  distinctOn?: InputMaybe<Array<RoomsSelectColumn>>;
  limit?: InputMaybe<Scalars["Int"]["input"]>;
  offset?: InputMaybe<Scalars["Int"]["input"]>;
  orderBy?: InputMaybe<Array<RoomsOrderBy>>;
  where?: InputMaybe<RoomsBoolExp>;
};

export type QueryRootRoomsAggregateArgs = {
  distinctOn?: InputMaybe<Array<RoomsSelectColumn>>;
  limit?: InputMaybe<Scalars["Int"]["input"]>;
  offset?: InputMaybe<Scalars["Int"]["input"]>;
  orderBy?: InputMaybe<Array<RoomsOrderBy>>;
  where?: InputMaybe<RoomsBoolExp>;
};

export type QueryRootRoomsByPkArgs = {
  id: Scalars["String"]["input"];
};

export type SubscriptionRoot = {
  __typename?: "subscription_root";
  /** fetch data from the table: "blinds" */
  blinds: Array<Blinds>;
  /** fetch aggregated fields from the table: "blinds" */
  blindsAggregate: BlindsAggregate;
  /** fetch data from the table: "blinds" using primary key columns */
  blindsByPk?: Maybe<Blinds>;
  /** fetch data from the table in a streaming manner: "blinds" */
  blindsStream: Array<Blinds>;
  /** An array relationship */
  lightingGroups: Array<LightingGroups>;
  /** An aggregate relationship */
  lightingGroupsAggregate: LightingGroupsAggregate;
  /** fetch data from the table: "lighting_groups" using primary key columns */
  lightingGroupsByPk?: Maybe<LightingGroups>;
  /** fetch data from the table in a streaming manner: "lighting_groups" */
  lightingGroupsStream: Array<LightingGroups>;
  /** fetch data from the table: "rooms" */
  rooms: Array<Rooms>;
  /** fetch aggregated fields from the table: "rooms" */
  roomsAggregate: RoomsAggregate;
  /** fetch data from the table: "rooms" using primary key columns */
  roomsByPk?: Maybe<Rooms>;
  /** fetch data from the table in a streaming manner: "rooms" */
  roomsStream: Array<Rooms>;
};

export type SubscriptionRootBlindsArgs = {
  distinctOn?: InputMaybe<Array<BlindsSelectColumn>>;
  limit?: InputMaybe<Scalars["Int"]["input"]>;
  offset?: InputMaybe<Scalars["Int"]["input"]>;
  orderBy?: InputMaybe<Array<BlindsOrderBy>>;
  where?: InputMaybe<BlindsBoolExp>;
};

export type SubscriptionRootBlindsAggregateArgs = {
  distinctOn?: InputMaybe<Array<BlindsSelectColumn>>;
  limit?: InputMaybe<Scalars["Int"]["input"]>;
  offset?: InputMaybe<Scalars["Int"]["input"]>;
  orderBy?: InputMaybe<Array<BlindsOrderBy>>;
  where?: InputMaybe<BlindsBoolExp>;
};

export type SubscriptionRootBlindsByPkArgs = {
  id: Scalars["String"]["input"];
};

export type SubscriptionRootBlindsStreamArgs = {
  batchSize: Scalars["Int"]["input"];
  cursor: Array<InputMaybe<BlindsStreamCursorInput>>;
  where?: InputMaybe<BlindsBoolExp>;
};

export type SubscriptionRootLightingGroupsArgs = {
  distinctOn?: InputMaybe<Array<LightingGroupsSelectColumn>>;
  limit?: InputMaybe<Scalars["Int"]["input"]>;
  offset?: InputMaybe<Scalars["Int"]["input"]>;
  orderBy?: InputMaybe<Array<LightingGroupsOrderBy>>;
  where?: InputMaybe<LightingGroupsBoolExp>;
};

export type SubscriptionRootLightingGroupsAggregateArgs = {
  distinctOn?: InputMaybe<Array<LightingGroupsSelectColumn>>;
  limit?: InputMaybe<Scalars["Int"]["input"]>;
  offset?: InputMaybe<Scalars["Int"]["input"]>;
  orderBy?: InputMaybe<Array<LightingGroupsOrderBy>>;
  where?: InputMaybe<LightingGroupsBoolExp>;
};

export type SubscriptionRootLightingGroupsByPkArgs = {
  id: Scalars["String"]["input"];
};

export type SubscriptionRootLightingGroupsStreamArgs = {
  batchSize: Scalars["Int"]["input"];
  cursor: Array<InputMaybe<LightingGroupsStreamCursorInput>>;
  where?: InputMaybe<LightingGroupsBoolExp>;
};

export type SubscriptionRootRoomsArgs = {
  distinctOn?: InputMaybe<Array<RoomsSelectColumn>>;
  limit?: InputMaybe<Scalars["Int"]["input"]>;
  offset?: InputMaybe<Scalars["Int"]["input"]>;
  orderBy?: InputMaybe<Array<RoomsOrderBy>>;
  where?: InputMaybe<RoomsBoolExp>;
};

export type SubscriptionRootRoomsAggregateArgs = {
  distinctOn?: InputMaybe<Array<RoomsSelectColumn>>;
  limit?: InputMaybe<Scalars["Int"]["input"]>;
  offset?: InputMaybe<Scalars["Int"]["input"]>;
  orderBy?: InputMaybe<Array<RoomsOrderBy>>;
  where?: InputMaybe<RoomsBoolExp>;
};

export type SubscriptionRootRoomsByPkArgs = {
  id: Scalars["String"]["input"];
};

export type SubscriptionRootRoomsStreamArgs = {
  batchSize: Scalars["Int"]["input"];
  cursor: Array<InputMaybe<RoomsStreamCursorInput>>;
  where?: InputMaybe<RoomsBoolExp>;
};

export type BlindsItemFragment = {
  __typename?: "Blinds";
  id: string;
  name?: string | null;
  level: number;
  roomId?: string | null;
  opacity?: any | null;
  group?: string | null;
} & { " $fragmentName"?: "BlindsItemFragment" };

export type SetBlindsLevelMutationVariables = Exact<{
  id: Scalars["ID"]["input"];
  level: Scalars["Float"]["input"];
}>;

export type SetBlindsLevelMutation = { __typename?: "mutation_root"; setBlind?: any | null };

export type LightGroupItemFragment = {
  __typename?: "LightingGroups";
  id: string;
  name?: string | null;
  level: number;
  roomId?: string | null;
} & { " $fragmentName"?: "LightGroupItemFragment" };

export type GetLightGroupsByRoomSubscriptionVariables = Exact<{
  roomId: Scalars["String"]["input"];
}>;

export type GetLightGroupsByRoomSubscription = {
  __typename?: "subscription_root";
  lightingGroups: Array<
    { __typename?: "LightingGroups" } & {
      " $fragmentRefs"?: { LightGroupItemFragment: LightGroupItemFragment };
    }
  >;
};

export type SetLightLevelMutationVariables = Exact<{
  id: Scalars["ID"]["input"];
  level: Scalars["Float"]["input"];
}>;

export type SetLightLevelMutation = { __typename?: "mutation_root"; setLightingGroup?: any | null };

export type RoomItemFragment = {
  __typename?: "Rooms";
  id: string;
  amplifierOn?: boolean | null;
  actualTemperature?: number | null;
  actualHumidity?: number | null;
  temperatureSetpoint?: number | null;
  thermalComfortIndex?: number | null;
  name?: string | null;
  group?: string | null;
  lastMovement?: any | null;
} & { " $fragmentName"?: "RoomItemFragment" };

export type GetAllRoomsQueryVariables = Exact<{ [key: string]: never }>;

export type GetAllRoomsQuery = {
  __typename?: "query_root";
  rooms: Array<{ __typename?: "Rooms"; id: string; name?: string | null; group?: string | null }>;
};

export type SubscribeToRoomSubscriptionVariables = Exact<{
  roomId: Scalars["String"]["input"];
}>;

export type SubscribeToRoomSubscription = {
  __typename?: "subscription_root";
  rooms: Array<
    {
      __typename?: "Rooms";
      blinds: Array<
        { __typename?: "Blinds" } & {
          " $fragmentRefs"?: { BlindsItemFragment: BlindsItemFragment };
        }
      >;
      lightingGroups: Array<
        { __typename?: "LightingGroups" } & {
          " $fragmentRefs"?: { LightGroupItemFragment: LightGroupItemFragment };
        }
      >;
    } & { " $fragmentRefs"?: { RoomItemFragment: RoomItemFragment } }
  >;
};

export type GetRoomByIdQueryVariables = Exact<{
  roomId: Scalars["String"]["input"];
}>;

export type GetRoomByIdQuery = {
  __typename?: "query_root";
  rooms: Array<
    {
      __typename?: "Rooms";
      blinds: Array<
        { __typename?: "Blinds" } & {
          " $fragmentRefs"?: { BlindsItemFragment: BlindsItemFragment };
        }
      >;
      lightingGroups: Array<
        { __typename?: "LightingGroups" } & {
          " $fragmentRefs"?: { LightGroupItemFragment: LightGroupItemFragment };
        }
      >;
    } & { " $fragmentRefs"?: { RoomItemFragment: RoomItemFragment } }
  >;
};

export type SetTemperatureSetpointMutationVariables = Exact<{
  id: Scalars["ID"]["input"];
  temperature: Scalars["Int"]["input"];
}>;

export type SetTemperatureSetpointMutation = {
  __typename?: "mutation_root";
  setRoomTemperatureSetpoint?: any | null;
};

export type SetAmplifierMutationVariables = Exact<{
  id: Scalars["ID"]["input"];
  on: Scalars["Boolean"]["input"];
}>;

export type SetAmplifierMutation = { __typename?: "mutation_root"; setAmplifier?: any | null };

export const BlindsItemFragmentDoc = {
  kind: "Document",
  definitions: [
    {
      kind: "FragmentDefinition",
      name: { kind: "Name", value: "BlindsItem" },
      typeCondition: { kind: "NamedType", name: { kind: "Name", value: "Blinds" } },
      selectionSet: {
        kind: "SelectionSet",
        selections: [
          { kind: "Field", name: { kind: "Name", value: "id" } },
          { kind: "Field", name: { kind: "Name", value: "name" } },
          { kind: "Field", name: { kind: "Name", value: "level" } },
          { kind: "Field", name: { kind: "Name", value: "roomId" } },
          { kind: "Field", name: { kind: "Name", value: "opacity" } },
          { kind: "Field", name: { kind: "Name", value: "group" } },
        ],
      },
    },
  ],
} as unknown as DocumentNode<BlindsItemFragment, unknown>;
export const LightGroupItemFragmentDoc = {
  kind: "Document",
  definitions: [
    {
      kind: "FragmentDefinition",
      name: { kind: "Name", value: "LightGroupItem" },
      typeCondition: { kind: "NamedType", name: { kind: "Name", value: "LightingGroups" } },
      selectionSet: {
        kind: "SelectionSet",
        selections: [
          { kind: "Field", name: { kind: "Name", value: "id" } },
          { kind: "Field", name: { kind: "Name", value: "name" } },
          { kind: "Field", name: { kind: "Name", value: "level" } },
          { kind: "Field", name: { kind: "Name", value: "roomId" } },
        ],
      },
    },
  ],
} as unknown as DocumentNode<LightGroupItemFragment, unknown>;
export const RoomItemFragmentDoc = {
  kind: "Document",
  definitions: [
    {
      kind: "FragmentDefinition",
      name: { kind: "Name", value: "RoomItem" },
      typeCondition: { kind: "NamedType", name: { kind: "Name", value: "Rooms" } },
      selectionSet: {
        kind: "SelectionSet",
        selections: [
          { kind: "Field", name: { kind: "Name", value: "id" } },
          { kind: "Field", name: { kind: "Name", value: "amplifierOn" } },
          { kind: "Field", name: { kind: "Name", value: "actualTemperature" } },
          { kind: "Field", name: { kind: "Name", value: "actualHumidity" } },
          { kind: "Field", name: { kind: "Name", value: "temperatureSetpoint" } },
          { kind: "Field", name: { kind: "Name", value: "thermalComfortIndex" } },
          { kind: "Field", name: { kind: "Name", value: "name" } },
          { kind: "Field", name: { kind: "Name", value: "group" } },
          { kind: "Field", name: { kind: "Name", value: "lastMovement" } },
        ],
      },
    },
  ],
} as unknown as DocumentNode<RoomItemFragment, unknown>;
export const SetBlindsLevelDocument = {
  kind: "Document",
  definitions: [
    {
      kind: "OperationDefinition",
      operation: "mutation",
      name: { kind: "Name", value: "SetBlindsLevel" },
      variableDefinitions: [
        {
          kind: "VariableDefinition",
          variable: { kind: "Variable", name: { kind: "Name", value: "id" } },
          type: {
            kind: "NonNullType",
            type: { kind: "NamedType", name: { kind: "Name", value: "ID" } },
          },
        },
        {
          kind: "VariableDefinition",
          variable: { kind: "Variable", name: { kind: "Name", value: "level" } },
          type: {
            kind: "NonNullType",
            type: { kind: "NamedType", name: { kind: "Name", value: "Float" } },
          },
        },
      ],
      selectionSet: {
        kind: "SelectionSet",
        selections: [
          {
            kind: "Field",
            name: { kind: "Name", value: "setBlind" },
            arguments: [
              {
                kind: "Argument",
                name: { kind: "Name", value: "id" },
                value: { kind: "Variable", name: { kind: "Name", value: "id" } },
              },
              {
                kind: "Argument",
                name: { kind: "Name", value: "level" },
                value: { kind: "Variable", name: { kind: "Name", value: "level" } },
              },
            ],
          },
        ],
      },
    },
  ],
} as unknown as DocumentNode<SetBlindsLevelMutation, SetBlindsLevelMutationVariables>;
export const GetLightGroupsByRoomDocument = {
  kind: "Document",
  definitions: [
    {
      kind: "OperationDefinition",
      operation: "subscription",
      name: { kind: "Name", value: "GetLightGroupsByRoom" },
      variableDefinitions: [
        {
          kind: "VariableDefinition",
          variable: { kind: "Variable", name: { kind: "Name", value: "roomId" } },
          type: {
            kind: "NonNullType",
            type: { kind: "NamedType", name: { kind: "Name", value: "String" } },
          },
        },
      ],
      selectionSet: {
        kind: "SelectionSet",
        selections: [
          {
            kind: "Field",
            name: { kind: "Name", value: "lightingGroups" },
            arguments: [
              {
                kind: "Argument",
                name: { kind: "Name", value: "where" },
                value: {
                  kind: "ObjectValue",
                  fields: [
                    {
                      kind: "ObjectField",
                      name: { kind: "Name", value: "roomId" },
                      value: {
                        kind: "ObjectValue",
                        fields: [
                          {
                            kind: "ObjectField",
                            name: { kind: "Name", value: "_eq" },
                            value: { kind: "Variable", name: { kind: "Name", value: "roomId" } },
                          },
                        ],
                      },
                    },
                  ],
                },
              },
            ],
            selectionSet: {
              kind: "SelectionSet",
              selections: [
                { kind: "FragmentSpread", name: { kind: "Name", value: "LightGroupItem" } },
              ],
            },
          },
        ],
      },
    },
    {
      kind: "FragmentDefinition",
      name: { kind: "Name", value: "LightGroupItem" },
      typeCondition: { kind: "NamedType", name: { kind: "Name", value: "LightingGroups" } },
      selectionSet: {
        kind: "SelectionSet",
        selections: [
          { kind: "Field", name: { kind: "Name", value: "id" } },
          { kind: "Field", name: { kind: "Name", value: "name" } },
          { kind: "Field", name: { kind: "Name", value: "level" } },
          { kind: "Field", name: { kind: "Name", value: "roomId" } },
        ],
      },
    },
  ],
} as unknown as DocumentNode<
  GetLightGroupsByRoomSubscription,
  GetLightGroupsByRoomSubscriptionVariables
>;
export const SetLightLevelDocument = {
  kind: "Document",
  definitions: [
    {
      kind: "OperationDefinition",
      operation: "mutation",
      name: { kind: "Name", value: "SetLightLevel" },
      variableDefinitions: [
        {
          kind: "VariableDefinition",
          variable: { kind: "Variable", name: { kind: "Name", value: "id" } },
          type: {
            kind: "NonNullType",
            type: { kind: "NamedType", name: { kind: "Name", value: "ID" } },
          },
        },
        {
          kind: "VariableDefinition",
          variable: { kind: "Variable", name: { kind: "Name", value: "level" } },
          type: {
            kind: "NonNullType",
            type: { kind: "NamedType", name: { kind: "Name", value: "Float" } },
          },
        },
      ],
      selectionSet: {
        kind: "SelectionSet",
        selections: [
          {
            kind: "Field",
            name: { kind: "Name", value: "setLightingGroup" },
            arguments: [
              {
                kind: "Argument",
                name: { kind: "Name", value: "id" },
                value: { kind: "Variable", name: { kind: "Name", value: "id" } },
              },
              {
                kind: "Argument",
                name: { kind: "Name", value: "level" },
                value: { kind: "Variable", name: { kind: "Name", value: "level" } },
              },
            ],
          },
        ],
      },
    },
  ],
} as unknown as DocumentNode<SetLightLevelMutation, SetLightLevelMutationVariables>;
export const GetAllRoomsDocument = {
  kind: "Document",
  definitions: [
    {
      kind: "OperationDefinition",
      operation: "query",
      name: { kind: "Name", value: "GetAllRooms" },
      selectionSet: {
        kind: "SelectionSet",
        selections: [
          {
            kind: "Field",
            name: { kind: "Name", value: "rooms" },
            selectionSet: {
              kind: "SelectionSet",
              selections: [
                { kind: "Field", name: { kind: "Name", value: "id" } },
                { kind: "Field", name: { kind: "Name", value: "name" } },
                { kind: "Field", name: { kind: "Name", value: "group" } },
              ],
            },
          },
        ],
      },
    },
  ],
} as unknown as DocumentNode<GetAllRoomsQuery, GetAllRoomsQueryVariables>;
export const SubscribeToRoomDocument = {
  kind: "Document",
  definitions: [
    {
      kind: "OperationDefinition",
      operation: "subscription",
      name: { kind: "Name", value: "SubscribeToRoom" },
      variableDefinitions: [
        {
          kind: "VariableDefinition",
          variable: { kind: "Variable", name: { kind: "Name", value: "roomId" } },
          type: {
            kind: "NonNullType",
            type: { kind: "NamedType", name: { kind: "Name", value: "String" } },
          },
        },
      ],
      selectionSet: {
        kind: "SelectionSet",
        selections: [
          {
            kind: "Field",
            name: { kind: "Name", value: "rooms" },
            arguments: [
              {
                kind: "Argument",
                name: { kind: "Name", value: "where" },
                value: {
                  kind: "ObjectValue",
                  fields: [
                    {
                      kind: "ObjectField",
                      name: { kind: "Name", value: "id" },
                      value: {
                        kind: "ObjectValue",
                        fields: [
                          {
                            kind: "ObjectField",
                            name: { kind: "Name", value: "_eq" },
                            value: { kind: "Variable", name: { kind: "Name", value: "roomId" } },
                          },
                        ],
                      },
                    },
                  ],
                },
              },
            ],
            selectionSet: {
              kind: "SelectionSet",
              selections: [
                { kind: "FragmentSpread", name: { kind: "Name", value: "RoomItem" } },
                {
                  kind: "Field",
                  name: { kind: "Name", value: "blinds" },
                  selectionSet: {
                    kind: "SelectionSet",
                    selections: [
                      { kind: "FragmentSpread", name: { kind: "Name", value: "BlindsItem" } },
                    ],
                  },
                },
                {
                  kind: "Field",
                  name: { kind: "Name", value: "lightingGroups" },
                  selectionSet: {
                    kind: "SelectionSet",
                    selections: [
                      { kind: "FragmentSpread", name: { kind: "Name", value: "LightGroupItem" } },
                    ],
                  },
                },
              ],
            },
          },
        ],
      },
    },
    {
      kind: "FragmentDefinition",
      name: { kind: "Name", value: "RoomItem" },
      typeCondition: { kind: "NamedType", name: { kind: "Name", value: "Rooms" } },
      selectionSet: {
        kind: "SelectionSet",
        selections: [
          { kind: "Field", name: { kind: "Name", value: "id" } },
          { kind: "Field", name: { kind: "Name", value: "amplifierOn" } },
          { kind: "Field", name: { kind: "Name", value: "actualTemperature" } },
          { kind: "Field", name: { kind: "Name", value: "actualHumidity" } },
          { kind: "Field", name: { kind: "Name", value: "temperatureSetpoint" } },
          { kind: "Field", name: { kind: "Name", value: "thermalComfortIndex" } },
          { kind: "Field", name: { kind: "Name", value: "name" } },
          { kind: "Field", name: { kind: "Name", value: "group" } },
          { kind: "Field", name: { kind: "Name", value: "lastMovement" } },
        ],
      },
    },
    {
      kind: "FragmentDefinition",
      name: { kind: "Name", value: "BlindsItem" },
      typeCondition: { kind: "NamedType", name: { kind: "Name", value: "Blinds" } },
      selectionSet: {
        kind: "SelectionSet",
        selections: [
          { kind: "Field", name: { kind: "Name", value: "id" } },
          { kind: "Field", name: { kind: "Name", value: "name" } },
          { kind: "Field", name: { kind: "Name", value: "level" } },
          { kind: "Field", name: { kind: "Name", value: "roomId" } },
          { kind: "Field", name: { kind: "Name", value: "opacity" } },
          { kind: "Field", name: { kind: "Name", value: "group" } },
        ],
      },
    },
    {
      kind: "FragmentDefinition",
      name: { kind: "Name", value: "LightGroupItem" },
      typeCondition: { kind: "NamedType", name: { kind: "Name", value: "LightingGroups" } },
      selectionSet: {
        kind: "SelectionSet",
        selections: [
          { kind: "Field", name: { kind: "Name", value: "id" } },
          { kind: "Field", name: { kind: "Name", value: "name" } },
          { kind: "Field", name: { kind: "Name", value: "level" } },
          { kind: "Field", name: { kind: "Name", value: "roomId" } },
        ],
      },
    },
  ],
} as unknown as DocumentNode<SubscribeToRoomSubscription, SubscribeToRoomSubscriptionVariables>;
export const GetRoomByIdDocument = {
  kind: "Document",
  definitions: [
    {
      kind: "OperationDefinition",
      operation: "query",
      name: { kind: "Name", value: "GetRoomById" },
      variableDefinitions: [
        {
          kind: "VariableDefinition",
          variable: { kind: "Variable", name: { kind: "Name", value: "roomId" } },
          type: {
            kind: "NonNullType",
            type: { kind: "NamedType", name: { kind: "Name", value: "String" } },
          },
        },
      ],
      selectionSet: {
        kind: "SelectionSet",
        selections: [
          {
            kind: "Field",
            name: { kind: "Name", value: "rooms" },
            arguments: [
              {
                kind: "Argument",
                name: { kind: "Name", value: "where" },
                value: {
                  kind: "ObjectValue",
                  fields: [
                    {
                      kind: "ObjectField",
                      name: { kind: "Name", value: "id" },
                      value: {
                        kind: "ObjectValue",
                        fields: [
                          {
                            kind: "ObjectField",
                            name: { kind: "Name", value: "_eq" },
                            value: { kind: "Variable", name: { kind: "Name", value: "roomId" } },
                          },
                        ],
                      },
                    },
                  ],
                },
              },
            ],
            selectionSet: {
              kind: "SelectionSet",
              selections: [
                { kind: "FragmentSpread", name: { kind: "Name", value: "RoomItem" } },
                {
                  kind: "Field",
                  name: { kind: "Name", value: "blinds" },
                  selectionSet: {
                    kind: "SelectionSet",
                    selections: [
                      { kind: "FragmentSpread", name: { kind: "Name", value: "BlindsItem" } },
                    ],
                  },
                },
                {
                  kind: "Field",
                  name: { kind: "Name", value: "lightingGroups" },
                  selectionSet: {
                    kind: "SelectionSet",
                    selections: [
                      { kind: "FragmentSpread", name: { kind: "Name", value: "LightGroupItem" } },
                    ],
                  },
                },
              ],
            },
          },
        ],
      },
    },
    {
      kind: "FragmentDefinition",
      name: { kind: "Name", value: "RoomItem" },
      typeCondition: { kind: "NamedType", name: { kind: "Name", value: "Rooms" } },
      selectionSet: {
        kind: "SelectionSet",
        selections: [
          { kind: "Field", name: { kind: "Name", value: "id" } },
          { kind: "Field", name: { kind: "Name", value: "amplifierOn" } },
          { kind: "Field", name: { kind: "Name", value: "actualTemperature" } },
          { kind: "Field", name: { kind: "Name", value: "actualHumidity" } },
          { kind: "Field", name: { kind: "Name", value: "temperatureSetpoint" } },
          { kind: "Field", name: { kind: "Name", value: "thermalComfortIndex" } },
          { kind: "Field", name: { kind: "Name", value: "name" } },
          { kind: "Field", name: { kind: "Name", value: "group" } },
          { kind: "Field", name: { kind: "Name", value: "lastMovement" } },
        ],
      },
    },
    {
      kind: "FragmentDefinition",
      name: { kind: "Name", value: "BlindsItem" },
      typeCondition: { kind: "NamedType", name: { kind: "Name", value: "Blinds" } },
      selectionSet: {
        kind: "SelectionSet",
        selections: [
          { kind: "Field", name: { kind: "Name", value: "id" } },
          { kind: "Field", name: { kind: "Name", value: "name" } },
          { kind: "Field", name: { kind: "Name", value: "level" } },
          { kind: "Field", name: { kind: "Name", value: "roomId" } },
          { kind: "Field", name: { kind: "Name", value: "opacity" } },
          { kind: "Field", name: { kind: "Name", value: "group" } },
        ],
      },
    },
    {
      kind: "FragmentDefinition",
      name: { kind: "Name", value: "LightGroupItem" },
      typeCondition: { kind: "NamedType", name: { kind: "Name", value: "LightingGroups" } },
      selectionSet: {
        kind: "SelectionSet",
        selections: [
          { kind: "Field", name: { kind: "Name", value: "id" } },
          { kind: "Field", name: { kind: "Name", value: "name" } },
          { kind: "Field", name: { kind: "Name", value: "level" } },
          { kind: "Field", name: { kind: "Name", value: "roomId" } },
        ],
      },
    },
  ],
} as unknown as DocumentNode<GetRoomByIdQuery, GetRoomByIdQueryVariables>;
export const SetTemperatureSetpointDocument = {
  kind: "Document",
  definitions: [
    {
      kind: "OperationDefinition",
      operation: "mutation",
      name: { kind: "Name", value: "SetTemperatureSetpoint" },
      variableDefinitions: [
        {
          kind: "VariableDefinition",
          variable: { kind: "Variable", name: { kind: "Name", value: "id" } },
          type: {
            kind: "NonNullType",
            type: { kind: "NamedType", name: { kind: "Name", value: "ID" } },
          },
        },
        {
          kind: "VariableDefinition",
          variable: { kind: "Variable", name: { kind: "Name", value: "temperature" } },
          type: {
            kind: "NonNullType",
            type: { kind: "NamedType", name: { kind: "Name", value: "Int" } },
          },
        },
      ],
      selectionSet: {
        kind: "SelectionSet",
        selections: [
          {
            kind: "Field",
            name: { kind: "Name", value: "setRoomTemperatureSetpoint" },
            arguments: [
              {
                kind: "Argument",
                name: { kind: "Name", value: "id" },
                value: { kind: "Variable", name: { kind: "Name", value: "id" } },
              },
              {
                kind: "Argument",
                name: { kind: "Name", value: "temperature" },
                value: { kind: "Variable", name: { kind: "Name", value: "temperature" } },
              },
            ],
          },
        ],
      },
    },
  ],
} as unknown as DocumentNode<
  SetTemperatureSetpointMutation,
  SetTemperatureSetpointMutationVariables
>;
export const SetAmplifierDocument = {
  kind: "Document",
  definitions: [
    {
      kind: "OperationDefinition",
      operation: "mutation",
      name: { kind: "Name", value: "SetAmplifier" },
      variableDefinitions: [
        {
          kind: "VariableDefinition",
          variable: { kind: "Variable", name: { kind: "Name", value: "id" } },
          type: {
            kind: "NonNullType",
            type: { kind: "NamedType", name: { kind: "Name", value: "ID" } },
          },
        },
        {
          kind: "VariableDefinition",
          variable: { kind: "Variable", name: { kind: "Name", value: "on" } },
          type: {
            kind: "NonNullType",
            type: { kind: "NamedType", name: { kind: "Name", value: "Boolean" } },
          },
        },
      ],
      selectionSet: {
        kind: "SelectionSet",
        selections: [
          {
            kind: "Field",
            name: { kind: "Name", value: "setAmplifier" },
            arguments: [
              {
                kind: "Argument",
                name: { kind: "Name", value: "id" },
                value: { kind: "Variable", name: { kind: "Name", value: "id" } },
              },
              {
                kind: "Argument",
                name: { kind: "Name", value: "on" },
                value: { kind: "Variable", name: { kind: "Name", value: "on" } },
              },
            ],
          },
        ],
      },
    },
  ],
} as unknown as DocumentNode<SetAmplifierMutation, SetAmplifierMutationVariables>;
