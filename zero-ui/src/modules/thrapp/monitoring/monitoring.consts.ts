import {
  DHW_BOOSTING_MODE_MODES,
  DHW_FILLING_MODE_MODES,
  DHW_TANK_STATE_MODES,
  ModeBadgeMode,
} from "@/modules/thrapp/mimics/components/mode-badge/mode-badge.consts";
import { BoilerTankState } from "@/modules/thrapp/types/thrs";
import type { ModuleMonitoring } from "./monitoring.types";

const MINUTE = 60_000;
const HOUR = 60 * MINUTE;
const DAY = 24 * HOUR;

export const MonitoringMetric = {
  Temperature: "TEMPERATURE",
  Level: "LEVEL",
  Pressure: "PRESSURE",
  Flow: "FLOW",
  FlowTemperature: "FLOW_TEMPERATURE",
  FlowQuantity: "FLOW_QUANTITY",
  PumpSpeed: "PUMP_SPEED",
  PumpFlow: "PUMP_FLOW",
  PumpPressure: "PUMP_PRESSURE",
  PumpPowerInput: "PUMP_POWER_INPUT",
  PumpEnergyConsumption: "PUMP_ENERGY_CONSUMPTION",
  PumpOperationTime: "PUMP_OPERATION_TIME",
  PumpDutyPoint: "PUMP_DUTY_POINT",
  PumpControlMode: "PUMP_CONTROL_MODE",
  PumpOnOff: "PUMP_ON_OFF",
  ValvePositionAbsolute: "VALVE_POSITION_ABSOLUTE",
  ValvePositionRelative: "VALVE_POSITION_RELATIVE",
  ValveSetpoint: "VALVE_SETPOINT",
  MinimumTankTemperature: "MINIMUM_TANK_TEMPERATURE",
  MaximumTankTemperature: "MAXIMUM_TANK_TEMPERATURE",
  MinimumTankLevel: "MINIMUM_TANK_LEVEL",
  MaximumTankLevel: "MAXIMUM_TANK_LEVEL",
  Heat: "HEAT",
  CalculatedFlow: "CALCULATED_FLOW",
} as const;
export type MonitoringMetric = (typeof MonitoringMetric)[keyof typeof MonitoringMetric];

export const MonitoringSignal = {
  AmcsMode: "AMCS_MODE",
  BoostingMode: "BOOSTING_MODE",
  FillingMode: "FILLING_MODE",
  Tank1State: "TANK_1_STATE",
  Tank2State: "TANK_2_STATE",
  Tank3State: "TANK_3_STATE",
} as const;
export type MonitoringSignal = (typeof MonitoringSignal)[keyof typeof MonitoringSignal];

export const RANGE_PRESETS = [
  { key: "15m", span: 15 * MINUTE },
  { key: "1h", span: HOUR },
  { key: "6h", span: 6 * HOUR },
  { key: "12h", span: 12 * HOUR },
  { key: "24h", span: DAY },
  { key: "7d", span: 7 * DAY },
  { key: "30d", span: 30 * DAY },
] as const;

export const DEFAULT_SPAN = 6 * HOUR;
export const MAX_SPAN = 30 * DAY;

/** Auto-refresh intervals in ms; 0 is off. */
export const REFRESH_INTERVALS = [0, 10_000, 30_000, MINUTE, 5 * MINUTE] as const;
export const DEFAULT_REFRESH_INTERVAL = 30_000;

/** A reading at least this old is marked stale, as in the Grafana Live tables. */
export const STALE_AFTER = MINUTE;

/** Points further apart than this are drawn with a break, as Grafana's insertNulls. */
export const GAP_AFTER = 5 * MINUTE;

export const TICK_STEPS = [
  MINUTE,
  5 * MINUTE,
  10 * MINUTE,
  15 * MINUTE,
  30 * MINUTE,
  HOUR,
  2 * HOUR,
  3 * HOUR,
  6 * HOUR,
  12 * HOUR,
  DAY,
  2 * DAY,
  7 * DAY,
] as const;

// Validated with the dataviz palette checks against the zero-ui light and dark
// surfaces; series past eight repeat a hue with a dashed line.
export const SERIES_COLORS = {
  light: ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"],
  dark: ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#008300", "#9085e9", "#e66767"],
} as const;

/** The allowed range between a minimum and maximum parameter. */
export const LIMIT_COLOR = "var(--brand)";

/**
 * Space left of and right of the plot area in every timeline and chart, in px,
 * so their time axes line up down the page.
 */
export const PLOT_INSET = { left: 76, right: 16 } as const;

/** The order of the annotation filters, and their marker colour. */
export const ANNOTATION_KINDS = ["CREW", "PARAMETERS", "ALARM"] as const;
export const ANNOTATION_COLORS: Record<(typeof ANNOTATION_KINDS)[number], string> = {
  CREW: "var(--brand)",
  PARAMETERS: "var(--muted-foreground)",
  ALARM: "var(--destructive)",
};

/** The design system tooltip, for the charts' hover boxes. */
export const TOOLTIP_CLASS =
  "bg-primary text-primary-foreground font-ui rounded-md px-3 py-2 text-xs leading-5 shadow-md";

