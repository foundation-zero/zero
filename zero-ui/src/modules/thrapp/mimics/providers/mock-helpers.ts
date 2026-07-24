import { stamp } from "@/modules/common/lib/utils";
import { Stamped } from "@/modules/common/types";
import {
  BoilerTankState,
  ControlComponentType,
  ControlDefinitionMap,
  ControllerStateComponentType,
  ControllerStateDefinitionMap,
  ParameterDefinitionMap,
  ParametersType,
  PID,
  SensorComponentType,
  SensorDefinitionMap,
  ThrusterMode,
} from "@/modules/thrs/types";
import { useIntervalFn } from "@vueuse/core";
import { computed, MaybeRef, ref, Ref, unref } from "vue";

export const randomizedNumber = (min: number, max: number) =>
  Math.floor(Math.random() * (max - min + 1)) + min;

export const randomizedState = <T>(possibleValues: T[]) =>
  possibleValues[Math.floor(Math.random() * possibleValues.length)];

export const randomizedRatio = () => Math.random();
export const randomizedBoolean = () => Math.random() < 0.5;

export const useRandomizedValue = <T>(valueFn: () => T, interval = 10_000) => {
  const value = ref<T>(valueFn());

  useIntervalFn(() => (value.value = valueFn()), interval);

  return value;
};

export const useRandomizedState = <T>(possibleValues: T[], interval = 10_000) =>
  useRandomizedValue(() => randomizedState(possibleValues), interval);

export const useDeltaT = (tIn: MaybeRef<number>, tOut: MaybeRef<number>) =>
  computed(() => unref(tOut) - unref(tIn));

export const useRandomizedNumber = (min: number, max: number, interval = 10_000) =>
  useRandomizedValue(() => randomizedNumber(min, max), interval);

export const useRandomizedRatio = (interval = 10_000) =>
  useRandomizedValue(randomizedRatio, interval);

export const useRandomizedBoolean = (interval = 10_000) =>
  useRandomizedValue(randomizedBoolean, interval);

export type ValueFactory<T extends Record<string, unknown>> = {
  [K in keyof T]: () => Ref<T[K] | undefined>;
};

export type StampedObject<T extends Record<string, unknown>> = {
  [K in keyof T]: Stamped<T[K] extends Ref<infer U> ? U : T[K]>;
};

export const SENSOR_VALUES_FACTORY: ValueFactory<SensorDefinitionMap> = {
  [SensorComponentType.Temperature]: () => {
    const temperature = useRandomizedNumber(20, 100);
    return computed(() => ({ temperature: stamp(temperature) }));
  },
  [SensorComponentType.Pressure]: () => {
    const pressure = useRandomizedNumber(1, 10);
    return computed(() => ({ pressure: stamp(pressure) }));
  },
  [SensorComponentType.Flow]: () => {
    const flow = useRandomizedNumber(1, 10);
    const temperature = useRandomizedNumber(20, 100);
    return computed(() => ({ flow: stamp(flow), temperature: stamp(temperature) }));
  },
  [SensorComponentType.Level]: () => {
    const level = useRandomizedNumber(0, 100);
    return computed(() => ({ level: stamp(level) }));
  },
  [SensorComponentType.LevelSwitch]: () => {
    const empty = useRandomizedBoolean();
    return computed(() => ({ empty: stamp(empty) }));
  },
  [SensorComponentType.Pcm]: () => {
    const charged = useRandomizedBoolean();
    return computed(() => ({ charged: stamp(charged) }));
  },
  [SensorComponentType.Pcs]: () => {
    const mode = useRandomizedState([
      ThrusterMode.Maneuvering,
      ThrusterMode.Off,
      ThrusterMode.Propulsion,
      ThrusterMode.Regeneration,
    ]);
    return computed(() => ({ mode: stamp(mode) }));
  },
  [SensorComponentType.Pump]: () => {
    const flow = useRandomizedNumber(0, 10);
    const speed = useRandomizedNumber(0, 100);
    const opTime = useRandomizedNumber(0, 1000);
    return computed(() => ({
      flow: stamp(flow),
      speed: stamp(speed),
      opTime: stamp(opTime),
    }));
  },
  [SensorComponentType.Thruster]: () => {
    const active = useRandomizedBoolean();
    return computed(() => ({ active: stamp(active) }));
  },
  [SensorComponentType.Valve]: () => {
    const positionRel = useRandomizedRatio();
    return computed(() => ({ positionRel: stamp(positionRel) }));
  },
  [SensorComponentType.HeatExchanger]: () => {
    const deltaT = useRandomizedNumber(-20, 20);
    const heat = useRandomizedNumber(0, 100);
    return computed(() => ({ deltaT: stamp(deltaT), heat: stamp(heat) }));
  },
  [SensorComponentType.DeltaT]: () => {
    const deltaT = useRandomizedNumber(-20, 20);
    return computed(() => ({ deltaT: stamp(deltaT) }));
  },
  [SensorComponentType.CalculatedFlow]: () => {
    const flow = useRandomizedNumber(0, 10);
    return computed(() => ({ flow: stamp(flow) }));
  },
  [SensorComponentType.AdsorptionChiller]: () => {
    const operating = useRandomizedBoolean();
    const noError = useRandomizedBoolean();
    const freeCooling = useRandomizedBoolean();
    return computed(() => ({
      operating: stamp(operating),
      noError: stamp(noError),
      freeCooling: stamp(freeCooling),
    }));
  },
  [SensorComponentType.Brightloop]: () => {
    const active = useRandomizedBoolean();
    return computed(() => ({ active: stamp(active) }));
  },
  [SensorComponentType.Ugrid]: () => {
    const active = useRandomizedBoolean();
    return computed(() => ({ active: stamp(active) }));
  },
  [SensorComponentType.PropulsionDrive]: () => {
    const active = useRandomizedBoolean();
    return computed(() => ({ active: stamp(active) }));
  },
  [SensorComponentType.ShorePowerConverter]: () => {
    const active = useRandomizedBoolean();
    return computed(() => ({ active: stamp(active) }));
  },
};

