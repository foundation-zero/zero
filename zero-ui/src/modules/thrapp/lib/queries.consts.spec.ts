import { DocumentNode, FragmentDefinitionNode, Kind, visit } from "graphql";
import { describe, expect, it } from "vitest";
import * as Queries from "./queries.consts";

const views = Object.entries(Queries).flatMap(([name, query]) =>
  name.endsWith("_QUERIES")
    ? Object.entries(query as Record<string, DocumentNode>).map(
        ([module, document]) => [`${name}.${module}`, document] as const,
      )
    : [[name, query as DocumentNode] as const],
);

/** The names of the fragments a query defines and the ones it spreads. */
const fragments = (document: DocumentNode) => {
  const defined = document.definitions
    .filter(
      (definition): definition is FragmentDefinitionNode =>
        definition.kind === Kind.FRAGMENT_DEFINITION,
    )
    .map((definition) => definition.name.value);
  const spread: string[] = [];
  visit(document, { FragmentSpread: (node) => void spread.push(node.name.value) });
  return { defined, spread: [...new Set(spread)] };
};

describe("view queries", () => {
  it.each(views)("%s defines exactly the fragments it spreads", (_, document) => {
    const { defined, spread } = fragments(document);

    expect(defined.toSorted()).toEqual(spread.toSorted());
  });

  it.each(views)("%s defines each fragment once", (_, document) => {
    const { defined } = fragments(document);

    expect(defined).toEqual([...new Set(defined)]);
  });
});
