/* eslint-disable */
import type { TypedDocumentNode as DocumentNode } from '@graphql-typed-document-node/core';
export type Maybe<T> = T | null;
export type InputMaybe<T> = T | null | undefined;
export type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
export type MakeOptional<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]?: Maybe<T[SubKey]> };
export type MakeMaybe<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]: Maybe<T[SubKey]> };
export type MakeEmpty<T extends { [key: string]: unknown }, K extends keyof T> = { [_ in K]?: never };
export type Incremental<T> = T | { [P in keyof T]?: P extends ' $fragmentName' | '__typename' ? T[P] : never };
/** All built-in and custom scalars, mapped to their actual values */
export type Scalars = {
  ID: { input: string; output: string; }
  String: { input: string; output: string; }
  Boolean: { input: boolean; output: boolean; }
  Int: { input: number; output: number; }
  Float: { input: number; output: number; }
  /** Date with time (isoformat) */
  DateTime: { input: any; output: any; }
};

export type AcLogType = {
  __typename?: 'AcLogType';
  actualHumidity: Scalars['Float']['output'];
  actualTemperature: Scalars['Float']['output'];
  humiditySetpoint: Scalars['Float']['output'];
  temperatureSetpoint: Scalars['Float']['output'];
  timestamp: Scalars['DateTime']['output'];
};

export type AmplifiersLogType = {
  __typename?: 'AmplifiersLogType';
  id: Scalars['String']['output'];
  on: Scalars['Boolean']['output'];
  timestamp: Scalars['DateTime']['output'];
};

export type BlindsLogType = {
  __typename?: 'BlindsLogType';
  id: Scalars['String']['output'];
  level: Scalars['Float']['output'];
  roomId: Scalars['String']['output'];
  timestamp: Scalars['DateTime']['output'];
};

/** Boolean expression to compare columns of type "Boolean". All fields are combined with logical 'AND'. */
export type BooleanComparisonExp = {
  _eq?: InputMaybe<Scalars['Boolean']['input']>;
  _gt?: InputMaybe<Scalars['Boolean']['input']>;
  _gte?: InputMaybe<Scalars['Boolean']['input']>;
  _in?: InputMaybe<Array<Scalars['Boolean']['input']>>;
  _isNull?: InputMaybe<Scalars['Boolean']['input']>;
  _lt?: InputMaybe<Scalars['Boolean']['input']>;
  _lte?: InputMaybe<Scalars['Boolean']['input']>;
  _neq?: InputMaybe<Scalars['Boolean']['input']>;
  _nin?: InputMaybe<Array<Scalars['Boolean']['input']>>;
};

/** ordering argument of a cursor */
export enum CursorOrdering {
  /** ascending ordering of the cursor */
  Asc = 'ASC',
  /** descending ordering of the cursor */
  Desc = 'DESC'
}

/** columns and relationships of "domestic.air_conditioning" */
export type DomesticAirConditioning = {
  __typename?: 'DomesticAirConditioning';
  actualHumidity?: Maybe<Scalars['Float']['output']>;
  actualTemperature?: Maybe<Scalars['Float']['output']>;
  humiditySetpoint?: Maybe<Scalars['Float']['output']>;
  id: Scalars['String']['output'];
  /** An object relationship */
  room: DomesticRooms;
  temperatureSetpoint?: Maybe<Scalars['Float']['output']>;
};

/** aggregated selection of "domestic.air_conditioning" */
export type DomesticAirConditioningAggregate = {
  __typename?: 'DomesticAirConditioningAggregate';
  aggregate?: Maybe<DomesticAirConditioningAggregateFields>;
  nodes: Array<DomesticAirConditioning>;
};

/** aggregate fields of "domestic.air_conditioning" */
export type DomesticAirConditioningAggregateFields = {
  __typename?: 'DomesticAirConditioningAggregateFields';
  avg?: Maybe<DomesticAirConditioningAvgFields>;
  count: Scalars['Int']['output'];
  max?: Maybe<DomesticAirConditioningMaxFields>;
  min?: Maybe<DomesticAirConditioningMinFields>;
  stddev?: Maybe<DomesticAirConditioningStddevFields>;
  stddevPop?: Maybe<DomesticAirConditioningStddevPopFields>;
  stddevSamp?: Maybe<DomesticAirConditioningStddevSampFields>;
  sum?: Maybe<DomesticAirConditioningSumFields>;
  varPop?: Maybe<DomesticAirConditioningVarPopFields>;
  varSamp?: Maybe<DomesticAirConditioningVarSampFields>;
  variance?: Maybe<DomesticAirConditioningVarianceFields>;
};


/** aggregate fields of "domestic.air_conditioning" */
export type DomesticAirConditioningAggregateFieldsCountArgs = {
  columns?: InputMaybe<Array<DomesticAirConditioningSelectColumn>>;
  distinct?: InputMaybe<Scalars['Boolean']['input']>;
};

/** aggregate avg on columns */
export type DomesticAirConditioningAvgFields = {
  __typename?: 'DomesticAirConditioningAvgFields';
  actualHumidity?: Maybe<Scalars['Float']['output']>;
  actualTemperature?: Maybe<Scalars['Float']['output']>;
  humiditySetpoint?: Maybe<Scalars['Float']['output']>;
  temperatureSetpoint?: Maybe<Scalars['Float']['output']>;
};

/** Boolean expression to filter rows from the table "domestic.air_conditioning". All fields are combined with a logical 'AND'. */
export type DomesticAirConditioningBoolExp = {
  _and?: InputMaybe<Array<DomesticAirConditioningBoolExp>>;
  _not?: InputMaybe<DomesticAirConditioningBoolExp>;
  _or?: InputMaybe<Array<DomesticAirConditioningBoolExp>>;
  actualHumidity?: InputMaybe<FloatComparisonExp>;
  actualTemperature?: InputMaybe<FloatComparisonExp>;
  humiditySetpoint?: InputMaybe<FloatComparisonExp>;
  id?: InputMaybe<StringComparisonExp>;
  room?: InputMaybe<DomesticRoomsBoolExp>;
  temperatureSetpoint?: InputMaybe<FloatComparisonExp>;
};

/** unique or primary key constraints on table "domestic.air_conditioning" */
export enum DomesticAirConditioningConstraint {
  /** unique or primary key constraint on columns "id" */
  AirConditioningPkey = 'air_conditioning_pkey'
}

/** input type for incrementing numeric columns in table "domestic.air_conditioning" */
export type DomesticAirConditioningIncInput = {
  actualHumidity?: InputMaybe<Scalars['Float']['input']>;
  actualTemperature?: InputMaybe<Scalars['Float']['input']>;
  humiditySetpoint?: InputMaybe<Scalars['Float']['input']>;
  temperatureSetpoint?: InputMaybe<Scalars['Float']['input']>;
};

/** input type for inserting data into table "domestic.air_conditioning" */
export type DomesticAirConditioningInsertInput = {
  actualHumidity?: InputMaybe<Scalars['Float']['input']>;
  actualTemperature?: InputMaybe<Scalars['Float']['input']>;
  humiditySetpoint?: InputMaybe<Scalars['Float']['input']>;
  id?: InputMaybe<Scalars['String']['input']>;
  room?: InputMaybe<DomesticRoomsObjRelInsertInput>;
  temperatureSetpoint?: InputMaybe<Scalars['Float']['input']>;
};

/** aggregate max on columns */
export type DomesticAirConditioningMaxFields = {
  __typename?: 'DomesticAirConditioningMaxFields';
  actualHumidity?: Maybe<Scalars['Float']['output']>;
  actualTemperature?: Maybe<Scalars['Float']['output']>;
  humiditySetpoint?: Maybe<Scalars['Float']['output']>;
  id?: Maybe<Scalars['String']['output']>;
  temperatureSetpoint?: Maybe<Scalars['Float']['output']>;
};

/** aggregate min on columns */
export type DomesticAirConditioningMinFields = {
  __typename?: 'DomesticAirConditioningMinFields';
  actualHumidity?: Maybe<Scalars['Float']['output']>;
  actualTemperature?: Maybe<Scalars['Float']['output']>;
  humiditySetpoint?: Maybe<Scalars['Float']['output']>;
  id?: Maybe<Scalars['String']['output']>;
  temperatureSetpoint?: Maybe<Scalars['Float']['output']>;
};

/** response of any mutation on the table "domestic.air_conditioning" */
export type DomesticAirConditioningMutationResponse = {
  __typename?: 'DomesticAirConditioningMutationResponse';
  /** number of rows affected by the mutation */
  affectedRows: Scalars['Int']['output'];
  /** data from the rows affected by the mutation */
  returning: Array<DomesticAirConditioning>;
};

/** input type for inserting object relation for remote table "domestic.air_conditioning" */
export type DomesticAirConditioningObjRelInsertInput = {
  data: DomesticAirConditioningInsertInput;
  /** upsert condition */
  onConflict?: InputMaybe<DomesticAirConditioningOnConflict>;
};

/** on_conflict condition type for table "domestic.air_conditioning" */
export type DomesticAirConditioningOnConflict = {
  constraint: DomesticAirConditioningConstraint;
  updateColumns?: Array<DomesticAirConditioningUpdateColumn>;
  where?: InputMaybe<DomesticAirConditioningBoolExp>;
};

/** Ordering options when selecting data from "domestic.air_conditioning". */
export type DomesticAirConditioningOrderBy = {
  actualHumidity?: InputMaybe<OrderBy>;
  actualTemperature?: InputMaybe<OrderBy>;
  humiditySetpoint?: InputMaybe<OrderBy>;
  id?: InputMaybe<OrderBy>;
  room?: InputMaybe<DomesticRoomsOrderBy>;
  temperatureSetpoint?: InputMaybe<OrderBy>;
};

/** primary key columns input for table: domestic.air_conditioning */
export type DomesticAirConditioningPkColumnsInput = {
  id: Scalars['String']['input'];
};

/** select columns of table "domestic.air_conditioning" */
export enum DomesticAirConditioningSelectColumn {
  /** column name */
  ActualHumidity = 'actualHumidity',
  /** column name */
  ActualTemperature = 'actualTemperature',
  /** column name */
  HumiditySetpoint = 'humiditySetpoint',
  /** column name */
  Id = 'id',
  /** column name */
  TemperatureSetpoint = 'temperatureSetpoint'
}

/** input type for updating data in table "domestic.air_conditioning" */
export type DomesticAirConditioningSetInput = {
  actualHumidity?: InputMaybe<Scalars['Float']['input']>;
  actualTemperature?: InputMaybe<Scalars['Float']['input']>;
  humiditySetpoint?: InputMaybe<Scalars['Float']['input']>;
  id?: InputMaybe<Scalars['String']['input']>;
  temperatureSetpoint?: InputMaybe<Scalars['Float']['input']>;
};

/** aggregate stddev on columns */
export type DomesticAirConditioningStddevFields = {
  __typename?: 'DomesticAirConditioningStddevFields';
  actualHumidity?: Maybe<Scalars['Float']['output']>;
  actualTemperature?: Maybe<Scalars['Float']['output']>;
  humiditySetpoint?: Maybe<Scalars['Float']['output']>;
  temperatureSetpoint?: Maybe<Scalars['Float']['output']>;
};

/** aggregate stddevPop on columns */
export type DomesticAirConditioningStddevPopFields = {
  __typename?: 'DomesticAirConditioningStddevPopFields';
  actualHumidity?: Maybe<Scalars['Float']['output']>;
  actualTemperature?: Maybe<Scalars['Float']['output']>;
  humiditySetpoint?: Maybe<Scalars['Float']['output']>;
  temperatureSetpoint?: Maybe<Scalars['Float']['output']>;
};

/** aggregate stddevSamp on columns */
export type DomesticAirConditioningStddevSampFields = {
  __typename?: 'DomesticAirConditioningStddevSampFields';
  actualHumidity?: Maybe<Scalars['Float']['output']>;
  actualTemperature?: Maybe<Scalars['Float']['output']>;
  humiditySetpoint?: Maybe<Scalars['Float']['output']>;
  temperatureSetpoint?: Maybe<Scalars['Float']['output']>;
};

/** Streaming cursor of the table "domestic_air_conditioning" */
export type DomesticAirConditioningStreamCursorInput = {
  /** Stream column input with initial value */
  initialValue: DomesticAirConditioningStreamCursorValueInput;
  /** cursor ordering */
  ordering?: InputMaybe<CursorOrdering>;
};

/** Initial value of the column from where the streaming should start */
export type DomesticAirConditioningStreamCursorValueInput = {
  actualHumidity?: InputMaybe<Scalars['Float']['input']>;
  actualTemperature?: InputMaybe<Scalars['Float']['input']>;
  humiditySetpoint?: InputMaybe<Scalars['Float']['input']>;
  id?: InputMaybe<Scalars['String']['input']>;
  temperatureSetpoint?: InputMaybe<Scalars['Float']['input']>;
};

/** aggregate sum on columns */
export type DomesticAirConditioningSumFields = {
  __typename?: 'DomesticAirConditioningSumFields';
  actualHumidity?: Maybe<Scalars['Float']['output']>;
  actualTemperature?: Maybe<Scalars['Float']['output']>;
  humiditySetpoint?: Maybe<Scalars['Float']['output']>;
  temperatureSetpoint?: Maybe<Scalars['Float']['output']>;
};

/** update columns of table "domestic.air_conditioning" */
export enum DomesticAirConditioningUpdateColumn {
  /** column name */
  ActualHumidity = 'actualHumidity',
  /** column name */
  ActualTemperature = 'actualTemperature',
  /** column name */
  HumiditySetpoint = 'humiditySetpoint',
  /** column name */
  Id = 'id',
  /** column name */
  TemperatureSetpoint = 'temperatureSetpoint'
}

export type DomesticAirConditioningUpdates = {
  /** increments the numeric columns with given value of the filtered values */
  _inc?: InputMaybe<DomesticAirConditioningIncInput>;
  /** sets the columns of the filtered rows to the given values */
  _set?: InputMaybe<DomesticAirConditioningSetInput>;
  /** filter the rows which have to be updated */
  where: DomesticAirConditioningBoolExp;
};

/** aggregate varPop on columns */
export type DomesticAirConditioningVarPopFields = {
  __typename?: 'DomesticAirConditioningVarPopFields';
  actualHumidity?: Maybe<Scalars['Float']['output']>;
  actualTemperature?: Maybe<Scalars['Float']['output']>;
  humiditySetpoint?: Maybe<Scalars['Float']['output']>;
  temperatureSetpoint?: Maybe<Scalars['Float']['output']>;
};

/** aggregate varSamp on columns */
export type DomesticAirConditioningVarSampFields = {
  __typename?: 'DomesticAirConditioningVarSampFields';
  actualHumidity?: Maybe<Scalars['Float']['output']>;
  actualTemperature?: Maybe<Scalars['Float']['output']>;
  humiditySetpoint?: Maybe<Scalars['Float']['output']>;
  temperatureSetpoint?: Maybe<Scalars['Float']['output']>;
};

/** aggregate variance on columns */
export type DomesticAirConditioningVarianceFields = {
  __typename?: 'DomesticAirConditioningVarianceFields';
  actualHumidity?: Maybe<Scalars['Float']['output']>;
  actualTemperature?: Maybe<Scalars['Float']['output']>;
  humiditySetpoint?: Maybe<Scalars['Float']['output']>;
  temperatureSetpoint?: Maybe<Scalars['Float']['output']>;
};

/** columns and relationships of "domestic.amplifiers" */
export type DomesticAmplifiers = {
  __typename?: 'DomesticAmplifiers';
  id: Scalars['String']['output'];
  name?: Maybe<Scalars['String']['output']>;
  on?: Maybe<Scalars['Boolean']['output']>;
  /** An object relationship */
  room: DomesticRooms;
};

/** aggregated selection of "domestic.amplifiers" */
export type DomesticAmplifiersAggregate = {
  __typename?: 'DomesticAmplifiersAggregate';
  aggregate?: Maybe<DomesticAmplifiersAggregateFields>;
  nodes: Array<DomesticAmplifiers>;
};

