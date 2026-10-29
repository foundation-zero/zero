import { DhwTankController } from "@/modules/thrapp/types/thrs";

export type BoilerTankStateField = keyof Omit<DhwTankController, "timeToFill" | "timeToHot">;
