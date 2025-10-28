import { gql } from "@urql/vue";

export type ValueType =
  | "Float"
  | "Float!"
  | "[Float!]!"
  | "Int"
  | "[Int!]!"
  | "Boolean"
  | "[Boolean!]!"
  | "String"
  | "[String!]!";

export const mutationWithValue = (mutationName: string, inputName: string, valueType: ValueType) =>
  gql`
    mutation MutationWithValue($value: ${valueType}) {
      ${mutationName}(${inputName}: $value)
    }`;

export const mutationWithoutValue = (mutationName: string) =>
  gql`
    mutation MutationWithoutValue {
      ${mutationName}
    }`;