export const CONTROL_VALUES_FACTORY: ValueFactory<ControlDefinitionMap> = {
  [ControlComponentType.Pcm]: () => {
    const on = useRandomizedBoolean();
    return computed(() => ({ on: stamp(on) }));
  },
  [ControlComponentType.Pump]: () => {
    const on = useRandomizedBoolean();
    const dutypoint = useRandomizedNumber(0, 100);
    return computed(() => ({
      on: stamp(on),
      dutypoint: stamp(dutypoint),
    }));
  },
  [ControlComponentType.Heatpump]: () => {
    const on = useRandomizedBoolean();
    const temperatureSetpoint = useRandomizedNumber(0, 100);
    return computed(() => ({
      on: stamp(on),
      temperatureSetpoint: stamp(temperatureSetpoint),
    }));
  },
  [ControlComponentType.Valve]: () => {
    const setpoint = useRandomizedNumber(0, 100);
    return computed(() => ({
      setpoint: stamp(setpoint),
    }));
  },
  [ControlComponentType.AdsorptionChiller]: () => {
    const enable = useRandomizedBoolean();
    return computed(() => ({
      enable: stamp(enable),
    }));
  },
};
export const CONTROLLER_VALUE_VALUES_FACTORY: ValueFactory<ControllerStateDefinitionMap> = {
  [ControllerStateComponentType.DhwTanksController]: () => {
    const states = [
      BoilerTankState.Boosting,
      BoilerTankState.Disabled,
      BoilerTankState.InUse,
      BoilerTankState.NeedsBoost,
      BoilerTankState.NeedsFill,
      BoilerTankState.Standby,
    ];
    const tank1State = useRandomizedState(states);
    const tank2State = useRandomizedState(states);
    const tank3State = useRandomizedState(states);
    const timeToFill = useRandomizedNumber(0, 1000);

    return computed(() => ({
      tank1State: stamp(tank1State),
      tank2State: stamp(tank2State),
      tank3State: stamp(tank3State),
      timeToFill: stamp(timeToFill),
    }));
  },
  [ControllerStateComponentType.PIDController]: () => {
    const setpoint = useRandomizedNumber(0, 100);
    const measurement = useRandomizedNumber(0, 100);
    const output = useRandomizedNumber(0, 100);
    const error = useRandomizedNumber(-50, 50);
    const enabled = useRandomizedBoolean();
    const tuning = computed<PID>(() => [1, 2, 3]);
    const components = computed<PID>(() => [1, 2, 3]);

    return computed(() => ({
      setpoint: stamp(setpoint),
      measurement: stamp(measurement),
      output: stamp(output),
      error: stamp(error),
      enabled: stamp(enabled),
      tuning: stamp(tuning),
      components: stamp(components),
    }));
  },
};

export const PARAMETER_VALUES_FACTORY: ValueFactory<ParameterDefinitionMap> = {
  [ParametersType.Disabled]: () => useRandomizedBoolean(),
  [ParametersType.Dutypoint]: () => useRandomizedRatio(),
  [ParametersType.Enabled]: () => useRandomizedBoolean(),
  [ParametersType.Flow]: () => useRandomizedNumber(0, 10),
  [ParametersType.FlowControl]: () => useRandomizedRatio(),
  [ParametersType.Level]: () => useRandomizedNumber(0, 100),
  [ParametersType.Ratio]: () => useRandomizedRatio(),
  [ParametersType.Temperature]: () => useRandomizedNumber(20, 100),
  [ParametersType.Tuning]: () => computed(() => [1, 2, 3]),
  [ParametersType.dT]: () => useRandomizedNumber(-20, 20),
};
