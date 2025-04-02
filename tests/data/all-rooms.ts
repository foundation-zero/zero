import { Rooms } from "../../src/gql/graphql";
import allRooms from "./all-rooms.json" with { type: "json" };

export default allRooms as { rooms: Rooms[] };