/** aggregate fields of "domestic.amplifiers" */
export type DomesticAmplifiersAggregateFields = {
  __typename?: 'DomesticAmplifiersAggregateFields';
  count: Scalars['Int']['output'];
  max?: Maybe<DomesticAmplifiersMaxFields>;
  min?: Maybe<DomesticAmplifiersMinFields>;
};


/** aggregate fields of "domestic.amplifiers" */
export type DomesticAmplifiersAggregateFieldsCountArgs = {
  columns?: InputMaybe<Array<DomesticAmplifiersSelectColumn>>;
  distinct?: InputMaybe<Scalars['Boolean']['input']>;
};

/** Boolean expression to filter rows from the table "domestic.amplifiers". All fields are combined with a logical 'AND'. */
export type DomesticAmplifiersBoolExp = {
  _and?: InputMaybe<Array<DomesticAmplifiersBoolExp>>;
  _not?: InputMaybe<DomesticAmplifiersBoolExp>;
  _or?: InputMaybe<Array<DomesticAmplifiersBoolExp>>;
  id?: InputMaybe<StringComparisonExp>;
  name?: InputMaybe<StringComparisonExp>;
  on?: InputMaybe<BooleanComparisonExp>;
  room?: InputMaybe<DomesticRoomsBoolExp>;
};

/** unique or primary key constraints on table "domestic.amplifiers" */
export enum DomesticAmplifiersConstraint {
  /** unique or primary key constraint on columns "id" */
  AmplifiersPkey = 'amplifiers_pkey'
}

/** input type for inserting data into table "domestic.amplifiers" */
export type DomesticAmplifiersInsertInput = {
  id?: InputMaybe<Scalars['String']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
  on?: InputMaybe<Scalars['Boolean']['input']>;
  room?: InputMaybe<DomesticRoomsObjRelInsertInput>;
};

/** aggregate max on columns */
export type DomesticAmplifiersMaxFields = {
  __typename?: 'DomesticAmplifiersMaxFields';
  id?: Maybe<Scalars['String']['output']>;
  name?: Maybe<Scalars['String']['output']>;
};

/** aggregate min on columns */
export type DomesticAmplifiersMinFields = {
  __typename?: 'DomesticAmplifiersMinFields';
  id?: Maybe<Scalars['String']['output']>;
  name?: Maybe<Scalars['String']['output']>;
};

/** response of any mutation on the table "domestic.amplifiers" */
export type DomesticAmplifiersMutationResponse = {
  __typename?: 'DomesticAmplifiersMutationResponse';
  /** number of rows affected by the mutation */
  affectedRows: Scalars['Int']['output'];
  /** data from the rows affected by the mutation */
  returning: Array<DomesticAmplifiers>;
};

/** input type for inserting object relation for remote table "domestic.amplifiers" */
export type DomesticAmplifiersObjRelInsertInput = {
  data: DomesticAmplifiersInsertInput;
  /** upsert condition */
  onConflict?: InputMaybe<DomesticAmplifiersOnConflict>;
};

/** on_conflict condition type for table "domestic.amplifiers" */
export type DomesticAmplifiersOnConflict = {
  constraint: DomesticAmplifiersConstraint;
  updateColumns?: Array<DomesticAmplifiersUpdateColumn>;
  where?: InputMaybe<DomesticAmplifiersBoolExp>;
};

/** Ordering options when selecting data from "domestic.amplifiers". */
export type DomesticAmplifiersOrderBy = {
  id?: InputMaybe<OrderBy>;
  name?: InputMaybe<OrderBy>;
  on?: InputMaybe<OrderBy>;
  room?: InputMaybe<DomesticRoomsOrderBy>;
};

/** primary key columns input for table: domestic.amplifiers */
export type DomesticAmplifiersPkColumnsInput = {
  id: Scalars['String']['input'];
};

/** select columns of table "domestic.amplifiers" */
export enum DomesticAmplifiersSelectColumn {
  /** column name */
  Id = 'id',
  /** column name */
  Name = 'name',
  /** column name */
  On = 'on'
}

/** input type for updating data in table "domestic.amplifiers" */
export type DomesticAmplifiersSetInput = {
  id?: InputMaybe<Scalars['String']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
  on?: InputMaybe<Scalars['Boolean']['input']>;
};

/** Streaming cursor of the table "domestic_amplifiers" */
export type DomesticAmplifiersStreamCursorInput = {
  /** Stream column input with initial value */
  initialValue: DomesticAmplifiersStreamCursorValueInput;
  /** cursor ordering */
  ordering?: InputMaybe<CursorOrdering>;
};

/** Initial value of the column from where the streaming should start */
export type DomesticAmplifiersStreamCursorValueInput = {
  id?: InputMaybe<Scalars['String']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
  on?: InputMaybe<Scalars['Boolean']['input']>;
};

/** update columns of table "domestic.amplifiers" */
export enum DomesticAmplifiersUpdateColumn {
  /** column name */
  Id = 'id',
  /** column name */
  Name = 'name',
  /** column name */
  On = 'on'
}

export type DomesticAmplifiersUpdates = {
  /** sets the columns of the filtered rows to the given values */
  _set?: InputMaybe<DomesticAmplifiersSetInput>;
  /** filter the rows which have to be updated */
  where: DomesticAmplifiersBoolExp;
};

/** columns and relationships of "domestic.blinds" */
export type DomesticBlinds = {
  __typename?: 'DomesticBlinds';
  group?: Maybe<Scalars['String']['output']>;
  id: Scalars['String']['output'];
  level?: Maybe<Scalars['Float']['output']>;
  name?: Maybe<Scalars['String']['output']>;
  opacity?: Maybe<Scalars['String']['output']>;
  /** An object relationship */
  room?: Maybe<DomesticRooms>;
  roomId?: Maybe<Scalars['String']['output']>;
};

/** aggregated selection of "domestic.blinds" */
export type DomesticBlindsAggregate = {
  __typename?: 'DomesticBlindsAggregate';
  aggregate?: Maybe<DomesticBlindsAggregateFields>;
  nodes: Array<DomesticBlinds>;
};

export type DomesticBlindsAggregateBoolExp = {
  count?: InputMaybe<DomesticBlindsAggregateBoolExpCount>;
};

/** aggregate fields of "domestic.blinds" */
export type DomesticBlindsAggregateFields = {
  __typename?: 'DomesticBlindsAggregateFields';
  avg?: Maybe<DomesticBlindsAvgFields>;
  count: Scalars['Int']['output'];
  max?: Maybe<DomesticBlindsMaxFields>;
  min?: Maybe<DomesticBlindsMinFields>;
  stddev?: Maybe<DomesticBlindsStddevFields>;
  stddevPop?: Maybe<DomesticBlindsStddevPopFields>;
  stddevSamp?: Maybe<DomesticBlindsStddevSampFields>;
  sum?: Maybe<DomesticBlindsSumFields>;
  varPop?: Maybe<DomesticBlindsVarPopFields>;
  varSamp?: Maybe<DomesticBlindsVarSampFields>;
  variance?: Maybe<DomesticBlindsVarianceFields>;
};


/** aggregate fields of "domestic.blinds" */
export type DomesticBlindsAggregateFieldsCountArgs = {
  columns?: InputMaybe<Array<DomesticBlindsSelectColumn>>;
  distinct?: InputMaybe<Scalars['Boolean']['input']>;
};

/** order by aggregate values of table "domestic.blinds" */
export type DomesticBlindsAggregateOrderBy = {
  avg?: InputMaybe<DomesticBlindsAvgOrderBy>;
  count?: InputMaybe<OrderBy>;
  max?: InputMaybe<DomesticBlindsMaxOrderBy>;
  min?: InputMaybe<DomesticBlindsMinOrderBy>;
  stddev?: InputMaybe<DomesticBlindsStddevOrderBy>;
  stddevPop?: InputMaybe<DomesticBlindsStddevPopOrderBy>;
  stddevSamp?: InputMaybe<DomesticBlindsStddevSampOrderBy>;
  sum?: InputMaybe<DomesticBlindsSumOrderBy>;
  varPop?: InputMaybe<DomesticBlindsVarPopOrderBy>;
  varSamp?: InputMaybe<DomesticBlindsVarSampOrderBy>;
  variance?: InputMaybe<DomesticBlindsVarianceOrderBy>;
};

/** input type for inserting array relation for remote table "domestic.blinds" */
export type DomesticBlindsArrRelInsertInput = {
  data: Array<DomesticBlindsInsertInput>;
  /** upsert condition */
  onConflict?: InputMaybe<DomesticBlindsOnConflict>;
};

/** aggregate avg on columns */
export type DomesticBlindsAvgFields = {
  __typename?: 'DomesticBlindsAvgFields';
  level?: Maybe<Scalars['Float']['output']>;
};

/** order by avg() on columns of table "domestic.blinds" */
export type DomesticBlindsAvgOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** Boolean expression to filter rows from the table "domestic.blinds". All fields are combined with a logical 'AND'. */
export type DomesticBlindsBoolExp = {
  _and?: InputMaybe<Array<DomesticBlindsBoolExp>>;
  _not?: InputMaybe<DomesticBlindsBoolExp>;
  _or?: InputMaybe<Array<DomesticBlindsBoolExp>>;
  group?: InputMaybe<StringComparisonExp>;
  id?: InputMaybe<StringComparisonExp>;
  level?: InputMaybe<FloatComparisonExp>;
  name?: InputMaybe<StringComparisonExp>;
  opacity?: InputMaybe<StringComparisonExp>;
  room?: InputMaybe<DomesticRoomsBoolExp>;
  roomId?: InputMaybe<StringComparisonExp>;
};

/** unique or primary key constraints on table "domestic.blinds" */
export enum DomesticBlindsConstraint {
  /** unique or primary key constraint on columns "id" */
  BlindsPkey = 'blinds_pkey'
}

/** input type for incrementing numeric columns in table "domestic.blinds" */
export type DomesticBlindsIncInput = {
  level?: InputMaybe<Scalars['Float']['input']>;
};

/** input type for inserting data into table "domestic.blinds" */
export type DomesticBlindsInsertInput = {
  group?: InputMaybe<Scalars['String']['input']>;
  id?: InputMaybe<Scalars['String']['input']>;
  level?: InputMaybe<Scalars['Float']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
  opacity?: InputMaybe<Scalars['String']['input']>;
  room?: InputMaybe<DomesticRoomsObjRelInsertInput>;
  roomId?: InputMaybe<Scalars['String']['input']>;
};

/** aggregate max on columns */
export type DomesticBlindsMaxFields = {
  __typename?: 'DomesticBlindsMaxFields';
  group?: Maybe<Scalars['String']['output']>;
  id?: Maybe<Scalars['String']['output']>;
  level?: Maybe<Scalars['Float']['output']>;
  name?: Maybe<Scalars['String']['output']>;
  opacity?: Maybe<Scalars['String']['output']>;
  roomId?: Maybe<Scalars['String']['output']>;
};

/** order by max() on columns of table "domestic.blinds" */
export type DomesticBlindsMaxOrderBy = {
  group?: InputMaybe<OrderBy>;
  id?: InputMaybe<OrderBy>;
  level?: InputMaybe<OrderBy>;
  name?: InputMaybe<OrderBy>;
  opacity?: InputMaybe<OrderBy>;
  roomId?: InputMaybe<OrderBy>;
};

/** aggregate min on columns */
export type DomesticBlindsMinFields = {
  __typename?: 'DomesticBlindsMinFields';
  group?: Maybe<Scalars['String']['output']>;
  id?: Maybe<Scalars['String']['output']>;
  level?: Maybe<Scalars['Float']['output']>;
  name?: Maybe<Scalars['String']['output']>;
  opacity?: Maybe<Scalars['String']['output']>;
  roomId?: Maybe<Scalars['String']['output']>;
};

/** order by min() on columns of table "domestic.blinds" */
export type DomesticBlindsMinOrderBy = {
  group?: InputMaybe<OrderBy>;
  id?: InputMaybe<OrderBy>;
  level?: InputMaybe<OrderBy>;
  name?: InputMaybe<OrderBy>;
  opacity?: InputMaybe<OrderBy>;
  roomId?: InputMaybe<OrderBy>;
};

/** response of any mutation on the table "domestic.blinds" */
export type DomesticBlindsMutationResponse = {
  __typename?: 'DomesticBlindsMutationResponse';
  /** number of rows affected by the mutation */
  affectedRows: Scalars['Int']['output'];
  /** data from the rows affected by the mutation */
  returning: Array<DomesticBlinds>;
};

/** on_conflict condition type for table "domestic.blinds" */
export type DomesticBlindsOnConflict = {
  constraint: DomesticBlindsConstraint;
  updateColumns?: Array<DomesticBlindsUpdateColumn>;
  where?: InputMaybe<DomesticBlindsBoolExp>;
};

/** Ordering options when selecting data from "domestic.blinds". */
export type DomesticBlindsOrderBy = {
  group?: InputMaybe<OrderBy>;
  id?: InputMaybe<OrderBy>;
  level?: InputMaybe<OrderBy>;
  name?: InputMaybe<OrderBy>;
  opacity?: InputMaybe<OrderBy>;
  room?: InputMaybe<DomesticRoomsOrderBy>;
  roomId?: InputMaybe<OrderBy>;
};

/** primary key columns input for table: domestic.blinds */
export type DomesticBlindsPkColumnsInput = {
  id: Scalars['String']['input'];
};

/** select columns of table "domestic.blinds" */
export enum DomesticBlindsSelectColumn {
  /** column name */
  Group = 'group',
  /** column name */
  Id = 'id',
  /** column name */
  Level = 'level',
  /** column name */
  Name = 'name',
  /** column name */
  Opacity = 'opacity',
  /** column name */
  RoomId = 'roomId'
}

/** input type for updating data in table "domestic.blinds" */
export type DomesticBlindsSetInput = {
  group?: InputMaybe<Scalars['String']['input']>;
  id?: InputMaybe<Scalars['String']['input']>;
  level?: InputMaybe<Scalars['Float']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
  opacity?: InputMaybe<Scalars['String']['input']>;
  roomId?: InputMaybe<Scalars['String']['input']>;
};

/** aggregate stddev on columns */
export type DomesticBlindsStddevFields = {
  __typename?: 'DomesticBlindsStddevFields';
  level?: Maybe<Scalars['Float']['output']>;
};

/** order by stddev() on columns of table "domestic.blinds" */
export type DomesticBlindsStddevOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** aggregate stddevPop on columns */
export type DomesticBlindsStddevPopFields = {
  __typename?: 'DomesticBlindsStddevPopFields';
  level?: Maybe<Scalars['Float']['output']>;
};

/** order by stddevPop() on columns of table "domestic.blinds" */
export type DomesticBlindsStddevPopOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** aggregate stddevSamp on columns */
export type DomesticBlindsStddevSampFields = {
  __typename?: 'DomesticBlindsStddevSampFields';
  level?: Maybe<Scalars['Float']['output']>;
};

/** order by stddevSamp() on columns of table "domestic.blinds" */
export type DomesticBlindsStddevSampOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** Streaming cursor of the table "domestic_blinds" */
export type DomesticBlindsStreamCursorInput = {
  /** Stream column input with initial value */
  initialValue: DomesticBlindsStreamCursorValueInput;
  /** cursor ordering */
  ordering?: InputMaybe<CursorOrdering>;
};

/** Initial value of the column from where the streaming should start */
export type DomesticBlindsStreamCursorValueInput = {
  group?: InputMaybe<Scalars['String']['input']>;
  id?: InputMaybe<Scalars['String']['input']>;
  level?: InputMaybe<Scalars['Float']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
  opacity?: InputMaybe<Scalars['String']['input']>;
  roomId?: InputMaybe<Scalars['String']['input']>;
};

/** aggregate sum on columns */
export type DomesticBlindsSumFields = {
  __typename?: 'DomesticBlindsSumFields';
  level?: Maybe<Scalars['Float']['output']>;
};

