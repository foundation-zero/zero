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

/** Boolean expression to compare columns of type "Boolean". All fields are combined with logical 'AND'. */
export type BooleanComparisonExp = {
  _eq?: InputMaybe<Scalars["Boolean"]["input"]>;
  _gt?: InputMaybe<Scalars["Boolean"]["input"]>;
  _gte?: InputMaybe<Scalars["Boolean"]["input"]>;
  _in?: InputMaybe<Array<Scalars["Boolean"]["input"]>>;
  _is_null?: InputMaybe<Scalars["Boolean"]["input"]>;
  _lt?: InputMaybe<Scalars["Boolean"]["input"]>;
  _lte?: InputMaybe<Scalars["Boolean"]["input"]>;
  _neq?: InputMaybe<Scalars["Boolean"]["input"]>;
  _nin?: InputMaybe<Array<Scalars["Boolean"]["input"]>>;
};

/** Boolean expression to compare columns of type "Float". All fields are combined with logical 'AND'. */
export type FloatComparisonExp = {
  _eq?: InputMaybe<Scalars["Float"]["input"]>;
  _gt?: InputMaybe<Scalars["Float"]["input"]>;
  _gte?: InputMaybe<Scalars["Float"]["input"]>;
  _in?: InputMaybe<Array<Scalars["Float"]["input"]>>;
  _is_null?: InputMaybe<Scalars["Boolean"]["input"]>;
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
  _is_null?: InputMaybe<Scalars["Boolean"]["input"]>;
  _lt?: InputMaybe<Scalars["Int"]["input"]>;
  _lte?: InputMaybe<Scalars["Int"]["input"]>;
  _neq?: InputMaybe<Scalars["Int"]["input"]>;
  _nin?: InputMaybe<Array<Scalars["Int"]["input"]>>;
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
  _is_null?: InputMaybe<Scalars["Boolean"]["input"]>;
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

/** Boolean expression to compare columns of type "blind_opacity". All fields are combined with logical 'AND'. */
export type BlindOpacityComparisonExp = {
  _eq?: InputMaybe<Scalars["blind_opacity"]["input"]>;
  _gt?: InputMaybe<Scalars["blind_opacity"]["input"]>;
  _gte?: InputMaybe<Scalars["blind_opacity"]["input"]>;
  _in?: InputMaybe<Array<Scalars["blind_opacity"]["input"]>>;
  _is_null?: InputMaybe<Scalars["Boolean"]["input"]>;
  _lt?: InputMaybe<Scalars["blind_opacity"]["input"]>;
  _lte?: InputMaybe<Scalars["blind_opacity"]["input"]>;
  _neq?: InputMaybe<Scalars["blind_opacity"]["input"]>;
  _nin?: InputMaybe<Array<Scalars["blind_opacity"]["input"]>>;
};

/** columns and relationships of "blinds" */
export type Blinds = {
  __typename?: "blinds";
  group: Scalars["String"]["output"];
  id: Scalars["String"]["output"];
  level: Scalars["Float"]["output"];
  name: Scalars["String"]["output"];
  opacity: Scalars["blind_opacity"]["output"];
  room_id?: Maybe<Scalars["String"]["output"]>;
};

/** aggregated selection of "blinds" */
export type BlindsAggregate = {
  __typename?: "blinds_aggregate";
  aggregate?: Maybe<BlindsAggregateFields>;
  nodes: Array<Blinds>;
};

export type BlindsAggregateBoolExp = {
  count?: InputMaybe<BlindsAggregateBoolExpCount>;
};

export type BlindsAggregateBoolExpCount = {
  arguments?: InputMaybe<Array<BlindsSelectColumn>>;
  distinct?: InputMaybe<Scalars["Boolean"]["input"]>;
  filter?: InputMaybe<BlindsBoolExp>;
  predicate: IntComparisonExp;
};

/** aggregate fields of "blinds" */
export type BlindsAggregateFields = {
  __typename?: "blinds_aggregate_fields";
  avg?: Maybe<BlindsAvgFields>;
  count: Scalars["Int"]["output"];
  max?: Maybe<BlindsMaxFields>;
  min?: Maybe<BlindsMinFields>;
  stddev?: Maybe<BlindsStddevFields>;
  stddev_pop?: Maybe<BlindsStddevPopFields>;
  stddev_samp?: Maybe<BlindsStddevSampFields>;
  sum?: Maybe<BlindsSumFields>;
  var_pop?: Maybe<BlindsVarPopFields>;
  var_samp?: Maybe<BlindsVarSampFields>;
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
  stddev_pop?: InputMaybe<BlindsStddevPopOrderBy>;
  stddev_samp?: InputMaybe<BlindsStddevSampOrderBy>;
  sum?: InputMaybe<BlindsSumOrderBy>;
  var_pop?: InputMaybe<BlindsVarPopOrderBy>;
  var_samp?: InputMaybe<BlindsVarSampOrderBy>;
  variance?: InputMaybe<BlindsVarianceOrderBy>;
};

/** aggregate avg on columns */
export type BlindsAvgFields = {
  __typename?: "blinds_avg_fields";
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
  room_id?: InputMaybe<StringComparisonExp>;
};

/** aggregate max on columns */
export type BlindsMaxFields = {
  __typename?: "blinds_max_fields";
  group?: Maybe<Scalars["String"]["output"]>;
  id?: Maybe<Scalars["String"]["output"]>;
  level?: Maybe<Scalars["Float"]["output"]>;
  name?: Maybe<Scalars["String"]["output"]>;
  opacity?: Maybe<Scalars["blind_opacity"]["output"]>;
  room_id?: Maybe<Scalars["String"]["output"]>;
};

/** order by max() on columns of table "blinds" */
export type BlindsMaxOrderBy = {
  group?: InputMaybe<OrderBy>;
  id?: InputMaybe<OrderBy>;
  level?: InputMaybe<OrderBy>;
  name?: InputMaybe<OrderBy>;
  opacity?: InputMaybe<OrderBy>;
  room_id?: InputMaybe<OrderBy>;
};

/** aggregate min on columns */
export type BlindsMinFields = {
  __typename?: "blinds_min_fields";
  group?: Maybe<Scalars["String"]["output"]>;
  id?: Maybe<Scalars["String"]["output"]>;
  level?: Maybe<Scalars["Float"]["output"]>;
  name?: Maybe<Scalars["String"]["output"]>;
  opacity?: Maybe<Scalars["blind_opacity"]["output"]>;
  room_id?: Maybe<Scalars["String"]["output"]>;
};

/** order by min() on columns of table "blinds" */
export type BlindsMinOrderBy = {
  group?: InputMaybe<OrderBy>;
  id?: InputMaybe<OrderBy>;
  level?: InputMaybe<OrderBy>;
  name?: InputMaybe<OrderBy>;
  opacity?: InputMaybe<OrderBy>;
  room_id?: InputMaybe<OrderBy>;
};

/** Ordering options when selecting data from "blinds". */
export type BlindsOrderBy = {
  group?: InputMaybe<OrderBy>;
  id?: InputMaybe<OrderBy>;
  level?: InputMaybe<OrderBy>;
  name?: InputMaybe<OrderBy>;
  opacity?: InputMaybe<OrderBy>;
  room_id?: InputMaybe<OrderBy>;
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
  RoomId = "room_id",
}

/** aggregate stddev on columns */
export type BlindsStddevFields = {
  __typename?: "blinds_stddev_fields";
  level?: Maybe<Scalars["Float"]["output"]>;
};

/** order by stddev() on columns of table "blinds" */
export type BlindsStddevOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** aggregate stddev_pop on columns */
export type BlindsStddevPopFields = {
  __typename?: "blinds_stddev_pop_fields";
  level?: Maybe<Scalars["Float"]["output"]>;
};

/** order by stddev_pop() on columns of table "blinds" */
export type BlindsStddevPopOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** aggregate stddev_samp on columns */
export type BlindsStddevSampFields = {
  __typename?: "blinds_stddev_samp_fields";
  level?: Maybe<Scalars["Float"]["output"]>;
};

/** order by stddev_samp() on columns of table "blinds" */
export type BlindsStddevSampOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** Streaming cursor of the table "blinds" */
export type BlindsStreamCursorInput = {
  /** Stream column input with initial value */
  initial_value: BlindsStreamCursorValueInput;
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
  room_id?: InputMaybe<Scalars["String"]["input"]>;
};

/** aggregate sum on columns */
export type BlindsSumFields = {
  __typename?: "blinds_sum_fields";
  level?: Maybe<Scalars["Float"]["output"]>;
};

/** order by sum() on columns of table "blinds" */
export type BlindsSumOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** aggregate var_pop on columns */
export type BlindsVarPopFields = {
  __typename?: "blinds_var_pop_fields";
  level?: Maybe<Scalars["Float"]["output"]>;
};

/** order by var_pop() on columns of table "blinds" */
export type BlindsVarPopOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** aggregate var_samp on columns */
export type BlindsVarSampFields = {
  __typename?: "blinds_var_samp_fields";
  level?: Maybe<Scalars["Float"]["output"]>;
};

/** order by var_samp() on columns of table "blinds" */
export type BlindsVarSampOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** aggregate variance on columns */
export type BlindsVarianceFields = {
  __typename?: "blinds_variance_fields";
  level?: Maybe<Scalars["Float"]["output"]>;
};

/** order by variance() on columns of table "blinds" */
export type BlindsVarianceOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** ordering argument of a cursor */
export enum CursorOrdering {
  /** ascending ordering of the cursor */
  Asc = "ASC",
  /** descending ordering of the cursor */
  Desc = "DESC",
}

/** columns and relationships of "lighting_groups" */
export type LightingGroups = {
  __typename?: "lighting_groups";
  id: Scalars["String"]["output"];
  level: Scalars["Float"]["output"];
  name: Scalars["String"]["output"];
  room_id?: Maybe<Scalars["String"]["output"]>;
};

/** aggregated selection of "lighting_groups" */
export type LightingGroupsAggregate = {
  __typename?: "lighting_groups_aggregate";
  aggregate?: Maybe<LightingGroupsAggregateFields>;
  nodes: Array<LightingGroups>;
};

export type LightingGroupsAggregateBoolExp = {
  count?: InputMaybe<LightingGroupsAggregateBoolExpCount>;
};

export type LightingGroupsAggregateBoolExpCount = {
  arguments?: InputMaybe<Array<LightingGroupsSelectColumn>>;
  distinct?: InputMaybe<Scalars["Boolean"]["input"]>;
  filter?: InputMaybe<LightingGroupsBoolExp>;
  predicate: IntComparisonExp;
};

/** aggregate fields of "lighting_groups" */
export type LightingGroupsAggregateFields = {
  __typename?: "lighting_groups_aggregate_fields";
  avg?: Maybe<LightingGroupsAvgFields>;
  count: Scalars["Int"]["output"];
  max?: Maybe<LightingGroupsMaxFields>;
  min?: Maybe<LightingGroupsMinFields>;
  stddev?: Maybe<LightingGroupsStddevFields>;
  stddev_pop?: Maybe<LightingGroupsStddevPopFields>;
  stddev_samp?: Maybe<LightingGroupsStddevSampFields>;
  sum?: Maybe<LightingGroupsSumFields>;
  var_pop?: Maybe<LightingGroupsVarPopFields>;
  var_samp?: Maybe<LightingGroupsVarSampFields>;
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
  stddev_pop?: InputMaybe<LightingGroupsStddevPopOrderBy>;
  stddev_samp?: InputMaybe<LightingGroupsStddevSampOrderBy>;
  sum?: InputMaybe<LightingGroupsSumOrderBy>;
  var_pop?: InputMaybe<LightingGroupsVarPopOrderBy>;
  var_samp?: InputMaybe<LightingGroupsVarSampOrderBy>;
  variance?: InputMaybe<LightingGroupsVarianceOrderBy>;
};

/** aggregate avg on columns */
export type LightingGroupsAvgFields = {
  __typename?: "lighting_groups_avg_fields";
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
  room_id?: InputMaybe<StringComparisonExp>;
};

/** aggregate max on columns */
export type LightingGroupsMaxFields = {
  __typename?: "lighting_groups_max_fields";
  id?: Maybe<Scalars["String"]["output"]>;
  level?: Maybe<Scalars["Float"]["output"]>;
  name?: Maybe<Scalars["String"]["output"]>;
  room_id?: Maybe<Scalars["String"]["output"]>;
};

/** order by max() on columns of table "lighting_groups" */
export type LightingGroupsMaxOrderBy = {
  id?: InputMaybe<OrderBy>;
  level?: InputMaybe<OrderBy>;
  name?: InputMaybe<OrderBy>;
  room_id?: InputMaybe<OrderBy>;
};

/** aggregate min on columns */
export type LightingGroupsMinFields = {
  __typename?: "lighting_groups_min_fields";
  id?: Maybe<Scalars["String"]["output"]>;
  level?: Maybe<Scalars["Float"]["output"]>;
  name?: Maybe<Scalars["String"]["output"]>;
  room_id?: Maybe<Scalars["String"]["output"]>;
};

/** order by min() on columns of table "lighting_groups" */
export type LightingGroupsMinOrderBy = {
  id?: InputMaybe<OrderBy>;
  level?: InputMaybe<OrderBy>;
  name?: InputMaybe<OrderBy>;
  room_id?: InputMaybe<OrderBy>;
};

/** Ordering options when selecting data from "lighting_groups". */
export type LightingGroupsOrderBy = {
  id?: InputMaybe<OrderBy>;
  level?: InputMaybe<OrderBy>;
  name?: InputMaybe<OrderBy>;
  room_id?: InputMaybe<OrderBy>;
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
  RoomId = "room_id",
}

/** aggregate stddev on columns */
export type LightingGroupsStddevFields = {
  __typename?: "lighting_groups_stddev_fields";
  level?: Maybe<Scalars["Float"]["output"]>;
};

/** order by stddev() on columns of table "lighting_groups" */
export type LightingGroupsStddevOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** aggregate stddev_pop on columns */
export type LightingGroupsStddevPopFields = {
  __typename?: "lighting_groups_stddev_pop_fields";
  level?: Maybe<Scalars["Float"]["output"]>;
};

/** order by stddev_pop() on columns of table "lighting_groups" */
export type LightingGroupsStddevPopOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** aggregate stddev_samp on columns */
export type LightingGroupsStddevSampFields = {
  __typename?: "lighting_groups_stddev_samp_fields";
  level?: Maybe<Scalars["Float"]["output"]>;
};

/** order by stddev_samp() on columns of table "lighting_groups" */
export type LightingGroupsStddevSampOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** Streaming cursor of the table "lighting_groups" */
export type LightingGroupsStreamCursorInput = {
  /** Stream column input with initial value */
  initial_value: LightingGroupsStreamCursorValueInput;
  /** cursor ordering */
  ordering?: InputMaybe<CursorOrdering>;
};

/** Initial value of the column from where the streaming should start */
export type LightingGroupsStreamCursorValueInput = {
  id?: InputMaybe<Scalars["String"]["input"]>;
  level?: InputMaybe<Scalars["Float"]["input"]>;
  name?: InputMaybe<Scalars["String"]["input"]>;
  room_id?: InputMaybe<Scalars["String"]["input"]>;
};

/** aggregate sum on columns */
export type LightingGroupsSumFields = {
  __typename?: "lighting_groups_sum_fields";
  level?: Maybe<Scalars["Float"]["output"]>;
};

/** order by sum() on columns of table "lighting_groups" */
export type LightingGroupsSumOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** aggregate var_pop on columns */
export type LightingGroupsVarPopFields = {
  __typename?: "lighting_groups_var_pop_fields";
  level?: Maybe<Scalars["Float"]["output"]>;
};

/** order by var_pop() on columns of table "lighting_groups" */
export type LightingGroupsVarPopOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** aggregate var_samp on columns */
export type LightingGroupsVarSampFields = {
  __typename?: "lighting_groups_var_samp_fields";
  level?: Maybe<Scalars["Float"]["output"]>;
};

/** order by var_samp() on columns of table "lighting_groups" */
export type LightingGroupsVarSampOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** aggregate variance on columns */
export type LightingGroupsVarianceFields = {
  __typename?: "lighting_groups_variance_fields";
  level?: Maybe<Scalars["Float"]["output"]>;
};

/** order by variance() on columns of table "lighting_groups" */
export type LightingGroupsVarianceOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** mutation root */
export type MutationRoot = {
  __typename?: "mutation_root";
  set_amplifier?: Maybe<Scalars["Void"]["output"]>;
  set_blind?: Maybe<Scalars["Void"]["output"]>;
  set_lighting_group?: Maybe<Scalars["Void"]["output"]>;
  set_lighting_groups?: Maybe<Scalars["Void"]["output"]>;
  set_room_temperature_setpoint?: Maybe<Scalars["Void"]["output"]>;
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

/** column ordering options */
export enum OrderBy {
  /** in ascending order, nulls last */
  Asc = "asc",
  /** in ascending order, nulls first */
  AscNullsFirst = "asc_nulls_first",
  /** in ascending order, nulls last */
  AscNullsLast = "asc_nulls_last",
  /** in descending order, nulls first */
  Desc = "desc",
  /** in descending order, nulls first */
  DescNullsFirst = "desc_nulls_first",
  /** in descending order, nulls last */
  DescNullsLast = "desc_nulls_last",
}

export type QueryRoot = {
  __typename?: "query_root";
  /** fetch data from the table: "blinds" */
  blinds: Array<Blinds>;
  /** fetch aggregated fields from the table: "blinds" */
  blinds_aggregate: BlindsAggregate;
  /** fetch data from the table: "blinds" using primary key columns */
  blinds_by_pk?: Maybe<Blinds>;
  /** An array relationship */
  lighting_groups: Array<LightingGroups>;
  /** An aggregate relationship */
  lighting_groups_aggregate: LightingGroupsAggregate;
  /** fetch data from the table: "lighting_groups" using primary key columns */
  lighting_groups_by_pk?: Maybe<LightingGroups>;
  /** fetch data from the table: "rooms" */
  rooms: Array<Rooms>;
  /** fetch aggregated fields from the table: "rooms" */
  rooms_aggregate: RoomsAggregate;
  /** fetch data from the table: "rooms" using primary key columns */
  rooms_by_pk?: Maybe<Rooms>;
  version: Scalars["String"]["output"];
};

export type QueryRootBlindsArgs = {
  distinct_on?: InputMaybe<Array<BlindsSelectColumn>>;
  limit?: InputMaybe<Scalars["Int"]["input"]>;
  offset?: InputMaybe<Scalars["Int"]["input"]>;
  order_by?: InputMaybe<Array<BlindsOrderBy>>;
  where?: InputMaybe<BlindsBoolExp>;
};

export type QueryRootBlindsAggregateArgs = {
  distinct_on?: InputMaybe<Array<BlindsSelectColumn>>;
  limit?: InputMaybe<Scalars["Int"]["input"]>;
  offset?: InputMaybe<Scalars["Int"]["input"]>;
  order_by?: InputMaybe<Array<BlindsOrderBy>>;
  where?: InputMaybe<BlindsBoolExp>;
};

export type QueryRootBlindsByPkArgs = {
  id: Scalars["String"]["input"];
};

export type QueryRootLightingGroupsArgs = {
  distinct_on?: InputMaybe<Array<LightingGroupsSelectColumn>>;
  limit?: InputMaybe<Scalars["Int"]["input"]>;
  offset?: InputMaybe<Scalars["Int"]["input"]>;
  order_by?: InputMaybe<Array<LightingGroupsOrderBy>>;
  where?: InputMaybe<LightingGroupsBoolExp>;
};

export type QueryRootLightingGroupsAggregateArgs = {
  distinct_on?: InputMaybe<Array<LightingGroupsSelectColumn>>;
  limit?: InputMaybe<Scalars["Int"]["input"]>;
  offset?: InputMaybe<Scalars["Int"]["input"]>;
  order_by?: InputMaybe<Array<LightingGroupsOrderBy>>;
  where?: InputMaybe<LightingGroupsBoolExp>;
};

export type QueryRootLightingGroupsByPkArgs = {
  id: Scalars["String"]["input"];
};

export type QueryRootRoomsArgs = {
  distinct_on?: InputMaybe<Array<RoomsSelectColumn>>;
  limit?: InputMaybe<Scalars["Int"]["input"]>;
  offset?: InputMaybe<Scalars["Int"]["input"]>;
  order_by?: InputMaybe<Array<RoomsOrderBy>>;
  where?: InputMaybe<RoomsBoolExp>;
};

export type QueryRootRoomsAggregateArgs = {
  distinct_on?: InputMaybe<Array<RoomsSelectColumn>>;
  limit?: InputMaybe<Scalars["Int"]["input"]>;
  offset?: InputMaybe<Scalars["Int"]["input"]>;
  order_by?: InputMaybe<Array<RoomsOrderBy>>;
  where?: InputMaybe<RoomsBoolExp>;
};

export type QueryRootRoomsByPkArgs = {
  id: Scalars["String"]["input"];
};

/** columns and relationships of "rooms" */
export type Rooms = {
  __typename?: "rooms";
  actual_humidity?: Maybe<Scalars["Float"]["output"]>;
  actual_temperature: Scalars["Float"]["output"];
  amplifier_on: Scalars["Boolean"]["output"];
  /** fetch data from the table: "blinds" */
  blinds: Array<Blinds>;
  /** fetch aggregated fields from the table: "blinds" */
  blinds_aggregate: BlindsAggregate;
  group: Scalars["String"]["output"];
  id: Scalars["String"]["output"];
  last_movement?: Maybe<Scalars["timestamptz"]["output"]>;
  /** An array relationship */
  lighting_groups: Array<LightingGroups>;
  /** An aggregate relationship */
  lighting_groups_aggregate: LightingGroupsAggregate;
  name: Scalars["String"]["output"];
  temperature_setpoint: Scalars["Float"]["output"];
  thermal_comfort_index?: Maybe<Scalars["Float"]["output"]>;
};

/** columns and relationships of "rooms" */
export type RoomsBlindsArgs = {
  distinct_on?: InputMaybe<Array<BlindsSelectColumn>>;
  limit?: InputMaybe<Scalars["Int"]["input"]>;
  offset?: InputMaybe<Scalars["Int"]["input"]>;
  order_by?: InputMaybe<Array<BlindsOrderBy>>;
  where?: InputMaybe<BlindsBoolExp>;
};

/** columns and relationships of "rooms" */
export type RoomsBlindsAggregateArgs = {
  distinct_on?: InputMaybe<Array<BlindsSelectColumn>>;
  limit?: InputMaybe<Scalars["Int"]["input"]>;
  offset?: InputMaybe<Scalars["Int"]["input"]>;
  order_by?: InputMaybe<Array<BlindsOrderBy>>;
  where?: InputMaybe<BlindsBoolExp>;
};

/** columns and relationships of "rooms" */
export type RoomsLightingGroupsArgs = {
  distinct_on?: InputMaybe<Array<LightingGroupsSelectColumn>>;
  limit?: InputMaybe<Scalars["Int"]["input"]>;
  offset?: InputMaybe<Scalars["Int"]["input"]>;
  order_by?: InputMaybe<Array<LightingGroupsOrderBy>>;
  where?: InputMaybe<LightingGroupsBoolExp>;
};

/** columns and relationships of "rooms" */
export type RoomsLightingGroupsAggregateArgs = {
  distinct_on?: InputMaybe<Array<LightingGroupsSelectColumn>>;
  limit?: InputMaybe<Scalars["Int"]["input"]>;
  offset?: InputMaybe<Scalars["Int"]["input"]>;
  order_by?: InputMaybe<Array<LightingGroupsOrderBy>>;
  where?: InputMaybe<LightingGroupsBoolExp>;
};

/** aggregated selection of "rooms" */
export type RoomsAggregate = {
  __typename?: "rooms_aggregate";
  aggregate?: Maybe<RoomsAggregateFields>;
  nodes: Array<Rooms>;
};

/** aggregate fields of "rooms" */
export type RoomsAggregateFields = {
  __typename?: "rooms_aggregate_fields";
  avg?: Maybe<RoomsAvgFields>;
  count: Scalars["Int"]["output"];
  max?: Maybe<RoomsMaxFields>;
  min?: Maybe<RoomsMinFields>;
  stddev?: Maybe<RoomsStddevFields>;
  stddev_pop?: Maybe<RoomsStddevPopFields>;
  stddev_samp?: Maybe<RoomsStddevSampFields>;
  sum?: Maybe<RoomsSumFields>;
  var_pop?: Maybe<RoomsVarPopFields>;
  var_samp?: Maybe<RoomsVarSampFields>;
  variance?: Maybe<RoomsVarianceFields>;
};

/** aggregate fields of "rooms" */
export type RoomsAggregateFieldsCountArgs = {
  columns?: InputMaybe<Array<RoomsSelectColumn>>;
  distinct?: InputMaybe<Scalars["Boolean"]["input"]>;
};

/** aggregate avg on columns */
export type RoomsAvgFields = {
  __typename?: "rooms_avg_fields";
  actual_humidity?: Maybe<Scalars["Float"]["output"]>;
  actual_temperature?: Maybe<Scalars["Float"]["output"]>;
  temperature_setpoint?: Maybe<Scalars["Float"]["output"]>;
  thermal_comfort_index?: Maybe<Scalars["Float"]["output"]>;
};

/** Boolean expression to filter rows from the table "rooms". All fields are combined with a logical 'AND'. */
export type RoomsBoolExp = {
  _and?: InputMaybe<Array<RoomsBoolExp>>;
  _not?: InputMaybe<RoomsBoolExp>;
  _or?: InputMaybe<Array<RoomsBoolExp>>;
  actual_humidity?: InputMaybe<FloatComparisonExp>;
  actual_temperature?: InputMaybe<FloatComparisonExp>;
  amplifier_on?: InputMaybe<BooleanComparisonExp>;
  blinds?: InputMaybe<BlindsBoolExp>;
  blinds_aggregate?: InputMaybe<BlindsAggregateBoolExp>;
  group?: InputMaybe<StringComparisonExp>;
  id?: InputMaybe<StringComparisonExp>;
  last_movement?: InputMaybe<TimestamptzComparisonExp>;
  lighting_groups?: InputMaybe<LightingGroupsBoolExp>;
  lighting_groups_aggregate?: InputMaybe<LightingGroupsAggregateBoolExp>;
  name?: InputMaybe<StringComparisonExp>;
  temperature_setpoint?: InputMaybe<FloatComparisonExp>;
  thermal_comfort_index?: InputMaybe<FloatComparisonExp>;
};

/** aggregate max on columns */
export type RoomsMaxFields = {
  __typename?: "rooms_max_fields";
  actual_humidity?: Maybe<Scalars["Float"]["output"]>;
  actual_temperature?: Maybe<Scalars["Float"]["output"]>;
  group?: Maybe<Scalars["String"]["output"]>;
  id?: Maybe<Scalars["String"]["output"]>;
  last_movement?: Maybe<Scalars["timestamptz"]["output"]>;
  name?: Maybe<Scalars["String"]["output"]>;
  temperature_setpoint?: Maybe<Scalars["Float"]["output"]>;
  thermal_comfort_index?: Maybe<Scalars["Float"]["output"]>;
};

/** aggregate min on columns */
export type RoomsMinFields = {
  __typename?: "rooms_min_fields";
  actual_humidity?: Maybe<Scalars["Float"]["output"]>;
  actual_temperature?: Maybe<Scalars["Float"]["output"]>;
  group?: Maybe<Scalars["String"]["output"]>;
  id?: Maybe<Scalars["String"]["output"]>;
  last_movement?: Maybe<Scalars["timestamptz"]["output"]>;
  name?: Maybe<Scalars["String"]["output"]>;
  temperature_setpoint?: Maybe<Scalars["Float"]["output"]>;
  thermal_comfort_index?: Maybe<Scalars["Float"]["output"]>;
};

/** Ordering options when selecting data from "rooms". */
export type RoomsOrderBy = {
  actual_humidity?: InputMaybe<OrderBy>;
  actual_temperature?: InputMaybe<OrderBy>;
  amplifier_on?: InputMaybe<OrderBy>;
  blinds_aggregate?: InputMaybe<BlindsAggregateOrderBy>;
  group?: InputMaybe<OrderBy>;
  id?: InputMaybe<OrderBy>;
  last_movement?: InputMaybe<OrderBy>;
  lighting_groups_aggregate?: InputMaybe<LightingGroupsAggregateOrderBy>;
  name?: InputMaybe<OrderBy>;
  temperature_setpoint?: InputMaybe<OrderBy>;
  thermal_comfort_index?: InputMaybe<OrderBy>;
};

/** select columns of table "rooms" */
export enum RoomsSelectColumn {
  /** column name */
  ActualHumidity = "actual_humidity",
  /** column name */
  ActualTemperature = "actual_temperature",
  /** column name */
  AmplifierOn = "amplifier_on",
  /** column name */
  Group = "group",
  /** column name */
  Id = "id",
  /** column name */
  LastMovement = "last_movement",
  /** column name */
  Name = "name",
  /** column name */
  TemperatureSetpoint = "temperature_setpoint",
  /** column name */
  ThermalComfortIndex = "thermal_comfort_index",
}

/** aggregate stddev on columns */
export type RoomsStddevFields = {
  __typename?: "rooms_stddev_fields";
  actual_humidity?: Maybe<Scalars["Float"]["output"]>;
  actual_temperature?: Maybe<Scalars["Float"]["output"]>;
  temperature_setpoint?: Maybe<Scalars["Float"]["output"]>;
  thermal_comfort_index?: Maybe<Scalars["Float"]["output"]>;
};

/** aggregate stddev_pop on columns */
export type RoomsStddevPopFields = {
  __typename?: "rooms_stddev_pop_fields";
  actual_humidity?: Maybe<Scalars["Float"]["output"]>;
  actual_temperature?: Maybe<Scalars["Float"]["output"]>;
  temperature_setpoint?: Maybe<Scalars["Float"]["output"]>;
  thermal_comfort_index?: Maybe<Scalars["Float"]["output"]>;
};

/** aggregate stddev_samp on columns */
export type RoomsStddevSampFields = {
  __typename?: "rooms_stddev_samp_fields";
  actual_humidity?: Maybe<Scalars["Float"]["output"]>;
  actual_temperature?: Maybe<Scalars["Float"]["output"]>;
  temperature_setpoint?: Maybe<Scalars["Float"]["output"]>;
  thermal_comfort_index?: Maybe<Scalars["Float"]["output"]>;
};

/** Streaming cursor of the table "rooms" */
export type RoomsStreamCursorInput = {
  /** Stream column input with initial value */
  initial_value: RoomsStreamCursorValueInput;
  /** cursor ordering */
  ordering?: InputMaybe<CursorOrdering>;
};

/** Initial value of the column from where the streaming should start */
export type RoomsStreamCursorValueInput = {
  actual_humidity?: InputMaybe<Scalars["Float"]["input"]>;
  actual_temperature?: InputMaybe<Scalars["Float"]["input"]>;
  amplifier_on?: InputMaybe<Scalars["Boolean"]["input"]>;
  group?: InputMaybe<Scalars["String"]["input"]>;
  id?: InputMaybe<Scalars["String"]["input"]>;
  last_movement?: InputMaybe<Scalars["timestamptz"]["input"]>;
  name?: InputMaybe<Scalars["String"]["input"]>;
  temperature_setpoint?: InputMaybe<Scalars["Float"]["input"]>;
  thermal_comfort_index?: InputMaybe<Scalars["Float"]["input"]>;
};

/** aggregate sum on columns */
export type RoomsSumFields = {
  __typename?: "rooms_sum_fields";
  actual_humidity?: Maybe<Scalars["Float"]["output"]>;
  actual_temperature?: Maybe<Scalars["Float"]["output"]>;
  temperature_setpoint?: Maybe<Scalars["Float"]["output"]>;
  thermal_comfort_index?: Maybe<Scalars["Float"]["output"]>;
};

/** aggregate var_pop on columns */
export type RoomsVarPopFields = {
  __typename?: "rooms_var_pop_fields";
  actual_humidity?: Maybe<Scalars["Float"]["output"]>;
  actual_temperature?: Maybe<Scalars["Float"]["output"]>;
  temperature_setpoint?: Maybe<Scalars["Float"]["output"]>;
  thermal_comfort_index?: Maybe<Scalars["Float"]["output"]>;
};

/** aggregate var_samp on columns */
export type RoomsVarSampFields = {
  __typename?: "rooms_var_samp_fields";
  actual_humidity?: Maybe<Scalars["Float"]["output"]>;
  actual_temperature?: Maybe<Scalars["Float"]["output"]>;
  temperature_setpoint?: Maybe<Scalars["Float"]["output"]>;
  thermal_comfort_index?: Maybe<Scalars["Float"]["output"]>;
};

/** aggregate variance on columns */
export type RoomsVarianceFields = {
  __typename?: "rooms_variance_fields";
  actual_humidity?: Maybe<Scalars["Float"]["output"]>;
  actual_temperature?: Maybe<Scalars["Float"]["output"]>;
  temperature_setpoint?: Maybe<Scalars["Float"]["output"]>;
  thermal_comfort_index?: Maybe<Scalars["Float"]["output"]>;
};

export type SubscriptionRoot = {
  __typename?: "subscription_root";
  /** fetch data from the table: "blinds" */
  blinds: Array<Blinds>;
  /** fetch aggregated fields from the table: "blinds" */
  blinds_aggregate: BlindsAggregate;
  /** fetch data from the table: "blinds" using primary key columns */
  blinds_by_pk?: Maybe<Blinds>;
  /** fetch data from the table in a streaming manner: "blinds" */
  blinds_stream: Array<Blinds>;
  /** An array relationship */
  lighting_groups: Array<LightingGroups>;
  /** An aggregate relationship */
  lighting_groups_aggregate: LightingGroupsAggregate;
  /** fetch data from the table: "lighting_groups" using primary key columns */
  lighting_groups_by_pk?: Maybe<LightingGroups>;
  /** fetch data from the table in a streaming manner: "lighting_groups" */
  lighting_groups_stream: Array<LightingGroups>;
  /** fetch data from the table: "rooms" */
  rooms: Array<Rooms>;
  /** fetch aggregated fields from the table: "rooms" */
  rooms_aggregate: RoomsAggregate;
  /** fetch data from the table: "rooms" using primary key columns */
  rooms_by_pk?: Maybe<Rooms>;
  /** fetch data from the table in a streaming manner: "rooms" */
  rooms_stream: Array<Rooms>;
};

export type SubscriptionRootBlindsArgs = {
  distinct_on?: InputMaybe<Array<BlindsSelectColumn>>;
  limit?: InputMaybe<Scalars["Int"]["input"]>;
  offset?: InputMaybe<Scalars["Int"]["input"]>;
  order_by?: InputMaybe<Array<BlindsOrderBy>>;
  where?: InputMaybe<BlindsBoolExp>;
};

export type SubscriptionRootBlindsAggregateArgs = {
  distinct_on?: InputMaybe<Array<BlindsSelectColumn>>;
  limit?: InputMaybe<Scalars["Int"]["input"]>;
  offset?: InputMaybe<Scalars["Int"]["input"]>;
  order_by?: InputMaybe<Array<BlindsOrderBy>>;
  where?: InputMaybe<BlindsBoolExp>;
};

export type SubscriptionRootBlindsByPkArgs = {
  id: Scalars["String"]["input"];
};

export type SubscriptionRootBlindsStreamArgs = {
  batch_size: Scalars["Int"]["input"];
  cursor: Array<InputMaybe<BlindsStreamCursorInput>>;
  where?: InputMaybe<BlindsBoolExp>;
};

export type SubscriptionRootLightingGroupsArgs = {
  distinct_on?: InputMaybe<Array<LightingGroupsSelectColumn>>;
  limit?: InputMaybe<Scalars["Int"]["input"]>;
  offset?: InputMaybe<Scalars["Int"]["input"]>;
  order_by?: InputMaybe<Array<LightingGroupsOrderBy>>;
  where?: InputMaybe<LightingGroupsBoolExp>;
};

export type SubscriptionRootLightingGroupsAggregateArgs = {
  distinct_on?: InputMaybe<Array<LightingGroupsSelectColumn>>;
  limit?: InputMaybe<Scalars["Int"]["input"]>;
  offset?: InputMaybe<Scalars["Int"]["input"]>;
  order_by?: InputMaybe<Array<LightingGroupsOrderBy>>;
  where?: InputMaybe<LightingGroupsBoolExp>;
};

export type SubscriptionRootLightingGroupsByPkArgs = {
  id: Scalars["String"]["input"];
};

export type SubscriptionRootLightingGroupsStreamArgs = {
  batch_size: Scalars["Int"]["input"];
  cursor: Array<InputMaybe<LightingGroupsStreamCursorInput>>;
  where?: InputMaybe<LightingGroupsBoolExp>;
};

export type SubscriptionRootRoomsArgs = {
  distinct_on?: InputMaybe<Array<RoomsSelectColumn>>;
  limit?: InputMaybe<Scalars["Int"]["input"]>;
  offset?: InputMaybe<Scalars["Int"]["input"]>;
  order_by?: InputMaybe<Array<RoomsOrderBy>>;
  where?: InputMaybe<RoomsBoolExp>;
};

export type SubscriptionRootRoomsAggregateArgs = {
  distinct_on?: InputMaybe<Array<RoomsSelectColumn>>;
  limit?: InputMaybe<Scalars["Int"]["input"]>;
  offset?: InputMaybe<Scalars["Int"]["input"]>;
  order_by?: InputMaybe<Array<RoomsOrderBy>>;
  where?: InputMaybe<RoomsBoolExp>;
};

export type SubscriptionRootRoomsByPkArgs = {
  id: Scalars["String"]["input"];
};

export type SubscriptionRootRoomsStreamArgs = {
  batch_size: Scalars["Int"]["input"];
  cursor: Array<InputMaybe<RoomsStreamCursorInput>>;
  where?: InputMaybe<RoomsBoolExp>;
};

/** Boolean expression to compare columns of type "timestamptz". All fields are combined with logical 'AND'. */
export type TimestamptzComparisonExp = {
  _eq?: InputMaybe<Scalars["timestamptz"]["input"]>;
  _gt?: InputMaybe<Scalars["timestamptz"]["input"]>;
  _gte?: InputMaybe<Scalars["timestamptz"]["input"]>;
  _in?: InputMaybe<Array<Scalars["timestamptz"]["input"]>>;
  _is_null?: InputMaybe<Scalars["Boolean"]["input"]>;
  _lt?: InputMaybe<Scalars["timestamptz"]["input"]>;
  _lte?: InputMaybe<Scalars["timestamptz"]["input"]>;
  _neq?: InputMaybe<Scalars["timestamptz"]["input"]>;
  _nin?: InputMaybe<Array<Scalars["timestamptz"]["input"]>>;
};

export type BlindsItemFragment = {
  __typename?: "blinds";
  id: string;
  name: string;
  level: number;
  room_id?: string | null;
  opacity: any;
  group: string;
} & { " $fragmentName"?: "BlindsItemFragment" };

export type GetBlindsByRoomQueryVariables = Exact<{
  roomId: Scalars["String"]["input"];
}>;

export type GetBlindsByRoomQuery = {
  __typename?: "query_root";
  blinds: Array<
    { __typename?: "blinds" } & { " $fragmentRefs"?: { BlindsItemFragment: BlindsItemFragment } }
  >;
};

export type LightGroupItemFragment = {
  __typename?: "lighting_groups";
  id: string;
  name: string;
  level: number;
  room_id?: string | null;
} & { " $fragmentName"?: "LightGroupItemFragment" };

export type GetLightGroupsByRoomQueryVariables = Exact<{
  roomId: Scalars["String"]["input"];
}>;

export type GetLightGroupsByRoomQuery = {
  __typename?: "query_root";
  lighting_groups: Array<
    { __typename?: "lighting_groups" } & {
      " $fragmentRefs"?: { LightGroupItemFragment: LightGroupItemFragment };
    }
  >;
};

export type RoomItemFragment = {
  __typename?: "rooms";
  id: string;
  amplifier_on: boolean;
  actual_temperature: number;
  actual_humidity?: number | null;
  temperature_setpoint: number;
  thermal_comfort_index?: number | null;
  name: string;
  group: string;
  last_movement?: any | null;
  blinds: Array<
    { __typename?: "blinds" } & { " $fragmentRefs"?: { BlindsItemFragment: BlindsItemFragment } }
  >;
  lighting_groups: Array<
    { __typename?: "lighting_groups" } & {
      " $fragmentRefs"?: { LightGroupItemFragment: LightGroupItemFragment };
    }
  >;
} & { " $fragmentName"?: "RoomItemFragment" };

export type GetAllRoomsQueryVariables = Exact<{ [key: string]: never }>;

export type GetAllRoomsQuery = {
  __typename?: "query_root";
  rooms: Array<
    { __typename?: "rooms" } & { " $fragmentRefs"?: { RoomItemFragment: RoomItemFragment } }
  >;
};

export const BlindsItemFragmentDoc = {
  kind: "Document",
  definitions: [
    {
      kind: "FragmentDefinition",
      name: { kind: "Name", value: "BlindsItem" },
      typeCondition: { kind: "NamedType", name: { kind: "Name", value: "blinds" } },
      selectionSet: {
        kind: "SelectionSet",
        selections: [
          { kind: "Field", name: { kind: "Name", value: "id" } },
          { kind: "Field", name: { kind: "Name", value: "name" } },
          { kind: "Field", name: { kind: "Name", value: "level" } },
          { kind: "Field", name: { kind: "Name", value: "room_id" } },
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
      typeCondition: { kind: "NamedType", name: { kind: "Name", value: "lighting_groups" } },
      selectionSet: {
        kind: "SelectionSet",
        selections: [
          { kind: "Field", name: { kind: "Name", value: "id" } },
          { kind: "Field", name: { kind: "Name", value: "name" } },
          { kind: "Field", name: { kind: "Name", value: "level" } },
          { kind: "Field", name: { kind: "Name", value: "room_id" } },
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
      typeCondition: { kind: "NamedType", name: { kind: "Name", value: "rooms" } },
      selectionSet: {
        kind: "SelectionSet",
        selections: [
          { kind: "Field", name: { kind: "Name", value: "id" } },
          { kind: "Field", name: { kind: "Name", value: "amplifier_on" } },
          { kind: "Field", name: { kind: "Name", value: "actual_temperature" } },
          { kind: "Field", name: { kind: "Name", value: "actual_humidity" } },
          { kind: "Field", name: { kind: "Name", value: "temperature_setpoint" } },
          { kind: "Field", name: { kind: "Name", value: "thermal_comfort_index" } },
          { kind: "Field", name: { kind: "Name", value: "name" } },
          { kind: "Field", name: { kind: "Name", value: "group" } },
          { kind: "Field", name: { kind: "Name", value: "last_movement" } },
          {
            kind: "Field",
            name: { kind: "Name", value: "blinds" },
            selectionSet: {
              kind: "SelectionSet",
              selections: [{ kind: "FragmentSpread", name: { kind: "Name", value: "BlindsItem" } }],
            },
          },
          {
            kind: "Field",
            name: { kind: "Name", value: "lighting_groups" },
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
      name: { kind: "Name", value: "BlindsItem" },
      typeCondition: { kind: "NamedType", name: { kind: "Name", value: "blinds" } },
      selectionSet: {
        kind: "SelectionSet",
        selections: [
          { kind: "Field", name: { kind: "Name", value: "id" } },
          { kind: "Field", name: { kind: "Name", value: "name" } },
          { kind: "Field", name: { kind: "Name", value: "level" } },
          { kind: "Field", name: { kind: "Name", value: "room_id" } },
          { kind: "Field", name: { kind: "Name", value: "opacity" } },
          { kind: "Field", name: { kind: "Name", value: "group" } },
        ],
      },
    },
    {
      kind: "FragmentDefinition",
      name: { kind: "Name", value: "LightGroupItem" },
      typeCondition: { kind: "NamedType", name: { kind: "Name", value: "lighting_groups" } },
      selectionSet: {
        kind: "SelectionSet",
        selections: [
          { kind: "Field", name: { kind: "Name", value: "id" } },
          { kind: "Field", name: { kind: "Name", value: "name" } },
          { kind: "Field", name: { kind: "Name", value: "level" } },
          { kind: "Field", name: { kind: "Name", value: "room_id" } },
        ],
      },
    },
  ],
} as unknown as DocumentNode<RoomItemFragment, unknown>;
export const GetBlindsByRoomDocument = {
  kind: "Document",
  definitions: [
    {
      kind: "OperationDefinition",
      operation: "query",
      name: { kind: "Name", value: "GetBlindsByRoom" },
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
            name: { kind: "Name", value: "blinds" },
            arguments: [
              {
                kind: "Argument",
                name: { kind: "Name", value: "where" },
                value: {
                  kind: "ObjectValue",
                  fields: [
                    {
                      kind: "ObjectField",
                      name: { kind: "Name", value: "room_id" },
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
              selections: [{ kind: "FragmentSpread", name: { kind: "Name", value: "BlindsItem" } }],
            },
          },
        ],
      },
    },
    {
      kind: "FragmentDefinition",
      name: { kind: "Name", value: "BlindsItem" },
      typeCondition: { kind: "NamedType", name: { kind: "Name", value: "blinds" } },
      selectionSet: {
        kind: "SelectionSet",
        selections: [
          { kind: "Field", name: { kind: "Name", value: "id" } },
          { kind: "Field", name: { kind: "Name", value: "name" } },
          { kind: "Field", name: { kind: "Name", value: "level" } },
          { kind: "Field", name: { kind: "Name", value: "room_id" } },
          { kind: "Field", name: { kind: "Name", value: "opacity" } },
          { kind: "Field", name: { kind: "Name", value: "group" } },
        ],
      },
    },
  ],
} as unknown as DocumentNode<GetBlindsByRoomQuery, GetBlindsByRoomQueryVariables>;
export const GetLightGroupsByRoomDocument = {
  kind: "Document",
  definitions: [
    {
      kind: "OperationDefinition",
      operation: "query",
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
            name: { kind: "Name", value: "lighting_groups" },
            arguments: [
              {
                kind: "Argument",
                name: { kind: "Name", value: "where" },
                value: {
                  kind: "ObjectValue",
                  fields: [
                    {
                      kind: "ObjectField",
                      name: { kind: "Name", value: "room_id" },
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
      typeCondition: { kind: "NamedType", name: { kind: "Name", value: "lighting_groups" } },
      selectionSet: {
        kind: "SelectionSet",
        selections: [
          { kind: "Field", name: { kind: "Name", value: "id" } },
          { kind: "Field", name: { kind: "Name", value: "name" } },
          { kind: "Field", name: { kind: "Name", value: "level" } },
          { kind: "Field", name: { kind: "Name", value: "room_id" } },
        ],
      },
    },
  ],
} as unknown as DocumentNode<GetLightGroupsByRoomQuery, GetLightGroupsByRoomQueryVariables>;
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
              selections: [{ kind: "FragmentSpread", name: { kind: "Name", value: "RoomItem" } }],
            },
          },
        ],
      },
    },
    {
      kind: "FragmentDefinition",
      name: { kind: "Name", value: "BlindsItem" },
      typeCondition: { kind: "NamedType", name: { kind: "Name", value: "blinds" } },
      selectionSet: {
        kind: "SelectionSet",
        selections: [
          { kind: "Field", name: { kind: "Name", value: "id" } },
          { kind: "Field", name: { kind: "Name", value: "name" } },
          { kind: "Field", name: { kind: "Name", value: "level" } },
          { kind: "Field", name: { kind: "Name", value: "room_id" } },
          { kind: "Field", name: { kind: "Name", value: "opacity" } },
          { kind: "Field", name: { kind: "Name", value: "group" } },
        ],
      },
    },
    {
      kind: "FragmentDefinition",
      name: { kind: "Name", value: "LightGroupItem" },
      typeCondition: { kind: "NamedType", name: { kind: "Name", value: "lighting_groups" } },
      selectionSet: {
        kind: "SelectionSet",
        selections: [
          { kind: "Field", name: { kind: "Name", value: "id" } },
          { kind: "Field", name: { kind: "Name", value: "name" } },
          { kind: "Field", name: { kind: "Name", value: "level" } },
          { kind: "Field", name: { kind: "Name", value: "room_id" } },
        ],
      },
    },
    {
      kind: "FragmentDefinition",
      name: { kind: "Name", value: "RoomItem" },
      typeCondition: { kind: "NamedType", name: { kind: "Name", value: "rooms" } },
      selectionSet: {
        kind: "SelectionSet",
        selections: [
          { kind: "Field", name: { kind: "Name", value: "id" } },
          { kind: "Field", name: { kind: "Name", value: "amplifier_on" } },
          { kind: "Field", name: { kind: "Name", value: "actual_temperature" } },
          { kind: "Field", name: { kind: "Name", value: "actual_humidity" } },
          { kind: "Field", name: { kind: "Name", value: "temperature_setpoint" } },
          { kind: "Field", name: { kind: "Name", value: "thermal_comfort_index" } },
          { kind: "Field", name: { kind: "Name", value: "name" } },
          { kind: "Field", name: { kind: "Name", value: "group" } },
          { kind: "Field", name: { kind: "Name", value: "last_movement" } },
          {
            kind: "Field",
            name: { kind: "Name", value: "blinds" },
            selectionSet: {
              kind: "SelectionSet",
              selections: [{ kind: "FragmentSpread", name: { kind: "Name", value: "BlindsItem" } }],
            },
          },
          {
            kind: "Field",
            name: { kind: "Name", value: "lighting_groups" },
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
} as unknown as DocumentNode<GetAllRoomsQuery, GetAllRoomsQueryVariables>;
