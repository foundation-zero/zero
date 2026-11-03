const UNIT_I18N_KEY: Record<string, string> = {
  tonne: "tonne",
  t_m: "t_m",
  um_m: "um_m",
  deg_c: "degC",
  m: "m",
};

export function formatUnit(unit: string | null | undefined, t: (key: string) => string): string {
  if (!unit) return "";
  const key = UNIT_I18N_KEY[unit];
  return key ? t(`rig.units.${key}`) : unit;
}

export function getDeflectionDisplayName(variableId: string): string | null {
  const height = /-(?:fa|sw)-deflection(\d{3})$/.exec(variableId);
  if (height) return `${Number(height[1])}% Height`;

  const spreader = /-(?:fa|sw)-deflection-spr(\d)$/.exec(variableId);
  if (spreader) return `Spreader ${spreader[1]}`;

  return null;
}