/** order by sum() on columns of table "domestic.blinds" */
export type DomesticBlindsSumOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** update columns of table "domestic.blinds" */
export enum DomesticBlindsUpdateColumn {
  /** column name */
  Group = 'group',
  /** column name */
  Id = 'id',
  /** column name */
  Level = 'level',
  /** column name */
  Name = 'name',
  /** column name */
  Opacity = 'opacity',
  /** column name */
  RoomId = 'roomId'
}

export type DomesticBlindsUpdates = {
  /** increments the numeric columns with given value of the filtered values */
  _inc?: InputMaybe<DomesticBlindsIncInput>;
  /** sets the columns of the filtered rows to the given values */
  _set?: InputMaybe<DomesticBlindsSetInput>;
  /** filter the rows which have to be updated */
  where: DomesticBlindsBoolExp;
};

/** aggregate varPop on columns */
export type DomesticBlindsVarPopFields = {
  __typename?: 'DomesticBlindsVarPopFields';
  level?: Maybe<Scalars['Float']['output']>;
};

/** order by varPop() on columns of table "domestic.blinds" */
export type DomesticBlindsVarPopOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** aggregate varSamp on columns */
export type DomesticBlindsVarSampFields = {
  __typename?: 'DomesticBlindsVarSampFields';
  level?: Maybe<Scalars['Float']['output']>;
};

/** order by varSamp() on columns of table "domestic.blinds" */
export type DomesticBlindsVarSampOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** aggregate variance on columns */
export type DomesticBlindsVarianceFields = {
  __typename?: 'DomesticBlindsVarianceFields';
  level?: Maybe<Scalars['Float']['output']>;
};

/** order by variance() on columns of table "domestic.blinds" */
export type DomesticBlindsVarianceOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** columns and relationships of "domestic.lighting_groups" */
export type DomesticLightingGroups = {
  __typename?: 'DomesticLightingGroups';
  id: Scalars['String']['output'];
  level?: Maybe<Scalars['Float']['output']>;
  name?: Maybe<Scalars['String']['output']>;
  /** An object relationship */
  room?: Maybe<DomesticRooms>;
  roomId?: Maybe<Scalars['String']['output']>;
};

/** aggregated selection of "domestic.lighting_groups" */
export type DomesticLightingGroupsAggregate = {
  __typename?: 'DomesticLightingGroupsAggregate';
  aggregate?: Maybe<DomesticLightingGroupsAggregateFields>;
  nodes: Array<DomesticLightingGroups>;
};

export type DomesticLightingGroupsAggregateBoolExp = {
  count?: InputMaybe<DomesticLightingGroupsAggregateBoolExpCount>;
};

/** aggregate fields of "domestic.lighting_groups" */
export type DomesticLightingGroupsAggregateFields = {
  __typename?: 'DomesticLightingGroupsAggregateFields';
  avg?: Maybe<DomesticLightingGroupsAvgFields>;
  count: Scalars['Int']['output'];
  max?: Maybe<DomesticLightingGroupsMaxFields>;
  min?: Maybe<DomesticLightingGroupsMinFields>;
  stddev?: Maybe<DomesticLightingGroupsStddevFields>;
  stddevPop?: Maybe<DomesticLightingGroupsStddevPopFields>;
  stddevSamp?: Maybe<DomesticLightingGroupsStddevSampFields>;
  sum?: Maybe<DomesticLightingGroupsSumFields>;
  varPop?: Maybe<DomesticLightingGroupsVarPopFields>;
  varSamp?: Maybe<DomesticLightingGroupsVarSampFields>;
  variance?: Maybe<DomesticLightingGroupsVarianceFields>;
};


/** aggregate fields of "domestic.lighting_groups" */
export type DomesticLightingGroupsAggregateFieldsCountArgs = {
  columns?: InputMaybe<Array<DomesticLightingGroupsSelectColumn>>;
  distinct?: InputMaybe<Scalars['Boolean']['input']>;
};

/** order by aggregate values of table "domestic.lighting_groups" */
export type DomesticLightingGroupsAggregateOrderBy = {
  avg?: InputMaybe<DomesticLightingGroupsAvgOrderBy>;
  count?: InputMaybe<OrderBy>;
  max?: InputMaybe<DomesticLightingGroupsMaxOrderBy>;
  min?: InputMaybe<DomesticLightingGroupsMinOrderBy>;
  stddev?: InputMaybe<DomesticLightingGroupsStddevOrderBy>;
  stddevPop?: InputMaybe<DomesticLightingGroupsStddevPopOrderBy>;
  stddevSamp?: InputMaybe<DomesticLightingGroupsStddevSampOrderBy>;
  sum?: InputMaybe<DomesticLightingGroupsSumOrderBy>;
  varPop?: InputMaybe<DomesticLightingGroupsVarPopOrderBy>;
  varSamp?: InputMaybe<DomesticLightingGroupsVarSampOrderBy>;
  variance?: InputMaybe<DomesticLightingGroupsVarianceOrderBy>;
};

/** input type for inserting array relation for remote table "domestic.lighting_groups" */
export type DomesticLightingGroupsArrRelInsertInput = {
  data: Array<DomesticLightingGroupsInsertInput>;
  /** upsert condition */
  onConflict?: InputMaybe<DomesticLightingGroupsOnConflict>;
};

/** aggregate avg on columns */
export type DomesticLightingGroupsAvgFields = {
  __typename?: 'DomesticLightingGroupsAvgFields';
  level?: Maybe<Scalars['Float']['output']>;
};

/** order by avg() on columns of table "domestic.lighting_groups" */
export type DomesticLightingGroupsAvgOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** Boolean expression to filter rows from the table "domestic.lighting_groups". All fields are combined with a logical 'AND'. */
export type DomesticLightingGroupsBoolExp = {
  _and?: InputMaybe<Array<DomesticLightingGroupsBoolExp>>;
  _not?: InputMaybe<DomesticLightingGroupsBoolExp>;
  _or?: InputMaybe<Array<DomesticLightingGroupsBoolExp>>;
  id?: InputMaybe<StringComparisonExp>;
  level?: InputMaybe<FloatComparisonExp>;
  name?: InputMaybe<StringComparisonExp>;
  room?: InputMaybe<DomesticRoomsBoolExp>;
  roomId?: InputMaybe<StringComparisonExp>;
};

/** unique or primary key constraints on table "domestic.lighting_groups" */
export enum DomesticLightingGroupsConstraint {
  /** unique or primary key constraint on columns "id" */
  LightingGroupsPkey = 'lighting_groups_pkey'
}

/** input type for incrementing numeric columns in table "domestic.lighting_groups" */
export type DomesticLightingGroupsIncInput = {
  level?: InputMaybe<Scalars['Float']['input']>;
};

/** input type for inserting data into table "domestic.lighting_groups" */
export type DomesticLightingGroupsInsertInput = {
  id?: InputMaybe<Scalars['String']['input']>;
  level?: InputMaybe<Scalars['Float']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
  room?: InputMaybe<DomesticRoomsObjRelInsertInput>;
  roomId?: InputMaybe<Scalars['String']['input']>;
};

/** aggregate max on columns */
export type DomesticLightingGroupsMaxFields = {
  __typename?: 'DomesticLightingGroupsMaxFields';
  id?: Maybe<Scalars['String']['output']>;
  level?: Maybe<Scalars['Float']['output']>;
  name?: Maybe<Scalars['String']['output']>;
  roomId?: Maybe<Scalars['String']['output']>;
};

/** order by max() on columns of table "domestic.lighting_groups" */
export type DomesticLightingGroupsMaxOrderBy = {
  id?: InputMaybe<OrderBy>;
  level?: InputMaybe<OrderBy>;
  name?: InputMaybe<OrderBy>;
  roomId?: InputMaybe<OrderBy>;
};

/** aggregate min on columns */
export type DomesticLightingGroupsMinFields = {
  __typename?: 'DomesticLightingGroupsMinFields';
  id?: Maybe<Scalars['String']['output']>;
  level?: Maybe<Scalars['Float']['output']>;
  name?: Maybe<Scalars['String']['output']>;
  roomId?: Maybe<Scalars['String']['output']>;
};

/** order by min() on columns of table "domestic.lighting_groups" */
export type DomesticLightingGroupsMinOrderBy = {
  id?: InputMaybe<OrderBy>;
  level?: InputMaybe<OrderBy>;
  name?: InputMaybe<OrderBy>;
  roomId?: InputMaybe<OrderBy>;
};

/** response of any mutation on the table "domestic.lighting_groups" */
export type DomesticLightingGroupsMutationResponse = {
  __typename?: 'DomesticLightingGroupsMutationResponse';
  /** number of rows affected by the mutation */
  affectedRows: Scalars['Int']['output'];
  /** data from the rows affected by the mutation */
  returning: Array<DomesticLightingGroups>;
};

/** on_conflict condition type for table "domestic.lighting_groups" */
export type DomesticLightingGroupsOnConflict = {
  constraint: DomesticLightingGroupsConstraint;
  updateColumns?: Array<DomesticLightingGroupsUpdateColumn>;
  where?: InputMaybe<DomesticLightingGroupsBoolExp>;
};

/** Ordering options when selecting data from "domestic.lighting_groups". */
export type DomesticLightingGroupsOrderBy = {
  id?: InputMaybe<OrderBy>;
  level?: InputMaybe<OrderBy>;
  name?: InputMaybe<OrderBy>;
  room?: InputMaybe<DomesticRoomsOrderBy>;
  roomId?: InputMaybe<OrderBy>;
};

/** primary key columns input for table: domestic.lighting_groups */
export type DomesticLightingGroupsPkColumnsInput = {
  id: Scalars['String']['input'];
};

/** select columns of table "domestic.lighting_groups" */
export enum DomesticLightingGroupsSelectColumn {
  /** column name */
  Id = 'id',
  /** column name */
  Level = 'level',
  /** column name */
  Name = 'name',
  /** column name */
  RoomId = 'roomId'
}

/** input type for updating data in table "domestic.lighting_groups" */
export type DomesticLightingGroupsSetInput = {
  id?: InputMaybe<Scalars['String']['input']>;
  level?: InputMaybe<Scalars['Float']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
  roomId?: InputMaybe<Scalars['String']['input']>;
};

/** aggregate stddev on columns */
export type DomesticLightingGroupsStddevFields = {
  __typename?: 'DomesticLightingGroupsStddevFields';
  level?: Maybe<Scalars['Float']['output']>;
};

/** order by stddev() on columns of table "domestic.lighting_groups" */
export type DomesticLightingGroupsStddevOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** aggregate stddevPop on columns */
export type DomesticLightingGroupsStddevPopFields = {
  __typename?: 'DomesticLightingGroupsStddevPopFields';
  level?: Maybe<Scalars['Float']['output']>;
};

/** order by stddevPop() on columns of table "domestic.lighting_groups" */
export type DomesticLightingGroupsStddevPopOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** aggregate stddevSamp on columns */
export type DomesticLightingGroupsStddevSampFields = {
  __typename?: 'DomesticLightingGroupsStddevSampFields';
  level?: Maybe<Scalars['Float']['output']>;
};

/** order by stddevSamp() on columns of table "domestic.lighting_groups" */
export type DomesticLightingGroupsStddevSampOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** Streaming cursor of the table "domestic_lighting_groups" */
export type DomesticLightingGroupsStreamCursorInput = {
  /** Stream column input with initial value */
  initialValue: DomesticLightingGroupsStreamCursorValueInput;
  /** cursor ordering */
  ordering?: InputMaybe<CursorOrdering>;
};

/** Initial value of the column from where the streaming should start */
export type DomesticLightingGroupsStreamCursorValueInput = {
  id?: InputMaybe<Scalars['String']['input']>;
  level?: InputMaybe<Scalars['Float']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
  roomId?: InputMaybe<Scalars['String']['input']>;
};

/** aggregate sum on columns */
export type DomesticLightingGroupsSumFields = {
  __typename?: 'DomesticLightingGroupsSumFields';
  level?: Maybe<Scalars['Float']['output']>;
};

/** order by sum() on columns of table "domestic.lighting_groups" */
export type DomesticLightingGroupsSumOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** update columns of table "domestic.lighting_groups" */
export enum DomesticLightingGroupsUpdateColumn {
  /** column name */
  Id = 'id',
  /** column name */
  Level = 'level',
  /** column name */
  Name = 'name',
  /** column name */
  RoomId = 'roomId'
}

export type DomesticLightingGroupsUpdates = {
  /** increments the numeric columns with given value of the filtered values */
  _inc?: InputMaybe<DomesticLightingGroupsIncInput>;
  /** sets the columns of the filtered rows to the given values */
  _set?: InputMaybe<DomesticLightingGroupsSetInput>;
  /** filter the rows which have to be updated */
  where: DomesticLightingGroupsBoolExp;
};

/** aggregate varPop on columns */
export type DomesticLightingGroupsVarPopFields = {
  __typename?: 'DomesticLightingGroupsVarPopFields';
  level?: Maybe<Scalars['Float']['output']>;
};

/** order by varPop() on columns of table "domestic.lighting_groups" */
export type DomesticLightingGroupsVarPopOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** aggregate varSamp on columns */
export type DomesticLightingGroupsVarSampFields = {
  __typename?: 'DomesticLightingGroupsVarSampFields';
  level?: Maybe<Scalars['Float']['output']>;
};

/** order by varSamp() on columns of table "domestic.lighting_groups" */
export type DomesticLightingGroupsVarSampOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** aggregate variance on columns */
export type DomesticLightingGroupsVarianceFields = {
  __typename?: 'DomesticLightingGroupsVarianceFields';
  level?: Maybe<Scalars['Float']['output']>;
};

/** order by variance() on columns of table "domestic.lighting_groups" */
export type DomesticLightingGroupsVarianceOrderBy = {
  level?: InputMaybe<OrderBy>;
};

/** columns and relationships of "domestic.rooms" */
export type DomesticRooms = {
  __typename?: 'DomesticRooms';
  /** An object relationship */
  airConditioning?: Maybe<DomesticAirConditioning>;
  airConditioningLog: Array<AcLogType>;
  /** An object relationship */
  amplifier?: Maybe<DomesticAmplifiers>;
  amplifiersLog: Array<AmplifiersLogType>;
  /** An array relationship */
  blinds: Array<DomesticBlinds>;
  /** An aggregate relationship */
  blindsAggregate: DomesticBlindsAggregate;
  blindsLog: Array<BlindsLogType>;
  group?: Maybe<Scalars['String']['output']>;
  id: Scalars['String']['output'];
  /** An array relationship */
  lightingGroups: Array<DomesticLightingGroups>;
  /** An aggregate relationship */
  lightingGroupsAggregate: DomesticLightingGroupsAggregate;
  lightingGroupsLog: Array<LightingGroupsLogType>;
  name?: Maybe<Scalars['String']['output']>;
  /** An object relationship */
  ventilation?: Maybe<DomesticVentilation>;
  ventilationLog: Array<VentilationLogType>;
};


/** columns and relationships of "domestic.rooms" */
export type DomesticRoomsAirConditioningLogArgs = {
  period: TimePeriod;
};


/** columns and relationships of "domestic.rooms" */
export type DomesticRoomsAmplifiersLogArgs = {
  period: TimePeriod;
};


/** columns and relationships of "domestic.rooms" */
export type DomesticRoomsBlindsArgs = {
  distinctOn?: InputMaybe<Array<DomesticBlindsSelectColumn>>;
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
  orderBy?: InputMaybe<Array<DomesticBlindsOrderBy>>;
  where?: InputMaybe<DomesticBlindsBoolExp>;
};


/** columns and relationships of "domestic.rooms" */
export type DomesticRoomsBlindsAggregateArgs = {
  distinctOn?: InputMaybe<Array<DomesticBlindsSelectColumn>>;
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
  orderBy?: InputMaybe<Array<DomesticBlindsOrderBy>>;
  where?: InputMaybe<DomesticBlindsBoolExp>;
};


/** columns and relationships of "domestic.rooms" */
export type DomesticRoomsBlindsLogArgs = {
  period: TimePeriod;
};


