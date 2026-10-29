import { createContext } from "reka-ui";
import { SailSelectorContext } from "./sail-selector.types";

export const [injectRootContext, provideRootContext] =
  createContext<SailSelectorContext>("sail-selector");
