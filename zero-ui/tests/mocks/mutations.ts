import { graphql } from "msw/graphql";

const api = graphql.link(process.env.VITE_GRAPHQL_URL!);

export const setLightLevel = api.mutation("SetGroupLightLevel", () => {});