/** columns and relationships of "domestic.rooms" */
export type DomesticRoomsLightingGroupsArgs = {
  distinctOn?: InputMaybe<Array<DomesticLightingGroupsSelectColumn>>;
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
  orderBy?: InputMaybe<Array<DomesticLightingGroupsOrderBy>>;
  where?: InputMaybe<DomesticLightingGroupsBoolExp>;
};


/** columns and relationships of "domestic.rooms" */
export type DomesticRoomsLightingGroupsAggregateArgs = {
  distinctOn?: InputMaybe<Array<DomesticLightingGroupsSelectColumn>>;
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
  orderBy?: InputMaybe<Array<DomesticLightingGroupsOrderBy>>;
  where?: InputMaybe<DomesticLightingGroupsBoolExp>;
};


/** columns and relationships of "domestic.rooms" */
export type DomesticRoomsLightingGroupsLogArgs = {
  period: TimePeriod;
};


/** columns and relationships of "domestic.rooms" */
export type DomesticRoomsVentilationLogArgs = {
  period: TimePeriod;
};

/** aggregated selection of "domestic.rooms" */
export type DomesticRoomsAggregate = {
  __typename?: 'DomesticRoomsAggregate';
  aggregate?: Maybe<DomesticRoomsAggregateFields>;
  nodes: Array<DomesticRooms>;
};

/** aggregate fields of "domestic.rooms" */
export type DomesticRoomsAggregateFields = {
  __typename?: 'DomesticRoomsAggregateFields';
  count: Scalars['Int']['output'];
  max?: Maybe<DomesticRoomsMaxFields>;
  min?: Maybe<DomesticRoomsMinFields>;
};


/** aggregate fields of "domestic.rooms" */
export type DomesticRoomsAggregateFieldsCountArgs = {
  columns?: InputMaybe<Array<DomesticRoomsSelectColumn>>;
  distinct?: InputMaybe<Scalars['Boolean']['input']>;
};

/** Boolean expression to filter rows from the table "domestic.rooms". All fields are combined with a logical 'AND'. */
export type DomesticRoomsBoolExp = {
  _and?: InputMaybe<Array<DomesticRoomsBoolExp>>;
  _not?: InputMaybe<DomesticRoomsBoolExp>;
  _or?: InputMaybe<Array<DomesticRoomsBoolExp>>;
  airConditioning?: InputMaybe<DomesticAirConditioningBoolExp>;
  amplifier?: InputMaybe<DomesticAmplifiersBoolExp>;
  blinds?: InputMaybe<DomesticBlindsBoolExp>;
  blindsAggregate?: InputMaybe<DomesticBlindsAggregateBoolExp>;
  group?: InputMaybe<StringComparisonExp>;
  id?: InputMaybe<StringComparisonExp>;
  lightingGroups?: InputMaybe<DomesticLightingGroupsBoolExp>;
  lightingGroupsAggregate?: InputMaybe<DomesticLightingGroupsAggregateBoolExp>;
  name?: InputMaybe<StringComparisonExp>;
  ventilation?: InputMaybe<DomesticVentilationBoolExp>;
};

/** unique or primary key constraints on table "domestic.rooms" */
export enum DomesticRoomsConstraint {
  /** unique or primary key constraint on columns "id" */
  RoomsPkey = 'rooms_pkey'
}

/** input type for inserting data into table "domestic.rooms" */
export type DomesticRoomsInsertInput = {
  airConditioning?: InputMaybe<DomesticAirConditioningObjRelInsertInput>;
  amplifier?: InputMaybe<DomesticAmplifiersObjRelInsertInput>;
  blinds?: InputMaybe<DomesticBlindsArrRelInsertInput>;
  group?: InputMaybe<Scalars['String']['input']>;
  id?: InputMaybe<Scalars['String']['input']>;
  lightingGroups?: InputMaybe<DomesticLightingGroupsArrRelInsertInput>;
  name?: InputMaybe<Scalars['String']['input']>;
  ventilation?: InputMaybe<DomesticVentilationObjRelInsertInput>;
};

/** aggregate max on columns */
export type DomesticRoomsMaxFields = {
  __typename?: 'DomesticRoomsMaxFields';
  group?: Maybe<Scalars['String']['output']>;
  id?: Maybe<Scalars['String']['output']>;
  name?: Maybe<Scalars['String']['output']>;
};

/** aggregate min on columns */
export type DomesticRoomsMinFields = {
  __typename?: 'DomesticRoomsMinFields';
  group?: Maybe<Scalars['String']['output']>;
  id?: Maybe<Scalars['String']['output']>;
  name?: Maybe<Scalars['String']['output']>;
};

/** response of any mutation on the table "domestic.rooms" */
export type DomesticRoomsMutationResponse = {
  __typename?: 'DomesticRoomsMutationResponse';
  /** number of rows affected by the mutation */
  affectedRows: Scalars['Int']['output'];
  /** data from the rows affected by the mutation */
  returning: Array<DomesticRooms>;
};

/** input type for inserting object relation for remote table "domestic.rooms" */
export type DomesticRoomsObjRelInsertInput = {
  data: DomesticRoomsInsertInput;
  /** upsert condition */
  onConflict?: InputMaybe<DomesticRoomsOnConflict>;
};

/** on_conflict condition type for table "domestic.rooms" */
export type DomesticRoomsOnConflict = {
  constraint: DomesticRoomsConstraint;
  updateColumns?: Array<DomesticRoomsUpdateColumn>;
  where?: InputMaybe<DomesticRoomsBoolExp>;
};

/** Ordering options when selecting data from "domestic.rooms". */
export type DomesticRoomsOrderBy = {
  airConditioning?: InputMaybe<DomesticAirConditioningOrderBy>;
  amplifier?: InputMaybe<DomesticAmplifiersOrderBy>;
  blindsAggregate?: InputMaybe<DomesticBlindsAggregateOrderBy>;
  group?: InputMaybe<OrderBy>;
  id?: InputMaybe<OrderBy>;
  lightingGroupsAggregate?: InputMaybe<DomesticLightingGroupsAggregateOrderBy>;
  name?: InputMaybe<OrderBy>;
  ventilation?: InputMaybe<DomesticVentilationOrderBy>;
};

/** primary key columns input for table: domestic.rooms */
export type DomesticRoomsPkColumnsInput = {
  id: Scalars['String']['input'];
};

/** select columns of table "domestic.rooms" */
export enum DomesticRoomsSelectColumn {
  /** column name */
  Group = 'group',
  /** column name */
  Id = 'id',
  /** column name */
  Name = 'name'
}

/** input type for updating data in table "domestic.rooms" */
export type DomesticRoomsSetInput = {
  group?: InputMaybe<Scalars['String']['input']>;
  id?: InputMaybe<Scalars['String']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
};

/** Streaming cursor of the table "domestic_rooms" */
export type DomesticRoomsStreamCursorInput = {
  /** Stream column input with initial value */
  initialValue: DomesticRoomsStreamCursorValueInput;
  /** cursor ordering */
  ordering?: InputMaybe<CursorOrdering>;
};

/** Initial value of the column from where the streaming should start */
export type DomesticRoomsStreamCursorValueInput = {
  group?: InputMaybe<Scalars['String']['input']>;
  id?: InputMaybe<Scalars['String']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
};

/** update columns of table "domestic.rooms" */
export enum DomesticRoomsUpdateColumn {
  /** column name */
  Group = 'group',
  /** column name */
  Id = 'id',
  /** column name */
  Name = 'name'
}

export type DomesticRoomsUpdates = {
  /** sets the columns of the filtered rows to the given values */
  _set?: InputMaybe<DomesticRoomsSetInput>;
  /** filter the rows which have to be updated */
  where: DomesticRoomsBoolExp;
};

/** columns and relationships of "domestic.ventilation" */
export type DomesticVentilation = {
  __typename?: 'DomesticVentilation';
  actualCo2?: Maybe<Scalars['Float']['output']>;
  co2Setpoint?: Maybe<Scalars['Float']['output']>;
  id: Scalars['String']['output'];
  /** An object relationship */
  room: DomesticRooms;
};

/** aggregated selection of "domestic.ventilation" */
export type DomesticVentilationAggregate = {
  __typename?: 'DomesticVentilationAggregate';
  aggregate?: Maybe<DomesticVentilationAggregateFields>;
  nodes: Array<DomesticVentilation>;
};

/** aggregate fields of "domestic.ventilation" */
export type DomesticVentilationAggregateFields = {
  __typename?: 'DomesticVentilationAggregateFields';
  avg?: Maybe<DomesticVentilationAvgFields>;
  count: Scalars['Int']['output'];
  max?: Maybe<DomesticVentilationMaxFields>;
  min?: Maybe<DomesticVentilationMinFields>;
  stddev?: Maybe<DomesticVentilationStddevFields>;
  stddevPop?: Maybe<DomesticVentilationStddevPopFields>;
  stddevSamp?: Maybe<DomesticVentilationStddevSampFields>;
  sum?: Maybe<DomesticVentilationSumFields>;
  varPop?: Maybe<DomesticVentilationVarPopFields>;
  varSamp?: Maybe<DomesticVentilationVarSampFields>;
  variance?: Maybe<DomesticVentilationVarianceFields>;
};


/** aggregate fields of "domestic.ventilation" */
export type DomesticVentilationAggregateFieldsCountArgs = {
  columns?: InputMaybe<Array<DomesticVentilationSelectColumn>>;
  distinct?: InputMaybe<Scalars['Boolean']['input']>;
};

/** aggregate avg on columns */
export type DomesticVentilationAvgFields = {
  __typename?: 'DomesticVentilationAvgFields';
  actualCo2?: Maybe<Scalars['Float']['output']>;
  co2Setpoint?: Maybe<Scalars['Float']['output']>;
};

/** Boolean expression to filter rows from the table "domestic.ventilation". All fields are combined with a logical 'AND'. */
export type DomesticVentilationBoolExp = {
  _and?: InputMaybe<Array<DomesticVentilationBoolExp>>;
  _not?: InputMaybe<DomesticVentilationBoolExp>;
  _or?: InputMaybe<Array<DomesticVentilationBoolExp>>;
  actualCo2?: InputMaybe<FloatComparisonExp>;
  co2Setpoint?: InputMaybe<FloatComparisonExp>;
  id?: InputMaybe<StringComparisonExp>;
  room?: InputMaybe<DomesticRoomsBoolExp>;
};

/** unique or primary key constraints on table "domestic.ventilation" */
export enum DomesticVentilationConstraint {
  /** unique or primary key constraint on columns "id" */
  VentilationPkey = 'ventilation_pkey'
}

/** input type for incrementing numeric columns in table "domestic.ventilation" */
export type DomesticVentilationIncInput = {
  actualCo2?: InputMaybe<Scalars['Float']['input']>;
  co2Setpoint?: InputMaybe<Scalars['Float']['input']>;
};

/** input type for inserting data into table "domestic.ventilation" */
export type DomesticVentilationInsertInput = {
  actualCo2?: InputMaybe<Scalars['Float']['input']>;
  co2Setpoint?: InputMaybe<Scalars['Float']['input']>;
  id?: InputMaybe<Scalars['String']['input']>;
  room?: InputMaybe<DomesticRoomsObjRelInsertInput>;
};

/** aggregate max on columns */
export type DomesticVentilationMaxFields = {
  __typename?: 'DomesticVentilationMaxFields';
  actualCo2?: Maybe<Scalars['Float']['output']>;
  co2Setpoint?: Maybe<Scalars['Float']['output']>;
  id?: Maybe<Scalars['String']['output']>;
};

/** aggregate min on columns */
export type DomesticVentilationMinFields = {
  __typename?: 'DomesticVentilationMinFields';
  actualCo2?: Maybe<Scalars['Float']['output']>;
  co2Setpoint?: Maybe<Scalars['Float']['output']>;
  id?: Maybe<Scalars['String']['output']>;
};

/** response of any mutation on the table "domestic.ventilation" */
export type DomesticVentilationMutationResponse = {
  __typename?: 'DomesticVentilationMutationResponse';
  /** number of rows affected by the mutation */
  affectedRows: Scalars['Int']['output'];
  /** data from the rows affected by the mutation */
  returning: Array<DomesticVentilation>;
};

/** input type for inserting object relation for remote table "domestic.ventilation" */
export type DomesticVentilationObjRelInsertInput = {
  data: DomesticVentilationInsertInput;
  /** upsert condition */
  onConflict?: InputMaybe<DomesticVentilationOnConflict>;
};

/** on_conflict condition type for table "domestic.ventilation" */
export type DomesticVentilationOnConflict = {
  constraint: DomesticVentilationConstraint;
  updateColumns?: Array<DomesticVentilationUpdateColumn>;
  where?: InputMaybe<DomesticVentilationBoolExp>;
};

/** Ordering options when selecting data from "domestic.ventilation". */
export type DomesticVentilationOrderBy = {
  actualCo2?: InputMaybe<OrderBy>;
  co2Setpoint?: InputMaybe<OrderBy>;
  id?: InputMaybe<OrderBy>;
  room?: InputMaybe<DomesticRoomsOrderBy>;
};

/** primary key columns input for table: domestic.ventilation */
export type DomesticVentilationPkColumnsInput = {
  id: Scalars['String']['input'];
};

/** select columns of table "domestic.ventilation" */
export enum DomesticVentilationSelectColumn {
  /** column name */
  ActualCo2 = 'actualCo2',
  /** column name */
  Co2Setpoint = 'co2Setpoint',
  /** column name */
  Id = 'id'
}

/** input type for updating data in table "domestic.ventilation" */
export type DomesticVentilationSetInput = {
  actualCo2?: InputMaybe<Scalars['Float']['input']>;
  co2Setpoint?: InputMaybe<Scalars['Float']['input']>;
  id?: InputMaybe<Scalars['String']['input']>;
};

/** aggregate stddev on columns */
export type DomesticVentilationStddevFields = {
  __typename?: 'DomesticVentilationStddevFields';
  actualCo2?: Maybe<Scalars['Float']['output']>;
  co2Setpoint?: Maybe<Scalars['Float']['output']>;
};

/** aggregate stddevPop on columns */
export type DomesticVentilationStddevPopFields = {
  __typename?: 'DomesticVentilationStddevPopFields';
  actualCo2?: Maybe<Scalars['Float']['output']>;
  co2Setpoint?: Maybe<Scalars['Float']['output']>;
};

/** aggregate stddevSamp on columns */
export type DomesticVentilationStddevSampFields = {
  __typename?: 'DomesticVentilationStddevSampFields';
  actualCo2?: Maybe<Scalars['Float']['output']>;
  co2Setpoint?: Maybe<Scalars['Float']['output']>;
};

/** Streaming cursor of the table "domestic_ventilation" */
export type DomesticVentilationStreamCursorInput = {
  /** Stream column input with initial value */
  initialValue: DomesticVentilationStreamCursorValueInput;
  /** cursor ordering */
  ordering?: InputMaybe<CursorOrdering>;
};

/** Initial value of the column from where the streaming should start */
export type DomesticVentilationStreamCursorValueInput = {
  actualCo2?: InputMaybe<Scalars['Float']['input']>;
  co2Setpoint?: InputMaybe<Scalars['Float']['input']>;
  id?: InputMaybe<Scalars['String']['input']>;
};

/** aggregate sum on columns */
export type DomesticVentilationSumFields = {
  __typename?: 'DomesticVentilationSumFields';
  actualCo2?: Maybe<Scalars['Float']['output']>;
  co2Setpoint?: Maybe<Scalars['Float']['output']>;
};

/** update columns of table "domestic.ventilation" */
export enum DomesticVentilationUpdateColumn {
  /** column name */
  ActualCo2 = 'actualCo2',
  /** column name */
  Co2Setpoint = 'co2Setpoint',
  /** column name */
  Id = 'id'
}