/** Timeline or chart on the left, a narrow column with its summary on the right. */
export const PANEL_GRID = "grid items-stretch gap-3 lg:grid-cols-[minmax(0,1fr)_360px]";

// The tank controller reports the states in lower case with spaces.
const tankModes: Record<string, ModeBadgeMode> = {
  "in use": DHW_TANK_STATE_MODES[BoilerTankState.InUse],
  filling: DHW_TANK_STATE_MODES[BoilerTankState.Filling],
  boosting: DHW_TANK_STATE_MODES[BoilerTankState.Boosting],
  disabled: DHW_TANK_STATE_MODES[BoilerTankState.Disabled],
  "needs boost": DHW_TANK_STATE_MODES[BoilerTankState.NeedsBoost],
  "needs fill": DHW_TANK_STATE_MODES[BoilerTankState.NeedsFill],
  standby: DHW_TANK_STATE_MODES[BoilerTankState.Standby],
};

export const MANUAL_STATE = "manual";

/** The mimics' badge for every state a signal reports, so colours match the mimics. */
export const SIGNAL_MODES: Record<MonitoringSignal, Record<string, ModeBadgeMode>> = {
  [MonitoringSignal.AmcsMode]: {
    amcs_local: ModeBadgeMode.Idle,
    amcs_manual: ModeBadgeMode.ManualControl,
    amcs_auto: ModeBadgeMode.AdvisoryOff,
    advisory: ModeBadgeMode.Active,
  },
  [MonitoringSignal.BoostingMode]: {
    ...DHW_BOOSTING_MODE_MODES,
    [MANUAL_STATE]: ModeBadgeMode.ManualControl,
  },
  [MonitoringSignal.FillingMode]: {
    ...DHW_FILLING_MODE_MODES,
    [MANUAL_STATE]: ModeBadgeMode.ManualControl,
  },
  [MonitoringSignal.Tank1State]: tankModes,
  [MonitoringSignal.Tank2State]: tankModes,
  [MonitoringSignal.Tank3State]: tankModes,
};

/** The live AMCS mode, as the control query reports it, named like the AMCS_MODE states. */
export const AMCS_MODE_STATES: Record<string, string> = {
  LOCAL: "amcs_local",
  MANUAL: "amcs_manual",
  AUTO: "amcs_auto",
  EXTERNAL: "advisory",
};

const tanks = (prefix: string) =>
  Object.fromEntries([1, 2, 3].map((tank) => [`${prefix}${tank}`, `Tank ${tank}`]));

const DHW_TANK_TEMPERATURES = tanks("dhw-temperature-tank");
const DHW_TANK_LEVELS = tanks("dhw-level-tank");

// Heat the DHW module takes in, per exchanger, after the DHW control module:
// the consumers exchanger is HT boosting.
const DHW_HEAT_SOURCES = {
  "dhw-consumers-exchanger": "HT boosting",
  "dhw-heatpump-heat": "Heat pump",
  "dhw-hvac-exchanger": "HVAC recovery",
  "dhw-dc-exchanger": "DC recovery",
  "dhw-drives-exchanger": "Drives recovery",
  "dhw-adsorption-exchanger": "Adsorption recovery",
};

// The fresh water the tanks take in, as the controller adds up the fill lines.
const DHW_FRESHWATER = "dhw-freshwater-flow-supply";

const BOOST_OVERLAY = { signal: MonitoringSignal.BoostingMode, shown: true };
const FILL_OVERLAY = { signal: MonitoringSignal.FillingMode, shown: false };
const OVERLAYS = [BOOST_OVERLAY, FILL_OVERLAY];

const perTank = (name: (tank: number) => string) => [1, 2, 3].map(name);

// Valves by the circuit they open, after the DHW control module; the tank
// boosting valves serve both boosting sources.
const DHW_VALVE_GROUPS = [
  { key: "boostingHighTemperature", devices: ["dhw-switch-high-temperature"] },
  { key: "boostingHeatpump", devices: ["dhw-switch-heatpump"] },
  {
    key: "boostingTanks",
    devices: [
      "dhw-switch-low-temperature",
      ...perTank((tank) => `dhw-switch-tank${tank}-boosting-supply`),
      ...perTank((tank) => `dhw-switch-tank${tank}-boosting-return`),
    ],
  },
  {
    key: "filling",
    devices: [
      ...perTank((tank) => `dhw-switch-tank${tank}-inlet`),
      "dhw-flowcontrol-dc",
      "dhw-flowcontrol-drives",
    ],
  },
  { key: "hotWaterUse", devices: perTank((tank) => `dhw-switch-tank${tank}-outlet`) },
];

// Temperatures by boiler and by the inlet and outlet of each circuit; the fresh
// water is preheated by the exchangers in this order.
const DHW_TEMPERATURE_GROUPS = [
  { key: "boilers", devices: perTank((tank) => `dhw-temperature-tank${tank}`) },
  {
    key: "boostingCircuit",
    devices: ["dhw-temperature-boosting-supply", "dhw-temperature-boosting-return"],
  },
  {
    key: "fillingPreheat",
    devices: [
      "dhw-temperature-freshwater-supply",
      "dhw-temperature-adsorption-return",
      "dhw-temperature-hvac-exchanger-return",
      "dhw-temperature-dc-return",
      "dhw-temperature-drives-return",
    ],
  },
];

