import { graphql, HttpResponse } from "msw";
import allRooms from "../data/all-rooms";

export const getAllRooms = graphql.query("GetAllRooms", () =>
  HttpResponse.json({
    data: allRooms,
  }),
);