export type DomesticVentilationUpdates = {
  /** increments the numeric columns with given value of the filtered values */
  _inc?: InputMaybe<DomesticVentilationIncInput>;
  /** sets the columns of the filtered rows to the given values */
  _set?: InputMaybe<DomesticVentilationSetInput>;
  /** filter the rows which have to be updated */
  where: DomesticVentilationBoolExp;
};

/** aggregate varPop on columns */
export type DomesticVentilationVarPopFields = {
  __typename?: 'DomesticVentilationVarPopFields';
  actualCo2?: Maybe<Scalars['Float']['output']>;
  co2Setpoint?: Maybe<Scalars['Float']['output']>;
};

/** aggregate varSamp on columns */
export type DomesticVentilationVarSampFields = {
  __typename?: 'DomesticVentilationVarSampFields';
  actualCo2?: Maybe<Scalars['Float']['output']>;
  co2Setpoint?: Maybe<Scalars['Float']['output']>;
};

/** aggregate variance on columns */
export type DomesticVentilationVarianceFields = {
  __typename?: 'DomesticVentilationVarianceFields';
  actualCo2?: Maybe<Scalars['Float']['output']>;
  co2Setpoint?: Maybe<Scalars['Float']['output']>;
};

/** Boolean expression to compare columns of type "Float". All fields are combined with logical 'AND'. */
export type FloatComparisonExp = {
  _eq?: InputMaybe<Scalars['Float']['input']>;
  _gt?: InputMaybe<Scalars['Float']['input']>;
  _gte?: InputMaybe<Scalars['Float']['input']>;
  _in?: InputMaybe<Array<Scalars['Float']['input']>>;
  _isNull?: InputMaybe<Scalars['Boolean']['input']>;
  _lt?: InputMaybe<Scalars['Float']['input']>;
  _lte?: InputMaybe<Scalars['Float']['input']>;
  _neq?: InputMaybe<Scalars['Float']['input']>;
  _nin?: InputMaybe<Array<Scalars['Float']['input']>>;
};

/** Boolean expression to compare columns of type "Int". All fields are combined with logical 'AND'. */
export type IntComparisonExp = {
  _eq?: InputMaybe<Scalars['Int']['input']>;
  _gt?: InputMaybe<Scalars['Int']['input']>;
  _gte?: InputMaybe<Scalars['Int']['input']>;
  _in?: InputMaybe<Array<Scalars['Int']['input']>>;
  _isNull?: InputMaybe<Scalars['Boolean']['input']>;
  _lt?: InputMaybe<Scalars['Int']['input']>;
  _lte?: InputMaybe<Scalars['Int']['input']>;
  _neq?: InputMaybe<Scalars['Int']['input']>;
  _nin?: InputMaybe<Array<Scalars['Int']['input']>>;
};

export type LightingGroupsLogType = {
  __typename?: 'LightingGroupsLogType';
  id: Scalars['String']['output'];
  level: Scalars['Float']['output'];
  roomId: Scalars['String']['output'];
  timestamp: Scalars['DateTime']['output'];
};

export type MutationResponse = {
  __typename?: 'MutationResponse';
  code: Scalars['Int']['output'];
  message: Scalars['String']['output'];
  success: Scalars['Boolean']['output'];
};

/** column ordering options */
export enum OrderBy {
  /** in ascending order, nulls last */
  Asc = 'ASC',
  /** in ascending order, nulls first */
  AscNullsFirst = 'ASC_NULLS_FIRST',
  /** in ascending order, nulls last */
  AscNullsLast = 'ASC_NULLS_LAST',
  /** in descending order, nulls first */
  Desc = 'DESC',
  /** in descending order, nulls first */
  DescNullsFirst = 'DESC_NULLS_FIRST',
  /** in descending order, nulls last */
  DescNullsLast = 'DESC_NULLS_LAST'
}

/** Boolean expression to compare columns of type "String". All fields are combined with logical 'AND'. */
export type StringComparisonExp = {
  _eq?: InputMaybe<Scalars['String']['input']>;
  _gt?: InputMaybe<Scalars['String']['input']>;
  _gte?: InputMaybe<Scalars['String']['input']>;
  /** does the column match the given case-insensitive pattern */
  _ilike?: InputMaybe<Scalars['String']['input']>;
  _in?: InputMaybe<Array<Scalars['String']['input']>>;
  /** does the column match the given POSIX regular expression, case insensitive */
  _iregex?: InputMaybe<Scalars['String']['input']>;
  _isNull?: InputMaybe<Scalars['Boolean']['input']>;
  /** does the column match the given pattern */
  _like?: InputMaybe<Scalars['String']['input']>;
  _lt?: InputMaybe<Scalars['String']['input']>;
  _lte?: InputMaybe<Scalars['String']['input']>;
  _neq?: InputMaybe<Scalars['String']['input']>;
  /** does the column NOT match the given case-insensitive pattern */
  _nilike?: InputMaybe<Scalars['String']['input']>;
  _nin?: InputMaybe<Array<Scalars['String']['input']>>;
  /** does the column NOT match the given POSIX regular expression, case insensitive */
  _niregex?: InputMaybe<Scalars['String']['input']>;
  /** does the column NOT match the given pattern */
  _nlike?: InputMaybe<Scalars['String']['input']>;
  /** does the column NOT match the given POSIX regular expression, case sensitive */
  _nregex?: InputMaybe<Scalars['String']['input']>;
  /** does the column NOT match the given SQL regular expression */
  _nsimilar?: InputMaybe<Scalars['String']['input']>;
  /** does the column match the given POSIX regular expression, case sensitive */
  _regex?: InputMaybe<Scalars['String']['input']>;
  /** does the column match the given SQL regular expression */
  _similar?: InputMaybe<Scalars['String']['input']>;
};

export enum TimePeriod {
  Day = 'DAY',
  Hour = 'HOUR',
  Week = 'WEEK'
}

export type VentilationLogType = {
  __typename?: 'VentilationLogType';
  actualCo2: Scalars['Float']['output'];
  co2Setpoint: Scalars['Float']['output'];
  id: Scalars['String']['output'];
  timestamp: Scalars['DateTime']['output'];
};

export type DomesticBlindsAggregateBoolExpCount = {
  arguments?: InputMaybe<Array<DomesticBlindsSelectColumn>>;
  distinct?: InputMaybe<Scalars['Boolean']['input']>;
  filter?: InputMaybe<DomesticBlindsBoolExp>;
  predicate: IntComparisonExp;
};

export type DomesticLightingGroupsAggregateBoolExpCount = {
  arguments?: InputMaybe<Array<DomesticLightingGroupsSelectColumn>>;
  distinct?: InputMaybe<Scalars['Boolean']['input']>;
  filter?: InputMaybe<DomesticLightingGroupsBoolExp>;
  predicate: IntComparisonExp;
};

/** mutation root */
export type MutationRoot = {
  __typename?: 'mutation_root';
  /** delete data from the table: "domestic.air_conditioning" */
  deleteDomesticAirConditioning?: Maybe<DomesticAirConditioningMutationResponse>;
  /** delete single row from the table: "domestic.air_conditioning" */
  deleteDomesticAirConditioningByPk?: Maybe<DomesticAirConditioning>;
  /** delete data from the table: "domestic.amplifiers" */
  deleteDomesticAmplifiers?: Maybe<DomesticAmplifiersMutationResponse>;
  /** delete single row from the table: "domestic.amplifiers" */
  deleteDomesticAmplifiersByPk?: Maybe<DomesticAmplifiers>;
  /** delete data from the table: "domestic.blinds" */
  deleteDomesticBlinds?: Maybe<DomesticBlindsMutationResponse>;
  /** delete single row from the table: "domestic.blinds" */
  deleteDomesticBlindsByPk?: Maybe<DomesticBlinds>;
  /** delete data from the table: "domestic.lighting_groups" */
  deleteDomesticLightingGroups?: Maybe<DomesticLightingGroupsMutationResponse>;
  /** delete single row from the table: "domestic.lighting_groups" */
  deleteDomesticLightingGroupsByPk?: Maybe<DomesticLightingGroups>;
  /** delete data from the table: "domestic.rooms" */
  deleteDomesticRooms?: Maybe<DomesticRoomsMutationResponse>;
  /** delete single row from the table: "domestic.rooms" */
  deleteDomesticRoomsByPk?: Maybe<DomesticRooms>;
  /** delete data from the table: "domestic.ventilation" */
  deleteDomesticVentilation?: Maybe<DomesticVentilationMutationResponse>;
  /** delete single row from the table: "domestic.ventilation" */
  deleteDomesticVentilationByPk?: Maybe<DomesticVentilation>;
  domesticSetAmplifiers: MutationResponse;
  domesticSetBlinds: MutationResponse;
  domesticSetLightingGroups: MutationResponse;
  domesticSetRoomCo2Setpoints: MutationResponse;
  domesticSetRoomHumiditySetpoints: MutationResponse;
  domesticSetRoomTemperatureSetpoints: MutationResponse;
  /** insert data into the table: "domestic.air_conditioning" */
  insertDomesticAirConditioning?: Maybe<DomesticAirConditioningMutationResponse>;
  /** insert a single row into the table: "domestic.air_conditioning" */
  insertDomesticAirConditioningOne?: Maybe<DomesticAirConditioning>;
  /** insert data into the table: "domestic.amplifiers" */
  insertDomesticAmplifiers?: Maybe<DomesticAmplifiersMutationResponse>;
  /** insert a single row into the table: "domestic.amplifiers" */
  insertDomesticAmplifiersOne?: Maybe<DomesticAmplifiers>;
  /** insert data into the table: "domestic.blinds" */
  insertDomesticBlinds?: Maybe<DomesticBlindsMutationResponse>;
  /** insert a single row into the table: "domestic.blinds" */
  insertDomesticBlindsOne?: Maybe<DomesticBlinds>;
  /** insert data into the table: "domestic.lighting_groups" */
  insertDomesticLightingGroups?: Maybe<DomesticLightingGroupsMutationResponse>;
  /** insert a single row into the table: "domestic.lighting_groups" */
  insertDomesticLightingGroupsOne?: Maybe<DomesticLightingGroups>;
  /** insert data into the table: "domestic.rooms" */
  insertDomesticRooms?: Maybe<DomesticRoomsMutationResponse>;
  /** insert a single row into the table: "domestic.rooms" */
  insertDomesticRoomsOne?: Maybe<DomesticRooms>;
  /** insert data into the table: "domestic.ventilation" */
  insertDomesticVentilation?: Maybe<DomesticVentilationMutationResponse>;
  /** insert a single row into the table: "domestic.ventilation" */
  insertDomesticVentilationOne?: Maybe<DomesticVentilation>;
  /** update data of the table: "domestic.air_conditioning" */
  updateDomesticAirConditioning?: Maybe<DomesticAirConditioningMutationResponse>;
  /** update single row of the table: "domestic.air_conditioning" */
  updateDomesticAirConditioningByPk?: Maybe<DomesticAirConditioning>;
  /** update multiples rows of table: "domestic.air_conditioning" */
  updateDomesticAirConditioningMany?: Maybe<Array<Maybe<DomesticAirConditioningMutationResponse>>>;
  /** update data of the table: "domestic.amplifiers" */
  updateDomesticAmplifiers?: Maybe<DomesticAmplifiersMutationResponse>;
  /** update single row of the table: "domestic.amplifiers" */
  updateDomesticAmplifiersByPk?: Maybe<DomesticAmplifiers>;
  /** update multiples rows of table: "domestic.amplifiers" */
  updateDomesticAmplifiersMany?: Maybe<Array<Maybe<DomesticAmplifiersMutationResponse>>>;
  /** update data of the table: "domestic.blinds" */
  updateDomesticBlinds?: Maybe<DomesticBlindsMutationResponse>;
  /** update single row of the table: "domestic.blinds" */
  updateDomesticBlindsByPk?: Maybe<DomesticBlinds>;
  /** update multiples rows of table: "domestic.blinds" */
  updateDomesticBlindsMany?: Maybe<Array<Maybe<DomesticBlindsMutationResponse>>>;
  /** update data of the table: "domestic.lighting_groups" */
  updateDomesticLightingGroups?: Maybe<DomesticLightingGroupsMutationResponse>;
  /** update single row of the table: "domestic.lighting_groups" */
  updateDomesticLightingGroupsByPk?: Maybe<DomesticLightingGroups>;
  /** update multiples rows of table: "domestic.lighting_groups" */
  updateDomesticLightingGroupsMany?: Maybe<Array<Maybe<DomesticLightingGroupsMutationResponse>>>;
  /** update data of the table: "domestic.rooms" */
  updateDomesticRooms?: Maybe<DomesticRoomsMutationResponse>;
  /** update single row of the table: "domestic.rooms" */
  updateDomesticRoomsByPk?: Maybe<DomesticRooms>;
  /** update multiples rows of table: "domestic.rooms" */
  updateDomesticRoomsMany?: Maybe<Array<Maybe<DomesticRoomsMutationResponse>>>;
  /** update data of the table: "domestic.ventilation" */
  updateDomesticVentilation?: Maybe<DomesticVentilationMutationResponse>;
  /** update single row of the table: "domestic.ventilation" */
  updateDomesticVentilationByPk?: Maybe<DomesticVentilation>;
  /** update multiples rows of table: "domestic.ventilation" */
  updateDomesticVentilationMany?: Maybe<Array<Maybe<DomesticVentilationMutationResponse>>>;
};


/** mutation root */
export type MutationRootDeleteDomesticAirConditioningArgs = {
  where: DomesticAirConditioningBoolExp;
};


/** mutation root */
export type MutationRootDeleteDomesticAirConditioningByPkArgs = {
  id: Scalars['String']['input'];
};


/** mutation root */
export type MutationRootDeleteDomesticAmplifiersArgs = {
  where: DomesticAmplifiersBoolExp;
};


/** mutation root */
export type MutationRootDeleteDomesticAmplifiersByPkArgs = {
  id: Scalars['String']['input'];
};


/** mutation root */
export type MutationRootDeleteDomesticBlindsArgs = {
  where: DomesticBlindsBoolExp;
};


/** mutation root */
export type MutationRootDeleteDomesticBlindsByPkArgs = {
  id: Scalars['String']['input'];
};


/** mutation root */
export type MutationRootDeleteDomesticLightingGroupsArgs = {
  where: DomesticLightingGroupsBoolExp;
};


/** mutation root */
export type MutationRootDeleteDomesticLightingGroupsByPkArgs = {
  id: Scalars['String']['input'];
};


/** mutation root */
export type MutationRootDeleteDomesticRoomsArgs = {
  where: DomesticRoomsBoolExp;
};


/** mutation root */
export type MutationRootDeleteDomesticRoomsByPkArgs = {
  id: Scalars['String']['input'];
};


/** mutation root */
export type MutationRootDeleteDomesticVentilationArgs = {
  where: DomesticVentilationBoolExp;
};


/** mutation root */
export type MutationRootDeleteDomesticVentilationByPkArgs = {
  id: Scalars['String']['input'];
};


/** mutation root */
export type MutationRootDomesticSetAmplifiersArgs = {
  ids: Array<Scalars['ID']['input']>;
  on: Scalars['Boolean']['input'];
};


/** mutation root */
export type MutationRootDomesticSetBlindsArgs = {
  ids: Array<Scalars['ID']['input']>;
  level: Scalars['Float']['input'];
};


/** mutation root */
export type MutationRootDomesticSetLightingGroupsArgs = {
  ids?: InputMaybe<Array<Scalars['ID']['input']>>;
  level: Scalars['Float']['input'];
};


/** mutation root */
export type MutationRootDomesticSetRoomCo2SetpointsArgs = {
  co2: Scalars['Float']['input'];
  ids: Array<Scalars['ID']['input']>;
};


/** mutation root */
export type MutationRootDomesticSetRoomHumiditySetpointsArgs = {
  humidity: Scalars['Float']['input'];
  ids: Array<Scalars['ID']['input']>;
};


/** mutation root */
export type MutationRootDomesticSetRoomTemperatureSetpointsArgs = {
  ids: Array<Scalars['ID']['input']>;
  temperature: Scalars['Float']['input'];
};


