import { Blinds, LightingGroups, Rooms } from "@/gql/graphql";
import {
  toAmplifierStatus,
  toHumiditySensor,
  toTemperatureControl,
  toTemperatureSensor,
} from "@tests/lib/helpers";
import { BlindsControl, ControlType, LightingControl, Room, RoomGroup } from "../../src/@types";
import allRooms from "./all-rooms.json" with { type: "json" };

const toBlindsControl = (blinds: Blinds): BlindsControl => ({
  id: blinds.id,
  name: blinds.name,
  value: blinds.level,
  time: Date.now(),
  type: ControlType.BLIND,
  meta: { opacity: blinds.opacity, group: blinds.group },
});

const toLightingControl = (light: LightingGroups): LightingControl => ({
  id: light.id,
  name: light.name,
  value: light.level,
  time: Date.now(),
  type: ControlType.LIGHT,
});

const toRoom = (room: Rooms): Room => ({
  id: room.id,
  name: room.name,
  group: room.group as RoomGroup,
  roomsControls: [
    ...room.blinds.map(toBlindsControl),
    ...room.lightingGroups.map(toLightingControl),
    toAmplifierStatus(room.amplifierOn),
    toTemperatureControl(room.temperatureSetpoint),
  ],
  roomsSensors: [
    toTemperatureSensor(room.actualTemperature),
    toHumiditySensor(room.actualHumidity),
  ],
});

export const rooms: Room[] = (allRooms.rooms as Rooms[]).map(toRoom);

export default { rooms };
