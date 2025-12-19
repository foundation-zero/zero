import { Sail, SailPosition } from "../types";

const position = (name: string, ...sails: Sail[][]): SailPosition => ({
  name,
  groups: sails.map((sailGroup) => ({ sails: sailGroup })),
});

export const sail = (name: string, id: string): Sail => ({
  name,
  id,
});

export const SAIL_POSITIONS: SailPosition[] = [
  position("Main", [
    sail("Full", "main-full"),
    sail("R1", "main-r1"),
    sail("R2", "main-r2"),
    sail("R3", "main-r3"),
    sail("Tri", "main-tri"),
  ]),
  position(
    "Foresails",
    [sail("Blade", "blade"), sail("Code-0", "code-0"), sail("A3", "A3"), sail("A2", "A2")],
    [sail("Staysail", "staysail"), sail("Stormjib", "stormjib")],
  ),
  position(
    "Mizzen",
    [sail("Full", "mizzen-full"), sail("R1", "mizzen-r1")],
    [sail("Ms Staysail", "mizzen-staysail"), sail("Ms Jib", "mizzen-jib")],
  ),
];
