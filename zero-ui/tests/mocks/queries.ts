import { HttpResponse } from "msw";
import { graphql } from "msw/graphql";
import allRooms from "../data/all-rooms";

const api = graphql.link(process.env.VITE_GRAPHQL_URL!);

export const getAllRooms = api.query("GetAllRooms", () =>
  HttpResponse.json({
    data: allRooms,
  }),
);

export const getVersion = api.query("GetVersion", () =>
  HttpResponse.json({
    data: { version: "1.0.0" },
  }),
);
