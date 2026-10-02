#!/usr/bin/env node

/**
 * Script to convert raw Figma-exported arrow paths in a mimic module's DirectionArrows.vue
 * into <line> elements with a marker-end arrowhead, matching the hand-authored convention
 * used across mimic modules (see src/modules/thrapp/mimics/modules/dhw/layers/DirectionArrows.vue).
 *
 * Figma exports each directional arrow as a filled <path> made of three subpaths: a small
 * end-cap square, a chevron (the arrowhead, identifiable by its cubic-bezier "C" commands),
 * and a thin rectangle spanning the arrow's length. This script parses each path's "d"
 * attribute, recovers the line's two endpoints from the rectangle subpath, and determines
 * which endpoint carries the arrowhead by finding the endpoint closest to the chevron.
 *
 * Usage:
 *   pnpm convert-direction-arrows <module>
 *
 * Example:
 *   pnpm convert-direction-arrows dc
 *   pnpm convert-direction-arrows dhw
 *
 * The <module> is the folder name under src/modules/thrapp/mimics/modules/<module>/layers/DirectionArrows.vue.
 */

import { execSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const MARKER_CLASS = "stroke-flows-pipe-arrow";
const MARKER_ID = "flows-dir-arrow";

// ============================================================================
// Minimal SVG path parsing (absolute M/L/H/V/C commands only)
// ============================================================================

type Subpath = {
  minX: number;
  maxX: number;
  minY: number;
  maxY: number;
  hasCurve: boolean;
};

const tokenize = (d: string) => d.match(/[MLHVCZ]|-?\d*\.?\d+(?:e-?\d+)?/gi) ?? [];

const parseSubpaths = (d: string): Subpath[] => {
  const tokens = tokenize(d);
  let i = 0;
  let cx = 0;
  let cy = 0;
  const subpaths: Subpath[] = [];
  let current: Subpath | null = null;

  const pushPoint = (x: number, y: number) => {
    if (!current) return;
    current.minX = Math.min(current.minX, x);
    current.maxX = Math.max(current.maxX, x);
    current.minY = Math.min(current.minY, y);
    current.maxY = Math.max(current.maxY, y);
  };

  while (i < tokens.length) {
    const tok = tokens[i];
    if (!/^[MLHVCZ]$/i.test(tok)) {
      // Stray number without a command; skip defensively.
      i++;
      continue;
    }
    const cmd = tok.toUpperCase();
    i++;
    switch (cmd) {
      case "M":
        cx = parseFloat(tokens[i++]);
        cy = parseFloat(tokens[i++]);
        current = { minX: cx, maxX: cx, minY: cy, maxY: cy, hasCurve: false };
        subpaths.push(current);
        break;
      case "L":
        cx = parseFloat(tokens[i++]);
        cy = parseFloat(tokens[i++]);
        pushPoint(cx, cy);
        break;
      case "H":
        cx = parseFloat(tokens[i++]);
        pushPoint(cx, cy);
        break;
      case "V":
        cy = parseFloat(tokens[i++]);
        pushPoint(cx, cy);
        break;
      case "C": {
        const x1 = parseFloat(tokens[i++]);
        const y1 = parseFloat(tokens[i++]);
        const x2 = parseFloat(tokens[i++]);
        const y2 = parseFloat(tokens[i++]);
        const x = parseFloat(tokens[i++]);
        const y = parseFloat(tokens[i++]);
        if (current) current.hasCurve = true;
        pushPoint(x1, y1);
        pushPoint(x2, y2);
        pushPoint(x, y);
        cx = x;
        cy = y;
        break;
      }
      case "Z":
        // Subpath closed; current point is conceptually back at its start.
        break;
    }
  }
  return subpaths;
};

type Line = { x1: number; y1: number; x2: number; y2: number };

const round = (n: number) => Math.round(n * 100) / 100;

/** Returns null when the path doesn't look like a Figma arrow (no chevron subpath found). */
const pathToLine = (d: string): Line | null => {
  const subs = parseSubpaths(d);
  const chevron = subs.find((s) => s.hasCurve);
  if (!chevron) return null;

  const rect = subs
    .filter((s) => s !== chevron)
    .reduce((a, b) => {
      const spanA = Math.max(a.maxX - a.minX, a.maxY - a.minY);
      const spanB = Math.max(b.maxX - b.minX, b.maxY - b.minY);
      return spanB > spanA ? b : a;
    });

  const width = rect.maxX - rect.minX;
  const height = rect.maxY - rect.minY;

  if (width > height) {
    const cy = (rect.minY + rect.maxY) / 2;
    const chevronCx = (chevron.minX + chevron.maxX) / 2;
    const arrowAtMin = Math.abs(chevronCx - rect.minX) < Math.abs(chevronCx - rect.maxX);
    return arrowAtMin
      ? { x1: round(rect.maxX), y1: round(cy), x2: round(rect.minX), y2: round(cy) }
      : { x1: round(rect.minX), y1: round(cy), x2: round(rect.maxX), y2: round(cy) };
  }

  const cx = (rect.minX + rect.maxX) / 2;
  const chevronCy = (chevron.minY + chevron.maxY) / 2;
  const arrowAtMin = Math.abs(chevronCy - rect.minY) < Math.abs(chevronCy - rect.maxY);
  return arrowAtMin
    ? { x1: round(cx), y1: round(rect.maxY), x2: round(cx), y2: round(rect.minY) }
    : { x1: round(cx), y1: round(rect.minY), x2: round(cx), y2: round(rect.maxY) };
};

// ============================================================================
// File transformation
// ============================================================================

const extractArrowPaths = (svgInner: string) => {
  const pathRegex = /<path\b([\s\S]*?)\/>/g;
  const matches: { start: number; end: number; d: string }[] = [];
  let match: RegExpExecArray | null;
  while ((match = pathRegex.exec(svgInner)) !== null) {
    const attrs = match[1];
    if (!/fill-opacity="0\.55"/.test(attrs)) continue;
    const dMatch = attrs.match(/d="([^"]+)"/);
    if (!dMatch) continue;
    matches.push({ start: match.index, end: match.index + match[0].length, d: dMatch[1] });
  }
  return matches;
};