/** mutation root */
export type MutationRootInsertDomesticAirConditioningArgs = {
  objects: Array<DomesticAirConditioningInsertInput>;
  onConflict?: InputMaybe<DomesticAirConditioningOnConflict>;
};


/** mutation root */
export type MutationRootInsertDomesticAirConditioningOneArgs = {
  object: DomesticAirConditioningInsertInput;
  onConflict?: InputMaybe<DomesticAirConditioningOnConflict>;
};


/** mutation root */
export type MutationRootInsertDomesticAmplifiersArgs = {
  objects: Array<DomesticAmplifiersInsertInput>;
  onConflict?: InputMaybe<DomesticAmplifiersOnConflict>;
};


/** mutation root */
export type MutationRootInsertDomesticAmplifiersOneArgs = {
  object: DomesticAmplifiersInsertInput;
  onConflict?: InputMaybe<DomesticAmplifiersOnConflict>;
};


/** mutation root */
export type MutationRootInsertDomesticBlindsArgs = {
  objects: Array<DomesticBlindsInsertInput>;
  onConflict?: InputMaybe<DomesticBlindsOnConflict>;
};


/** mutation root */
export type MutationRootInsertDomesticBlindsOneArgs = {
  object: DomesticBlindsInsertInput;
  onConflict?: InputMaybe<DomesticBlindsOnConflict>;
};


/** mutation root */
export type MutationRootInsertDomesticLightingGroupsArgs = {
  objects: Array<DomesticLightingGroupsInsertInput>;
  onConflict?: InputMaybe<DomesticLightingGroupsOnConflict>;
};


/** mutation root */
export type MutationRootInsertDomesticLightingGroupsOneArgs = {
  object: DomesticLightingGroupsInsertInput;
  onConflict?: InputMaybe<DomesticLightingGroupsOnConflict>;
};


/** mutation root */
export type MutationRootInsertDomesticRoomsArgs = {
  objects: Array<DomesticRoomsInsertInput>;
  onConflict?: InputMaybe<DomesticRoomsOnConflict>;
};


/** mutation root */
export type MutationRootInsertDomesticRoomsOneArgs = {
  object: DomesticRoomsInsertInput;
  onConflict?: InputMaybe<DomesticRoomsOnConflict>;
};


/** mutation root */
export type MutationRootInsertDomesticVentilationArgs = {
  objects: Array<DomesticVentilationInsertInput>;
  onConflict?: InputMaybe<DomesticVentilationOnConflict>;
};


/** mutation root */
export type MutationRootInsertDomesticVentilationOneArgs = {
  object: DomesticVentilationInsertInput;
  onConflict?: InputMaybe<DomesticVentilationOnConflict>;
};


/** mutation root */
export type MutationRootUpdateDomesticAirConditioningArgs = {
  _inc?: InputMaybe<DomesticAirConditioningIncInput>;
  _set?: InputMaybe<DomesticAirConditioningSetInput>;
  where: DomesticAirConditioningBoolExp;
};


/** mutation root */
export type MutationRootUpdateDomesticAirConditioningByPkArgs = {
  _inc?: InputMaybe<DomesticAirConditioningIncInput>;
  _set?: InputMaybe<DomesticAirConditioningSetInput>;
  pkColumns: DomesticAirConditioningPkColumnsInput;
};


/** mutation root */
export type MutationRootUpdateDomesticAirConditioningManyArgs = {
  updates: Array<DomesticAirConditioningUpdates>;
};


/** mutation root */
export type MutationRootUpdateDomesticAmplifiersArgs = {
  _set?: InputMaybe<DomesticAmplifiersSetInput>;
  where: DomesticAmplifiersBoolExp;
};


/** mutation root */
export type MutationRootUpdateDomesticAmplifiersByPkArgs = {
  _set?: InputMaybe<DomesticAmplifiersSetInput>;
  pkColumns: DomesticAmplifiersPkColumnsInput;
};


/** mutation root */
export type MutationRootUpdateDomesticAmplifiersManyArgs = {
  updates: Array<DomesticAmplifiersUpdates>;
};


/** mutation root */
export type MutationRootUpdateDomesticBlindsArgs = {
  _inc?: InputMaybe<DomesticBlindsIncInput>;
  _set?: InputMaybe<DomesticBlindsSetInput>;
  where: DomesticBlindsBoolExp;
};


/** mutation root */
export type MutationRootUpdateDomesticBlindsByPkArgs = {
  _inc?: InputMaybe<DomesticBlindsIncInput>;
  _set?: InputMaybe<DomesticBlindsSetInput>;
  pkColumns: DomesticBlindsPkColumnsInput;
};


/** mutation root */
export type MutationRootUpdateDomesticBlindsManyArgs = {
  updates: Array<DomesticBlindsUpdates>;
};


/** mutation root */
export type MutationRootUpdateDomesticLightingGroupsArgs = {
  _inc?: InputMaybe<DomesticLightingGroupsIncInput>;
  _set?: InputMaybe<DomesticLightingGroupsSetInput>;
  where: DomesticLightingGroupsBoolExp;
};


/** mutation root */
export type MutationRootUpdateDomesticLightingGroupsByPkArgs = {
  _inc?: InputMaybe<DomesticLightingGroupsIncInput>;
  _set?: InputMaybe<DomesticLightingGroupsSetInput>;
  pkColumns: DomesticLightingGroupsPkColumnsInput;
};


/** mutation root */
export type MutationRootUpdateDomesticLightingGroupsManyArgs = {
  updates: Array<DomesticLightingGroupsUpdates>;
};


/** mutation root */
export type MutationRootUpdateDomesticRoomsArgs = {
  _set?: InputMaybe<DomesticRoomsSetInput>;
  where: DomesticRoomsBoolExp;
};


/** mutation root */
export type MutationRootUpdateDomesticRoomsByPkArgs = {
  _set?: InputMaybe<DomesticRoomsSetInput>;
  pkColumns: DomesticRoomsPkColumnsInput;
};


/** mutation root */
export type MutationRootUpdateDomesticRoomsManyArgs = {
  updates: Array<DomesticRoomsUpdates>;
};


/** mutation root */
export type MutationRootUpdateDomesticVentilationArgs = {
  _inc?: InputMaybe<DomesticVentilationIncInput>;
  _set?: InputMaybe<DomesticVentilationSetInput>;
  where: DomesticVentilationBoolExp;
};


/** mutation root */
export type MutationRootUpdateDomesticVentilationByPkArgs = {
  _inc?: InputMaybe<DomesticVentilationIncInput>;
  _set?: InputMaybe<DomesticVentilationSetInput>;
  pkColumns: DomesticVentilationPkColumnsInput;
};


/** mutation root */
export type MutationRootUpdateDomesticVentilationManyArgs = {
  updates: Array<DomesticVentilationUpdates>;
};

export type QueryRoot = {
  __typename?: 'query_root';
  airConditioningLog: Array<AcLogType>;
  amplifiersLog: Array<AmplifiersLogType>;
  blindsLog: Array<BlindsLogType>;
  /** fetch data from the table: "domestic.air_conditioning" */
  domesticAirConditioning: Array<DomesticAirConditioning>;
  /** fetch aggregated fields from the table: "domestic.air_conditioning" */
  domesticAirConditioningAggregate: DomesticAirConditioningAggregate;
  /** fetch data from the table: "domestic.air_conditioning" using primary key columns */
  domesticAirConditioningByPk?: Maybe<DomesticAirConditioning>;
  /** fetch data from the table: "domestic.amplifiers" */
  domesticAmplifiers: Array<DomesticAmplifiers>;
  /** fetch aggregated fields from the table: "domestic.amplifiers" */
  domesticAmplifiersAggregate: DomesticAmplifiersAggregate;
  /** fetch data from the table: "domestic.amplifiers" using primary key columns */
  domesticAmplifiersByPk?: Maybe<DomesticAmplifiers>;
  /** fetch data from the table: "domestic.blinds" */
  domesticBlinds: Array<DomesticBlinds>;
  /** fetch aggregated fields from the table: "domestic.blinds" */
  domesticBlindsAggregate: DomesticBlindsAggregate;
  /** fetch data from the table: "domestic.blinds" using primary key columns */
  domesticBlindsByPk?: Maybe<DomesticBlinds>;
  /** fetch data from the table: "domestic.lighting_groups" */
  domesticLightingGroups: Array<DomesticLightingGroups>;
  /** fetch aggregated fields from the table: "domestic.lighting_groups" */
  domesticLightingGroupsAggregate: DomesticLightingGroupsAggregate;
  /** fetch data from the table: "domestic.lighting_groups" using primary key columns */
  domesticLightingGroupsByPk?: Maybe<DomesticLightingGroups>;
  /** fetch data from the table: "domestic.rooms" */
  domesticRooms: Array<DomesticRooms>;
  /** fetch aggregated fields from the table: "domestic.rooms" */
  domesticRoomsAggregate: DomesticRoomsAggregate;
  /** fetch data from the table: "domestic.rooms" using primary key columns */
  domesticRoomsByPk?: Maybe<DomesticRooms>;
  /** fetch data from the table: "domestic.ventilation" */
  domesticVentilation: Array<DomesticVentilation>;
  /** fetch aggregated fields from the table: "domestic.ventilation" */
  domesticVentilationAggregate: DomesticVentilationAggregate;
  /** fetch data from the table: "domestic.ventilation" using primary key columns */
  domesticVentilationByPk?: Maybe<DomesticVentilation>;
  domesticVersion: Scalars['String']['output'];
  lightingGroupsLog: Array<LightingGroupsLogType>;
  ventilationLog: Array<VentilationLogType>;
};


export type QueryRootAirConditioningLogArgs = {
  period: TimePeriod;
  roomId: Scalars['ID']['input'];
};


export type QueryRootAmplifiersLogArgs = {
  period: TimePeriod;
  roomId: Scalars['ID']['input'];
};


export type QueryRootBlindsLogArgs = {
  period: TimePeriod;
  roomId: Scalars['ID']['input'];
};


export type QueryRootDomesticAirConditioningArgs = {
  distinctOn?: InputMaybe<Array<DomesticAirConditioningSelectColumn>>;
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
  orderBy?: InputMaybe<Array<DomesticAirConditioningOrderBy>>;
  where?: InputMaybe<DomesticAirConditioningBoolExp>;
};


export type QueryRootDomesticAirConditioningAggregateArgs = {
  distinctOn?: InputMaybe<Array<DomesticAirConditioningSelectColumn>>;
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
  orderBy?: InputMaybe<Array<DomesticAirConditioningOrderBy>>;
  where?: InputMaybe<DomesticAirConditioningBoolExp>;
};


export type QueryRootDomesticAirConditioningByPkArgs = {
  id: Scalars['String']['input'];
};


export type QueryRootDomesticAmplifiersArgs = {
  distinctOn?: InputMaybe<Array<DomesticAmplifiersSelectColumn>>;
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
  orderBy?: InputMaybe<Array<DomesticAmplifiersOrderBy>>;
  where?: InputMaybe<DomesticAmplifiersBoolExp>;
};


export type QueryRootDomesticAmplifiersAggregateArgs = {
  distinctOn?: InputMaybe<Array<DomesticAmplifiersSelectColumn>>;
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
  orderBy?: InputMaybe<Array<DomesticAmplifiersOrderBy>>;
  where?: InputMaybe<DomesticAmplifiersBoolExp>;
};


export type QueryRootDomesticAmplifiersByPkArgs = {
  id: Scalars['String']['input'];
};


export type QueryRootDomesticBlindsArgs = {
  distinctOn?: InputMaybe<Array<DomesticBlindsSelectColumn>>;
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
  orderBy?: InputMaybe<Array<DomesticBlindsOrderBy>>;
  where?: InputMaybe<DomesticBlindsBoolExp>;
};


export type QueryRootDomesticBlindsAggregateArgs = {
  distinctOn?: InputMaybe<Array<DomesticBlindsSelectColumn>>;
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
  orderBy?: InputMaybe<Array<DomesticBlindsOrderBy>>;
  where?: InputMaybe<DomesticBlindsBoolExp>;
};


export type QueryRootDomesticBlindsByPkArgs = {
  id: Scalars['String']['input'];
};


export type QueryRootDomesticLightingGroupsArgs = {
  distinctOn?: InputMaybe<Array<DomesticLightingGroupsSelectColumn>>;
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
  orderBy?: InputMaybe<Array<DomesticLightingGroupsOrderBy>>;
  where?: InputMaybe<DomesticLightingGroupsBoolExp>;
};


export type QueryRootDomesticLightingGroupsAggregateArgs = {
  distinctOn?: InputMaybe<Array<DomesticLightingGroupsSelectColumn>>;
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
  orderBy?: InputMaybe<Array<DomesticLightingGroupsOrderBy>>;
  where?: InputMaybe<DomesticLightingGroupsBoolExp>;
};


export type QueryRootDomesticLightingGroupsByPkArgs = {
  id: Scalars['String']['input'];
};


export type QueryRootDomesticRoomsArgs = {
  distinctOn?: InputMaybe<Array<DomesticRoomsSelectColumn>>;
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
  orderBy?: InputMaybe<Array<DomesticRoomsOrderBy>>;
  where?: InputMaybe<DomesticRoomsBoolExp>;
};


export type QueryRootDomesticRoomsAggregateArgs = {
  distinctOn?: InputMaybe<Array<DomesticRoomsSelectColumn>>;
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
  orderBy?: InputMaybe<Array<DomesticRoomsOrderBy>>;
  where?: InputMaybe<DomesticRoomsBoolExp>;
};


export type QueryRootDomesticRoomsByPkArgs = {
  id: Scalars['String']['input'];
};


export type QueryRootDomesticVentilationArgs = {
  distinctOn?: InputMaybe<Array<DomesticVentilationSelectColumn>>;
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
  orderBy?: InputMaybe<Array<DomesticVentilationOrderBy>>;
  where?: InputMaybe<DomesticVentilationBoolExp>;
};


export type QueryRootDomesticVentilationAggregateArgs = {
  distinctOn?: InputMaybe<Array<DomesticVentilationSelectColumn>>;
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
  orderBy?: InputMaybe<Array<DomesticVentilationOrderBy>>;
  where?: InputMaybe<DomesticVentilationBoolExp>;
};


export type QueryRootDomesticVentilationByPkArgs = {
  id: Scalars['String']['input'];
};


export type QueryRootLightingGroupsLogArgs = {
  period: TimePeriod;
  roomId: Scalars['ID']['input'];
};


export type QueryRootVentilationLogArgs = {
  period: TimePeriod;
  roomId: Scalars['ID']['input'];
};