/** What the monitoring page shows per module, in the order of the mockup. */
export const MODULE_MONITORING: Record<string, ModuleMonitoring> = {
  dhw: {
    module: "DHW",
    states: [
      {
        section: "modesAndStates",
        panels: [
          {
            key: "advisoryMode",
            header: "mode",
            rows: [{ signal: MonitoringSignal.AmcsMode, label: { key: "advisory" } }],
          },
          {
            key: "boostMode",
            header: "mode",
            rows: [{ signal: MonitoringSignal.BoostingMode, label: { key: "boosting" } }],
          },
          {
            key: "fillingMode",
            header: "mode",
            rows: [{ signal: MonitoringSignal.FillingMode, label: { key: "filling" } }],
          },
          {
            key: "tankState",
            header: "tankState",
            rows: [
              MonitoringSignal.Tank1State,
              MonitoringSignal.Tank2State,
              MonitoringSignal.Tank3State,
            ].map((signal, index) => ({
              signal,
              label: { key: "tank", params: { number: index + 1 } },
            })),
          },
        ],
      },
    ],
    trends: [
      {
        section: "heatExchange",
        panels: [
          {
            key: "heatTransfer",
            metrics: [MonitoringMetric.Heat],
            devices: Object.keys(DHW_HEAT_SOURCES),
            deviceLabels: DHW_HEAT_SOURCES,
            overlays: OVERLAYS,
            display: "heat",
          },
          {
            key: "heatDistribution",
            metrics: [MonitoringMetric.Heat],
            devices: Object.keys(DHW_HEAT_SOURCES),
            deviceLabels: DHW_HEAT_SOURCES,
            display: "distribution",
          },
        ],
      },
      {
        section: "functional",
        panels: [
          {
            key: "tankTemperatures",
            metrics: [MonitoringMetric.Temperature],
            devices: Object.keys(DHW_TANK_TEMPERATURES),
            deviceLabels: DHW_TANK_TEMPERATURES,
            overlays: OVERLAYS,
            limits: {
              lower: MonitoringMetric.MinimumTankTemperature,
              upper: MonitoringMetric.MaximumTankTemperature,
            },
          },
          {
            key: "tankLevels",
            metrics: [MonitoringMetric.Level],
            devices: Object.keys(DHW_TANK_LEVELS),
            deviceLabels: DHW_TANK_LEVELS,
            overlays: [
              { ...BOOST_OVERLAY, shown: false },
              { ...FILL_OVERLAY, shown: true },
            ],
            limits: {
              lower: MonitoringMetric.MinimumTankLevel,
              upper: MonitoringMetric.MaximumTankLevel,
            },
            totals: true,
          },
          {
            key: "waterUsage",
            // Fresh water in from its flow; hot water out from that and the change
            // in tank volume, as no meter measures it.
            metrics: [MonitoringMetric.CalculatedFlow, MonitoringMetric.Level],
            devices: [DHW_FRESHWATER, ...Object.keys(DHW_TANK_LEVELS)],
            overlays: [
              { ...BOOST_OVERLAY, shown: false },
              { ...FILL_OVERLAY, shown: true },
            ],
            display: "water",
          },
        ],
      },
      {
        section: "sensorsAndActuators",
        panels: [
          {
            key: "pumps",
            metrics: [
              MonitoringMetric.PumpSpeed,
              MonitoringMetric.PumpFlow,
              MonitoringMetric.PumpPressure,
              MonitoringMetric.PumpPowerInput,
              MonitoringMetric.PumpEnergyConsumption,
              MonitoringMetric.PumpOperationTime,
              MonitoringMetric.PumpDutyPoint,
              MonitoringMetric.PumpControlMode,
              MonitoringMetric.PumpOnOff,
            ],
            defaultMetric: MonitoringMetric.PumpFlow,
            overlays: OVERLAYS,
          },
          {
            key: "valves",
            metrics: [
              MonitoringMetric.ValvePositionAbsolute,
              MonitoringMetric.ValvePositionRelative,
              MonitoringMetric.ValveSetpoint,
            ],
            defaultMetric: MonitoringMetric.ValvePositionRelative,
            overlays: OVERLAYS,
            legendGroups: DHW_VALVE_GROUPS,
          },
          {
            key: "flow",
            metrics: [
              MonitoringMetric.Flow,
              MonitoringMetric.FlowTemperature,
              MonitoringMetric.FlowQuantity,
            ],
            defaultMetric: MonitoringMetric.Flow,
            overlays: OVERLAYS,
          },
          {
            key: "temperatures",
            metrics: [MonitoringMetric.Temperature],
            overlays: OVERLAYS,
            legendGroups: DHW_TEMPERATURE_GROUPS,
          },
          {
            key: "pressure",
            metrics: [MonitoringMetric.Pressure],
            overlays: OVERLAYS,
          },
        ],
      },
    ],
  },
};
