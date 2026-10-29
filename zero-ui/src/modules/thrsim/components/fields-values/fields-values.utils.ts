import { createContext } from "reka-ui";
import { FieldsValuesContext } from "./fields-values.types";

export const [getContext, provideContext] = createContext<FieldsValuesContext>("FieldsValues");