export type SubscriptionRoot = {
  __typename?: 'subscription_root';
  /** fetch data from the table: "domestic.air_conditioning" */
  domesticAirConditioning: Array<DomesticAirConditioning>;
  /** fetch aggregated fields from the table: "domestic.air_conditioning" */
  domesticAirConditioningAggregate: DomesticAirConditioningAggregate;
  /** fetch data from the table: "domestic.air_conditioning" using primary key columns */
  domesticAirConditioningByPk?: Maybe<DomesticAirConditioning>;
  /** fetch data from the table in a streaming manner: "domestic.air_conditioning" */
  domesticAirConditioningStream: Array<DomesticAirConditioning>;
  /** fetch data from the table: "domestic.amplifiers" */
  domesticAmplifiers: Array<DomesticAmplifiers>;
  /** fetch aggregated fields from the table: "domestic.amplifiers" */
  domesticAmplifiersAggregate: DomesticAmplifiersAggregate;
  /** fetch data from the table: "domestic.amplifiers" using primary key columns */
  domesticAmplifiersByPk?: Maybe<DomesticAmplifiers>;
  /** fetch data from the table in a streaming manner: "domestic.amplifiers" */
  domesticAmplifiersStream: Array<DomesticAmplifiers>;
  /** fetch data from the table: "domestic.blinds" */
  domesticBlinds: Array<DomesticBlinds>;
  /** fetch aggregated fields from the table: "domestic.blinds" */
  domesticBlindsAggregate: DomesticBlindsAggregate;
  /** fetch data from the table: "domestic.blinds" using primary key columns */
  domesticBlindsByPk?: Maybe<DomesticBlinds>;
  /** fetch data from the table in a streaming manner: "domestic.blinds" */
  domesticBlindsStream: Array<DomesticBlinds>;
  /** fetch data from the table: "domestic.lighting_groups" */
  domesticLightingGroups: Array<DomesticLightingGroups>;
  /** fetch aggregated fields from the table: "domestic.lighting_groups" */
  domesticLightingGroupsAggregate: DomesticLightingGroupsAggregate;
  /** fetch data from the table: "domestic.lighting_groups" using primary key columns */
  domesticLightingGroupsByPk?: Maybe<DomesticLightingGroups>;
  /** fetch data from the table in a streaming manner: "domestic.lighting_groups" */
  domesticLightingGroupsStream: Array<DomesticLightingGroups>;
  /** fetch data from the table: "domestic.rooms" */
  domesticRooms: Array<DomesticRooms>;
  /** fetch aggregated fields from the table: "domestic.rooms" */
  domesticRoomsAggregate: DomesticRoomsAggregate;
  /** fetch data from the table: "domestic.rooms" using primary key columns */
  domesticRoomsByPk?: Maybe<DomesticRooms>;
  /** fetch data from the table in a streaming manner: "domestic.rooms" */
  domesticRoomsStream: Array<DomesticRooms>;
  /** fetch data from the table: "domestic.ventilation" */
  domesticVentilation: Array<DomesticVentilation>;
  /** fetch aggregated fields from the table: "domestic.ventilation" */
  domesticVentilationAggregate: DomesticVentilationAggregate;
  /** fetch data from the table: "domestic.ventilation" using primary key columns */
  domesticVentilationByPk?: Maybe<DomesticVentilation>;
  /** fetch data from the table in a streaming manner: "domestic.ventilation" */
  domesticVentilationStream: Array<DomesticVentilation>;
};


export type SubscriptionRootDomesticAirConditioningArgs = {
  distinctOn?: InputMaybe<Array<DomesticAirConditioningSelectColumn>>;
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
  orderBy?: InputMaybe<Array<DomesticAirConditioningOrderBy>>;
  where?: InputMaybe<DomesticAirConditioningBoolExp>;
};


export type SubscriptionRootDomesticAirConditioningAggregateArgs = {
  distinctOn?: InputMaybe<Array<DomesticAirConditioningSelectColumn>>;
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
  orderBy?: InputMaybe<Array<DomesticAirConditioningOrderBy>>;
  where?: InputMaybe<DomesticAirConditioningBoolExp>;
};


export type SubscriptionRootDomesticAirConditioningByPkArgs = {
  id: Scalars['String']['input'];
};


export type SubscriptionRootDomesticAirConditioningStreamArgs = {
  batchSize: Scalars['Int']['input'];
  cursor: Array<InputMaybe<DomesticAirConditioningStreamCursorInput>>;
  where?: InputMaybe<DomesticAirConditioningBoolExp>;
};


export type SubscriptionRootDomesticAmplifiersArgs = {
  distinctOn?: InputMaybe<Array<DomesticAmplifiersSelectColumn>>;
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
  orderBy?: InputMaybe<Array<DomesticAmplifiersOrderBy>>;
  where?: InputMaybe<DomesticAmplifiersBoolExp>;
};


export type SubscriptionRootDomesticAmplifiersAggregateArgs = {
  distinctOn?: InputMaybe<Array<DomesticAmplifiersSelectColumn>>;
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
  orderBy?: InputMaybe<Array<DomesticAmplifiersOrderBy>>;
  where?: InputMaybe<DomesticAmplifiersBoolExp>;
};


export type SubscriptionRootDomesticAmplifiersByPkArgs = {
  id: Scalars['String']['input'];
};


export type SubscriptionRootDomesticAmplifiersStreamArgs = {
  batchSize: Scalars['Int']['input'];
  cursor: Array<InputMaybe<DomesticAmplifiersStreamCursorInput>>;
  where?: InputMaybe<DomesticAmplifiersBoolExp>;
};


export type SubscriptionRootDomesticBlindsArgs = {
  distinctOn?: InputMaybe<Array<DomesticBlindsSelectColumn>>;
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
  orderBy?: InputMaybe<Array<DomesticBlindsOrderBy>>;
  where?: InputMaybe<DomesticBlindsBoolExp>;
};


export type SubscriptionRootDomesticBlindsAggregateArgs = {
  distinctOn?: InputMaybe<Array<DomesticBlindsSelectColumn>>;
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
  orderBy?: InputMaybe<Array<DomesticBlindsOrderBy>>;
  where?: InputMaybe<DomesticBlindsBoolExp>;
};


export type SubscriptionRootDomesticBlindsByPkArgs = {
  id: Scalars['String']['input'];
};


export type SubscriptionRootDomesticBlindsStreamArgs = {
  batchSize: Scalars['Int']['input'];
  cursor: Array<InputMaybe<DomesticBlindsStreamCursorInput>>;
  where?: InputMaybe<DomesticBlindsBoolExp>;
};


export type SubscriptionRootDomesticLightingGroupsArgs = {
  distinctOn?: InputMaybe<Array<DomesticLightingGroupsSelectColumn>>;
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
  orderBy?: InputMaybe<Array<DomesticLightingGroupsOrderBy>>;
  where?: InputMaybe<DomesticLightingGroupsBoolExp>;
};


export type SubscriptionRootDomesticLightingGroupsAggregateArgs = {
  distinctOn?: InputMaybe<Array<DomesticLightingGroupsSelectColumn>>;
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
  orderBy?: InputMaybe<Array<DomesticLightingGroupsOrderBy>>;
  where?: InputMaybe<DomesticLightingGroupsBoolExp>;
};


export type SubscriptionRootDomesticLightingGroupsByPkArgs = {
  id: Scalars['String']['input'];
};


export type SubscriptionRootDomesticLightingGroupsStreamArgs = {
  batchSize: Scalars['Int']['input'];
  cursor: Array<InputMaybe<DomesticLightingGroupsStreamCursorInput>>;
  where?: InputMaybe<DomesticLightingGroupsBoolExp>;
};


export type SubscriptionRootDomesticRoomsArgs = {
  distinctOn?: InputMaybe<Array<DomesticRoomsSelectColumn>>;
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
  orderBy?: InputMaybe<Array<DomesticRoomsOrderBy>>;
  where?: InputMaybe<DomesticRoomsBoolExp>;
};


export type SubscriptionRootDomesticRoomsAggregateArgs = {
  distinctOn?: InputMaybe<Array<DomesticRoomsSelectColumn>>;
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
  orderBy?: InputMaybe<Array<DomesticRoomsOrderBy>>;
  where?: InputMaybe<DomesticRoomsBoolExp>;
};


export type SubscriptionRootDomesticRoomsByPkArgs = {
  id: Scalars['String']['input'];
};


export type SubscriptionRootDomesticRoomsStreamArgs = {
  batchSize: Scalars['Int']['input'];
  cursor: Array<InputMaybe<DomesticRoomsStreamCursorInput>>;
  where?: InputMaybe<DomesticRoomsBoolExp>;
};


export type SubscriptionRootDomesticVentilationArgs = {
  distinctOn?: InputMaybe<Array<DomesticVentilationSelectColumn>>;
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
  orderBy?: InputMaybe<Array<DomesticVentilationOrderBy>>;
  where?: InputMaybe<DomesticVentilationBoolExp>;
};


export type SubscriptionRootDomesticVentilationAggregateArgs = {
  distinctOn?: InputMaybe<Array<DomesticVentilationSelectColumn>>;
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
  orderBy?: InputMaybe<Array<DomesticVentilationOrderBy>>;
  where?: InputMaybe<DomesticVentilationBoolExp>;
};


export type SubscriptionRootDomesticVentilationByPkArgs = {
  id: Scalars['String']['input'];
};


export type SubscriptionRootDomesticVentilationStreamArgs = {
  batchSize: Scalars['Int']['input'];
  cursor: Array<InputMaybe<DomesticVentilationStreamCursorInput>>;
  where?: InputMaybe<DomesticVentilationBoolExp>;
};

export type GetVersionQueryVariables = Exact<{ [key: string]: never; }>;


export type GetVersionQuery = { __typename?: 'query_root', version: string };

export type BlindsItemFragment = { __typename?: 'DomesticBlinds', id: string, name?: string | null, level?: number | null, roomId?: string | null, opacity?: string | null, group?: string | null } & { ' $fragmentName'?: 'BlindsItemFragment' };

export type SetBlindsLevelMutationVariables = Exact<{
  ids: Array<Scalars['ID']['input']> | Scalars['ID']['input'];
  level: Scalars['Float']['input'];
}>;


export type SetBlindsLevelMutation = { __typename?: 'mutation_root', setBlinds: (
    { __typename?: 'MutationResponse' }
    & { ' $fragmentRefs'?: { 'MutationResponseFragment': MutationResponseFragment } }
  ) };

export type GetRoomAirConditioningLogQueryVariables = Exact<{
  period: TimePeriod;
}>;


export type GetRoomAirConditioningLogQuery = { __typename?: 'query_root', rooms: Array<{ __typename?: 'DomesticRooms', id: string, name?: string | null, airConditioningLog: Array<{ __typename?: 'AcLogType', timestamp: any, actualTemperature: number, temperatureSetpoint: number, actualHumidity: number, humiditySetpoint: number }> }> };

export type GetRoomVentilationLogQueryVariables = Exact<{
  period: TimePeriod;
}>;


export type GetRoomVentilationLogQuery = { __typename?: 'query_root', rooms: Array<{ __typename?: 'DomesticRooms', id: string, name?: string | null, ventilationLog: Array<{ __typename?: 'VentilationLogType', timestamp: any, actualCo2: number, co2Setpoint: number }> }> };

export type MutationResponseFragment = { __typename?: 'MutationResponse', code: number, success: boolean, message: string } & { ' $fragmentName'?: 'MutationResponseFragment' };

export type LightGroupItemFragment = { __typename?: 'DomesticLightingGroups', id: string, name?: string | null, level?: number | null, roomId?: string | null } & { ' $fragmentName'?: 'LightGroupItemFragment' };

export type GetLightGroupsByRoomSubscriptionVariables = Exact<{
  roomId: Scalars['String']['input'];
}>;


export type GetLightGroupsByRoomSubscription = { __typename?: 'subscription_root', lightingGroups: Array<(
    { __typename?: 'DomesticLightingGroups' }
    & { ' $fragmentRefs'?: { 'LightGroupItemFragment': LightGroupItemFragment } }
  )> };

export type SetLightLevelMutationVariables = Exact<{
  id: Scalars['ID']['input'];
  level: Scalars['Float']['input'];
}>;


export type SetLightLevelMutation = { __typename?: 'mutation_root', setLightingGroup: (
    { __typename?: 'MutationResponse' }
    & { ' $fragmentRefs'?: { 'MutationResponseFragment': MutationResponseFragment } }
  ) };

export type SetGroupLightLevelMutationVariables = Exact<{
  ids: Array<Scalars['ID']['input']> | Scalars['ID']['input'];
  level: Scalars['Float']['input'];
}>;


export type SetGroupLightLevelMutation = { __typename?: 'mutation_root', setLightingGroups: (
    { __typename?: 'MutationResponse' }
    & { ' $fragmentRefs'?: { 'MutationResponseFragment': MutationResponseFragment } }
  ) };

export type RoomItemFragment = { __typename?: 'DomesticRooms', id: string, name?: string | null, group?: string | null, lightingGroups: Array<{ __typename?: 'DomesticLightingGroups', id: string, name?: string | null, level?: number | null }>, blinds: Array<{ __typename?: 'DomesticBlinds', id: string, name?: string | null, level?: number | null, opacity?: string | null, group?: string | null }>, airConditioning?: { __typename?: 'DomesticAirConditioning', temperatureSetpoint?: number | null, humiditySetpoint?: number | null, actualTemperature?: number | null, actualHumidity?: number | null } | null, ventilation?: { __typename?: 'DomesticVentilation', co2Setpoint?: number | null, actualCo2?: number | null } | null, amplifier?: { __typename?: 'DomesticAmplifiers', on?: boolean | null } | null } & { ' $fragmentName'?: 'RoomItemFragment' };

export type GetAllRoomsQueryVariables = Exact<{ [key: string]: never; }>;


export type GetAllRoomsQuery = { __typename?: 'query_root', rooms: Array<{ __typename?: 'DomesticRooms', id: string, name?: string | null, group?: string | null }> };

export type SubscribeToRoomSubscriptionVariables = Exact<{
  roomId: Scalars['String']['input'];
}>;


export type SubscribeToRoomSubscription = { __typename?: 'subscription_root', domesticRooms: Array<(
    { __typename?: 'DomesticRooms' }
    & { ' $fragmentRefs'?: { 'RoomItemFragment': RoomItemFragment } }
  )> };

export type SubscribeToRoomsSubscriptionVariables = Exact<{ [key: string]: never; }>;


export type SubscribeToRoomsSubscription = { __typename?: 'subscription_root', rooms: Array<(
    { __typename?: 'DomesticRooms' }
    & { ' $fragmentRefs'?: { 'RoomItemFragment': RoomItemFragment } }
  )> };

export type GetRoomByIdQueryVariables = Exact<{
  roomId: Scalars['String']['input'];
}>;


export type GetRoomByIdQuery = { __typename?: 'query_root', rooms: Array<(
    { __typename?: 'DomesticRooms' }
    & { ' $fragmentRefs'?: { 'RoomItemFragment': RoomItemFragment } }
  )> };

export type SetTemperatureSetpointForRoomMutationVariables = Exact<{
  ids: Array<Scalars['ID']['input']> | Scalars['ID']['input'];
  temperature: Scalars['Float']['input'];
}>;


export type SetTemperatureSetpointForRoomMutation = { __typename?: 'mutation_root', setRoomTemperatureSetpoints: (
    { __typename?: 'MutationResponse' }
    & { ' $fragmentRefs'?: { 'MutationResponseFragment': MutationResponseFragment } }
  ) };

export type SetAmplifierMutationVariables = Exact<{
  ids: Array<Scalars['ID']['input']> | Scalars['ID']['input'];
  on: Scalars['Boolean']['input'];
}>;


export type SetAmplifierMutation = { __typename?: 'mutation_root', setAmplifiers: (
    { __typename?: 'MutationResponse' }
    & { ' $fragmentRefs'?: { 'MutationResponseFragment': MutationResponseFragment } }
  ) };

export type SetRoomHumiditySetpointsMutationVariables = Exact<{
  ids: Array<Scalars['ID']['input']> | Scalars['ID']['input'];
  humidity: Scalars['Float']['input'];
}>;


export type SetRoomHumiditySetpointsMutation = { __typename?: 'mutation_root', setRoomHumiditySetpoints: (
    { __typename?: 'MutationResponse' }
    & { ' $fragmentRefs'?: { 'MutationResponseFragment': MutationResponseFragment } }
  ) };

export type SetRoomCo2SetpointsMutationVariables = Exact<{
  ids: Array<Scalars['ID']['input']> | Scalars['ID']['input'];
  co2: Scalars['Float']['input'];
}>;


export type SetRoomCo2SetpointsMutation = { __typename?: 'mutation_root', setRoomCo2Setpoints: (
    { __typename?: 'MutationResponse' }
    & { ' $fragmentRefs'?: { 'MutationResponseFragment': MutationResponseFragment } }
  ) };

