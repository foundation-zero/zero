import { graphql, http, HttpResponse } from "msw";
import allRooms from "../data/all-rooms";
import powerTags from "../data/power-tags";

export const getAllRooms = graphql.query("GetAllRooms", () =>
  HttpResponse.json({
    data: allRooms,
  }),
);

export const getVersion = graphql.query("GetVersion", () =>
  HttpResponse.json({
    data: { version: "1.0.0" },
  }),
);
