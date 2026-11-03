import { buildSchema, validate } from "graphql";
import { describe, expect, it } from "vitest";
import schemaSource from "../graphql/schema.graphql?raw";
import * as Queries from "./queries.consts";

const schema = buildSchema(schemaSource);

describe("view queries", () => {
  // Per-module maps reuse the queries that are checked individually.
  const queries = Object.entries(Queries).filter(([name]) => !name.endsWith("_QUERIES"));

  it.each(queries)("%s is valid against the THRS schema", (_, query) => {
    expect(validate(schema, query as never)).toEqual([]);
  });
});