export const BlindsItemFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"BlindsItem"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DomesticBlinds"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"level"}},{"kind":"Field","name":{"kind":"Name","value":"roomId"}},{"kind":"Field","name":{"kind":"Name","value":"opacity"}},{"kind":"Field","name":{"kind":"Name","value":"group"}}]}}]} as unknown as DocumentNode<BlindsItemFragment, unknown>;
export const MutationResponseFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"MutationResponse"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"MutationResponse"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"message"}}]}}]} as unknown as DocumentNode<MutationResponseFragment, unknown>;
export const LightGroupItemFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"LightGroupItem"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DomesticLightingGroups"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"level"}},{"kind":"Field","name":{"kind":"Name","value":"roomId"}}]}}]} as unknown as DocumentNode<LightGroupItemFragment, unknown>;
export const RoomItemFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"RoomItem"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DomesticRooms"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"group"}},{"kind":"Field","name":{"kind":"Name","value":"lightingGroups"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"orderBy"},"value":{"kind":"ObjectValue","fields":[{"kind":"ObjectField","name":{"kind":"Name","value":"id"},"value":{"kind":"EnumValue","value":"ASC"}}]}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"level"}}]}},{"kind":"Field","name":{"kind":"Name","value":"blinds"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"orderBy"},"value":{"kind":"ObjectValue","fields":[{"kind":"ObjectField","name":{"kind":"Name","value":"id"},"value":{"kind":"EnumValue","value":"ASC"}}]}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"level"}},{"kind":"Field","name":{"kind":"Name","value":"opacity"}},{"kind":"Field","name":{"kind":"Name","value":"group"}}]}},{"kind":"Field","name":{"kind":"Name","value":"airConditioning"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"temperatureSetpoint"}},{"kind":"Field","name":{"kind":"Name","value":"humiditySetpoint"}},{"kind":"Field","name":{"kind":"Name","value":"actualTemperature"}},{"kind":"Field","name":{"kind":"Name","value":"actualHumidity"}}]}},{"kind":"Field","name":{"kind":"Name","value":"ventilation"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"co2Setpoint"}},{"kind":"Field","name":{"kind":"Name","value":"actualCo2"}}]}},{"kind":"Field","name":{"kind":"Name","value":"amplifier"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"on"}}]}}]}}]} as unknown as DocumentNode<RoomItemFragment, unknown>;
export const GetVersionDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","alias":{"kind":"Name","value":"version"},"name":{"kind":"Name","value":"domesticVersion"}}]}}]} as unknown as DocumentNode<GetVersionQuery, GetVersionQueryVariables>;
export const SetBlindsLevelDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"SetBlindsLevel"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"ids"}},"type":{"kind":"NonNullType","type":{"kind":"ListType","type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"ID"}}}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"level"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Float"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","alias":{"kind":"Name","value":"setBlinds"},"name":{"kind":"Name","value":"domesticSetBlinds"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"ids"},"value":{"kind":"Variable","name":{"kind":"Name","value":"ids"}}},{"kind":"Argument","name":{"kind":"Name","value":"level"},"value":{"kind":"Variable","name":{"kind":"Name","value":"level"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"MutationResponse"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"MutationResponse"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"MutationResponse"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"message"}}]}}]} as unknown as DocumentNode<SetBlindsLevelMutation, SetBlindsLevelMutationVariables>;
export const GetRoomAirConditioningLogDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetRoomAirConditioningLog"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"period"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"TimePeriod"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","alias":{"kind":"Name","value":"rooms"},"name":{"kind":"Name","value":"domesticRooms"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"airConditioningLog"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"period"},"value":{"kind":"Variable","name":{"kind":"Name","value":"period"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"timestamp"}},{"kind":"Field","name":{"kind":"Name","value":"actualTemperature"}},{"kind":"Field","name":{"kind":"Name","value":"temperatureSetpoint"}},{"kind":"Field","name":{"kind":"Name","value":"actualHumidity"}},{"kind":"Field","name":{"kind":"Name","value":"humiditySetpoint"}}]}}]}}]}}]} as unknown as DocumentNode<GetRoomAirConditioningLogQuery, GetRoomAirConditioningLogQueryVariables>;
export const GetRoomVentilationLogDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetRoomVentilationLog"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"period"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"TimePeriod"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","alias":{"kind":"Name","value":"rooms"},"name":{"kind":"Name","value":"domesticRooms"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"ventilationLog"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"period"},"value":{"kind":"Variable","name":{"kind":"Name","value":"period"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"timestamp"}},{"kind":"Field","name":{"kind":"Name","value":"actualCo2"}},{"kind":"Field","name":{"kind":"Name","value":"co2Setpoint"}}]}}]}}]}}]} as unknown as DocumentNode<GetRoomVentilationLogQuery, GetRoomVentilationLogQueryVariables>;
export const GetLightGroupsByRoomDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"subscription","name":{"kind":"Name","value":"GetLightGroupsByRoom"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"roomId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","alias":{"kind":"Name","value":"lightingGroups"},"name":{"kind":"Name","value":"domesticLightingGroups"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"where"},"value":{"kind":"ObjectValue","fields":[{"kind":"ObjectField","name":{"kind":"Name","value":"roomId"},"value":{"kind":"ObjectValue","fields":[{"kind":"ObjectField","name":{"kind":"Name","value":"_eq"},"value":{"kind":"Variable","name":{"kind":"Name","value":"roomId"}}}]}}]}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"LightGroupItem"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"LightGroupItem"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DomesticLightingGroups"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"level"}},{"kind":"Field","name":{"kind":"Name","value":"roomId"}}]}}]} as unknown as DocumentNode<GetLightGroupsByRoomSubscription, GetLightGroupsByRoomSubscriptionVariables>;
export const SetLightLevelDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"SetLightLevel"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"id"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"ID"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"level"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Float"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","alias":{"kind":"Name","value":"setLightingGroup"},"name":{"kind":"Name","value":"domesticSetLightingGroups"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"ids"},"value":{"kind":"ListValue","values":[{"kind":"Variable","name":{"kind":"Name","value":"id"}}]}},{"kind":"Argument","name":{"kind":"Name","value":"level"},"value":{"kind":"Variable","name":{"kind":"Name","value":"level"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"MutationResponse"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"MutationResponse"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"MutationResponse"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"message"}}]}}]} as unknown as DocumentNode<SetLightLevelMutation, SetLightLevelMutationVariables>;
export const SetGroupLightLevelDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"SetGroupLightLevel"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"ids"}},"type":{"kind":"NonNullType","type":{"kind":"ListType","type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"ID"}}}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"level"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Float"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","alias":{"kind":"Name","value":"setLightingGroups"},"name":{"kind":"Name","value":"domesticSetLightingGroups"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"ids"},"value":{"kind":"Variable","name":{"kind":"Name","value":"ids"}}},{"kind":"Argument","name":{"kind":"Name","value":"level"},"value":{"kind":"Variable","name":{"kind":"Name","value":"level"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"MutationResponse"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"MutationResponse"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"MutationResponse"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"message"}}]}}]} as unknown as DocumentNode<SetGroupLightLevelMutation, SetGroupLightLevelMutationVariables>;
export const GetAllRoomsDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetAllRooms"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","alias":{"kind":"Name","value":"rooms"},"name":{"kind":"Name","value":"domesticRooms"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"group"}}]}}]}}]} as unknown as DocumentNode<GetAllRoomsQuery, GetAllRoomsQueryVariables>;
export const SubscribeToRoomDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"subscription","name":{"kind":"Name","value":"SubscribeToRoom"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"roomId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"domesticRooms"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"where"},"value":{"kind":"ObjectValue","fields":[{"kind":"ObjectField","name":{"kind":"Name","value":"id"},"value":{"kind":"ObjectValue","fields":[{"kind":"ObjectField","name":{"kind":"Name","value":"_eq"},"value":{"kind":"Variable","name":{"kind":"Name","value":"roomId"}}}]}}]}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"RoomItem"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"RoomItem"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DomesticRooms"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"group"}},{"kind":"Field","name":{"kind":"Name","value":"lightingGroups"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"orderBy"},"value":{"kind":"ObjectValue","fields":[{"kind":"ObjectField","name":{"kind":"Name","value":"id"},"value":{"kind":"EnumValue","value":"ASC"}}]}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"level"}}]}},{"kind":"Field","name":{"kind":"Name","value":"blinds"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"orderBy"},"value":{"kind":"ObjectValue","fields":[{"kind":"ObjectField","name":{"kind":"Name","value":"id"},"value":{"kind":"EnumValue","value":"ASC"}}]}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"level"}},{"kind":"Field","name":{"kind":"Name","value":"opacity"}},{"kind":"Field","name":{"kind":"Name","value":"group"}}]}},{"kind":"Field","name":{"kind":"Name","value":"airConditioning"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"temperatureSetpoint"}},{"kind":"Field","name":{"kind":"Name","value":"humiditySetpoint"}},{"kind":"Field","name":{"kind":"Name","value":"actualTemperature"}},{"kind":"Field","name":{"kind":"Name","value":"actualHumidity"}}]}},{"kind":"Field","name":{"kind":"Name","value":"ventilation"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"co2Setpoint"}},{"kind":"Field","name":{"kind":"Name","value":"actualCo2"}}]}},{"kind":"Field","name":{"kind":"Name","value":"amplifier"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"on"}}]}}]}}]} as unknown as DocumentNode<SubscribeToRoomSubscription, SubscribeToRoomSubscriptionVariables>;
export const SubscribeToRoomsDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"subscription","name":{"kind":"Name","value":"SubscribeToRooms"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","alias":{"kind":"Name","value":"rooms"},"name":{"kind":"Name","value":"domesticRooms"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"RoomItem"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"RoomItem"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DomesticRooms"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"group"}},{"kind":"Field","name":{"kind":"Name","value":"lightingGroups"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"orderBy"},"value":{"kind":"ObjectValue","fields":[{"kind":"ObjectField","name":{"kind":"Name","value":"id"},"value":{"kind":"EnumValue","value":"ASC"}}]}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"level"}}]}},{"kind":"Field","name":{"kind":"Name","value":"blinds"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"orderBy"},"value":{"kind":"ObjectValue","fields":[{"kind":"ObjectField","name":{"kind":"Name","value":"id"},"value":{"kind":"EnumValue","value":"ASC"}}]}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"level"}},{"kind":"Field","name":{"kind":"Name","value":"opacity"}},{"kind":"Field","name":{"kind":"Name","value":"group"}}]}},{"kind":"Field","name":{"kind":"Name","value":"airConditioning"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"temperatureSetpoint"}},{"kind":"Field","name":{"kind":"Name","value":"humiditySetpoint"}},{"kind":"Field","name":{"kind":"Name","value":"actualTemperature"}},{"kind":"Field","name":{"kind":"Name","value":"actualHumidity"}}]}},{"kind":"Field","name":{"kind":"Name","value":"ventilation"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"co2Setpoint"}},{"kind":"Field","name":{"kind":"Name","value":"actualCo2"}}]}},{"kind":"Field","name":{"kind":"Name","value":"amplifier"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"on"}}]}}]}}]} as unknown as DocumentNode<SubscribeToRoomsSubscription, SubscribeToRoomsSubscriptionVariables>;
export const GetRoomByIdDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetRoomById"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"roomId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","alias":{"kind":"Name","value":"rooms"},"name":{"kind":"Name","value":"domesticRooms"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"where"},"value":{"kind":"ObjectValue","fields":[{"kind":"ObjectField","name":{"kind":"Name","value":"id"},"value":{"kind":"ObjectValue","fields":[{"kind":"ObjectField","name":{"kind":"Name","value":"_eq"},"value":{"kind":"Variable","name":{"kind":"Name","value":"roomId"}}}]}}]}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"RoomItem"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"RoomItem"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DomesticRooms"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"group"}},{"kind":"Field","name":{"kind":"Name","value":"lightingGroups"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"orderBy"},"value":{"kind":"ObjectValue","fields":[{"kind":"ObjectField","name":{"kind":"Name","value":"id"},"value":{"kind":"EnumValue","value":"ASC"}}]}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"level"}}]}},{"kind":"Field","name":{"kind":"Name","value":"blinds"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"orderBy"},"value":{"kind":"ObjectValue","fields":[{"kind":"ObjectField","name":{"kind":"Name","value":"id"},"value":{"kind":"EnumValue","value":"ASC"}}]}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"level"}},{"kind":"Field","name":{"kind":"Name","value":"opacity"}},{"kind":"Field","name":{"kind":"Name","value":"group"}}]}},{"kind":"Field","name":{"kind":"Name","value":"airConditioning"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"temperatureSetpoint"}},{"kind":"Field","name":{"kind":"Name","value":"humiditySetpoint"}},{"kind":"Field","name":{"kind":"Name","value":"actualTemperature"}},{"kind":"Field","name":{"kind":"Name","value":"actualHumidity"}}]}},{"kind":"Field","name":{"kind":"Name","value":"ventilation"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"co2Setpoint"}},{"kind":"Field","name":{"kind":"Name","value":"actualCo2"}}]}},{"kind":"Field","name":{"kind":"Name","value":"amplifier"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"on"}}]}}]}}]} as unknown as DocumentNode<GetRoomByIdQuery, GetRoomByIdQueryVariables>;
export const SetTemperatureSetpointForRoomDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"SetTemperatureSetpointForRoom"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"ids"}},"type":{"kind":"NonNullType","type":{"kind":"ListType","type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"ID"}}}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"temperature"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Float"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","alias":{"kind":"Name","value":"setRoomTemperatureSetpoints"},"name":{"kind":"Name","value":"domesticSetRoomTemperatureSetpoints"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"ids"},"value":{"kind":"Variable","name":{"kind":"Name","value":"ids"}}},{"kind":"Argument","name":{"kind":"Name","value":"temperature"},"value":{"kind":"Variable","name":{"kind":"Name","value":"temperature"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"MutationResponse"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"MutationResponse"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"MutationResponse"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"message"}}]}}]} as unknown as DocumentNode<SetTemperatureSetpointForRoomMutation, SetTemperatureSetpointForRoomMutationVariables>;
export const SetAmplifierDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"SetAmplifier"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"ids"}},"type":{"kind":"NonNullType","type":{"kind":"ListType","type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"ID"}}}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"on"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Boolean"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","alias":{"kind":"Name","value":"setAmplifiers"},"name":{"kind":"Name","value":"domesticSetAmplifiers"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"ids"},"value":{"kind":"Variable","name":{"kind":"Name","value":"ids"}}},{"kind":"Argument","name":{"kind":"Name","value":"on"},"value":{"kind":"Variable","name":{"kind":"Name","value":"on"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"MutationResponse"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"MutationResponse"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"MutationResponse"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"message"}}]}}]} as unknown as DocumentNode<SetAmplifierMutation, SetAmplifierMutationVariables>;
export const SetRoomHumiditySetpointsDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"SetRoomHumiditySetpoints"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"ids"}},"type":{"kind":"NonNullType","type":{"kind":"ListType","type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"ID"}}}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"humidity"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Float"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","alias":{"kind":"Name","value":"setRoomHumiditySetpoints"},"name":{"kind":"Name","value":"domesticSetRoomHumiditySetpoints"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"ids"},"value":{"kind":"Variable","name":{"kind":"Name","value":"ids"}}},{"kind":"Argument","name":{"kind":"Name","value":"humidity"},"value":{"kind":"Variable","name":{"kind":"Name","value":"humidity"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"MutationResponse"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"MutationResponse"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"MutationResponse"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"message"}}]}}]} as unknown as DocumentNode<SetRoomHumiditySetpointsMutation, SetRoomHumiditySetpointsMutationVariables>;
export const SetRoomCo2SetpointsDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"SetRoomCo2Setpoints"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"ids"}},"type":{"kind":"NonNullType","type":{"kind":"ListType","type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"ID"}}}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"co2"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Float"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","alias":{"kind":"Name","value":"setRoomCo2Setpoints"},"name":{"kind":"Name","value":"domesticSetRoomCo2Setpoints"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"ids"},"value":{"kind":"Variable","name":{"kind":"Name","value":"ids"}}},{"kind":"Argument","name":{"kind":"Name","value":"co2"},"value":{"kind":"Variable","name":{"kind":"Name","value":"co2"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"MutationResponse"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"MutationResponse"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"MutationResponse"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"message"}}]}}]} as unknown as DocumentNode<SetRoomCo2SetpointsMutation, SetRoomCo2SetpointsMutationVariables>;