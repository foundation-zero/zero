import { stamp } from "@/modules/common/lib/utils";
import { Stamped } from "@/modules/common/types";
import {
  ControlComponentType,
  ControlDefinitionMap,
  SensorComponentType,
  SensorDefinitionMap,
  ThrusterMode,
} from "@/modules/thrs/types";
import { computed, Ref } from "vue";
import {
  useRandomizedBoolean,
  useRandomizedNumber,
  useRandomizedRatio,
  useRandomizedState,
} from "../instances";

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
    const dutypoint = useRandomizedNumber(0, 100);
    return computed(() => ({
      on: stamp(on),
      dutypoint: stamp(dutypoint),
    }));
  },
  [ControlComponentType.Valve]: () => {
    const setpoint = useRandomizedNumber(0, 100);
    return computed(() => ({
      setpoint: stamp(setpoint),
    }));
  },
};
