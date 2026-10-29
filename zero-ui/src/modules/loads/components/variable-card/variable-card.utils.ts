import { createContext } from "reka-ui";
import { PositionCardContext } from "./variable-card.types";

export const [getContext, provideContext] =
  createContext<PositionCardContext>("loads.variable-card");
