import { Rooms } from "@/modules/domestic/graphql/types.generated";
import { Room, RoomGroup } from "../../src/modules/domestic/types";
import allRooms from "./all-rooms.json" with { type: "json" };

const toRoom = (room: Rooms): Room => ({
  id: room.id,
  name: room.name,
  group: room.group as RoomGroup,
  airConditioning: {
    actualHumidity: room.actualHumidity,
    actualTemperature: room.actualTemperature,
    humiditySetpoint: room.temperatureSetpoint,
    temperatureSetpoint: room.temperatureSetpoint,
  },
  ventilation: {
    actualCo2: 400,
    co2Setpoint: 400,
  },
  lightingGroups: room.lightingGroups.map((lg) => ({
    id: lg.id,
    name: lg.name,
    level: lg.level,
  })),
  blinds: room.blinds.map((b) => ({
    id: b.id,
    name: b.name,
    level: b.level,
    group: b.group,
  })),
  amplifier: {
    on: room.amplifierOn,
  },
});

export const rooms: Room[] = (allRooms.rooms as Rooms[]).map(toRoom);

export default { rooms };