const extractDefsBlocks = (svgInner: string) => {
  const defsRegex = /<defs>([\s\S]*?)<\/defs>/g;
  const matches: { fullMatch: string; inner: string }[] = [];
  let match: RegExpExecArray | null;
  while ((match = defsRegex.exec(svgInner)) !== null) {
    matches.push({ fullMatch: match[0], inner: match[1] });
  }
  return matches;
};

const buildLineTag = ({ x1, y1, x2, y2 }: Line) =>
  `      <line\n        x1="${x1}"\n        y1="${y1}"\n        x2="${x2}"\n        y2="${y2}"\n      />`;

const convertFile = (filePath: string) => {
  const content = fs.readFileSync(filePath, "utf8");

  const svgMatch = content.match(/<svg\b([^>]*)>([\s\S]*)<\/svg>/);
  if (!svgMatch) {
    throw new Error(`No <svg> root found in ${filePath}`);
  }
  const svgAttrs = svgMatch[1];
  let inner = svgMatch[2];

  const arrowPaths = extractArrowPaths(inner);
  if (arrowPaths.length === 0) {
    throw new Error(
      `No arrow paths (fill-opacity="0.55") found in ${filePath} — already converted?`,
    );
  }

  const lines: Line[] = [];
  const skipped: string[] = [];
  const rangesToRemove: { start: number; end: number }[] = [];
  for (const { start, end, d } of arrowPaths) {
    const line = pathToLine(d);
    if (!line) {
      skipped.push(d);
      continue;
    }
    lines.push(line);
    rangesToRemove.push({ start, end });
  }

  if (lines.length === 0) {
    throw new Error(
      `Found ${arrowPaths.length} candidate path(s) but none had a detectable chevron in ${filePath}`,
    );
  }

  // Remove converted paths by index range (back to front) instead of string-replace,
  // since two arrows can share an identical "d" string.
  for (const { start, end } of rangesToRemove.sort((a, b) => b.start - a.start)) {
    inner = inner.slice(0, start) + inner.slice(end);
  }

  const defsBlocks = extractDefsBlocks(inner);
  for (const { fullMatch } of defsBlocks) {
    inner = inner.replace(fullMatch, "");
  }
  const extraDefsInner = defsBlocks.map((b) => b.inner.trim()).join("\n");

  const extraContent = inner.replace(/\n\s*\n/g, "\n").trim();

  const markerDef = `      <marker
        id="${MARKER_ID}"
        markerWidth="6"
        markerHeight="7"
        refX="3.5"
        refY="3.5"
        orient="auto"
        markerUnits="userSpaceOnUse"
      >
        <path
          d="M0.75 0.75L4.25 3.5L0.75 6.25"
          class="${MARKER_CLASS}"
          fill="none"
          stroke-width="1"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </marker>`;

  const defsInner = [markerDef, extraDefsInner].filter(Boolean).join("\n");

  const linesBlock = lines.map(buildLineTag).join("\n");

  const output = `<template>
  <svg${svgAttrs}>
    <defs>
${defsInner}
    </defs>
    <g
      class="${MARKER_CLASS}"
      stroke-width="1"
      fill="none"
      marker-end="url(#${MARKER_ID})"
    >
${linesBlock}
    </g>
    ${extraContent}
  </svg>
</template>
`;

  fs.writeFileSync(filePath, output);

  return { converted: lines.length, skipped };
};

// ============================================================================
// CLI
// ============================================================================

const moduleName = process.argv[2];
if (!moduleName) {
  console.error("Usage: pnpm convert-direction-arrows <module>");
  console.error("Example: pnpm convert-direction-arrows dc");
  process.exit(1);
}

const filePath = path.join(
  __dirname,
  "../src/modules/thrapp/mimics/modules",
  moduleName,
  "layers/DirectionArrows.vue",
);

if (!fs.existsSync(filePath)) {
  console.error(`No DirectionArrows.vue found for module "${moduleName}" at ${filePath}`);
  process.exit(1);
}

const { converted, skipped } = convertFile(filePath);

execSync(`npx prettier --write "${filePath}"`, { stdio: "inherit" });

console.log(
  `Converted ${converted} arrow path(s) to <line> in ${path.relative(process.cwd(), filePath)}`,
);
if (skipped.length > 0) {
  console.warn(`Skipped ${skipped.length} path(s) with no detectable chevron (left unchanged):`);
  skipped.forEach((d) => console.warn(`  ${d}`));
}
