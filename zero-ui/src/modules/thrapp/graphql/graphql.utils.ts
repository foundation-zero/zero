import { gql } from "@urql/vue";
import { ValueType } from "./graphql.types";

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
