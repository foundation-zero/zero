import { graphql, HttpResponse } from "msw";
import allRooms from "../data/all-rooms";

export const getAllRooms = graphql.query("GetAllRooms", () =>
  HttpResponse.json({
    data: allRooms,
  }),
);

export const getControlLogs = graphql.query("GetControlLogs", () =>
  HttpResponse.json({
    data: { controlsLog: [] },
  }),
);

export const getSensorLogs = graphql.query("GetSensorLogs", () =>
  HttpResponse.json({
    data: { sensorsLog: [] },
  }),
);

export const getVersion = graphql.query("GetVersion", () =>
  HttpResponse.json({
    data: { version: "1.0.0" },
  }),
);
