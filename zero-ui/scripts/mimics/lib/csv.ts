import { readFileSync, writeFileSync } from "node:fs";

const escapeCell = (value: string): string => {
  if (/[",\n]/.test(value)) {
    return `"${value.replaceAll('"', '""')}"`;
  }
  return value;
};

export const toCsv = (rows: Record<string, string>[]): string => {
  if (rows.length === 0) return "";
  const headers = Object.keys(rows[0]);
  const lines = [headers.map(escapeCell).join(",")];
  for (const row of rows) {
    lines.push(headers.map((header) => escapeCell(row[header] ?? "")).join(","));
  }
  return `${lines.join("\n")}\n`;
};

export const writeCsv = (filePath: string, rows: Record<string, string>[]): void => {
  writeFileSync(filePath, toCsv(rows), "utf8");
};

export const parseCsv = (content: string): Record<string, string>[] => {
  const cells: string[][] = [];
  let row: string[] = [];
  let current = "";
  let inQuotes = false;
  let i = 0;
  while (i < content.length) {
    const char = content[i];
    if (char === '"') {
      if (inQuotes && content[i + 1] === '"') {
        current += '"';
        i += 1;
      } else {
        inQuotes = !inQuotes;
      }
    } else if (char === "," && !inQuotes) {
      row.push(current);
      current = "";
    } else if ((char === "\n" || char === "\r") && !inQuotes) {
      row.push(current);
      current = "";
      if (row.length > 1 || row[0] !== "") cells.push(row);
      row = [];
    } else {
      current += char;
    }
    i += 1;
  }
  if (row.length > 0) {
    row.push(current);
    cells.push(row);
  } else if (current !== "") {
    cells.push([current]);
  }

  if (cells.length === 0) return [];
  const headers = cells[0];
  const result: Record<string, string>[] = [];
  for (const rowCells of cells.slice(1)) {
    if (rowCells.length === 1 && rowCells[0] === "") continue;
    const record: Record<string, string> = {};
    headers.forEach((header, index) => {
      record[header] = rowCells[index] ?? "";
    });
    result.push(record);
  }
  return result;
};

export const readCsv = (filePath: string): Record<string, string>[] =>
  parseCsv(readFileSync(filePath, "utf8"));
