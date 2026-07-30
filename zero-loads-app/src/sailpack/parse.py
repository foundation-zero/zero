from pathlib import Path

import polars as pl
from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag


def parse_directory(input_source: Path) -> pl.DataFrame:
    if input_source.is_file():
        raise ValueError(
            "Expected a sailpack directory containing .htm files, "
            f"got file: {input_source}"
        )

    if not input_source.exists():
        raise FileNotFoundError(f"Input directory not found: {input_source}")
    frames = []
    for file in input_source.glob("*.htm"):
        frame = parse_sailpack(file)
        frames.append(frame)

    if not frames:
        raise ValueError(f"No .htm files found in sailpack directory: {input_source}")

    return pl.concat(frames, how="diagonal")


def parse_sailpack(file_path: Path) -> pl.DataFrame:
    with open(file_path, "r", encoding="latin-1", errors="ignore") as f:
        soup = BeautifulSoup(f, "html.parser")

    calc_id = (
        soup.find("b", string="Calculation ID").find_next("i").get_text(strip=True)  # type: ignore
    )

    frames = [*parse_tables(file_path, soup), extract_notes(soup)]

    return pl.concat(frames, how="diagonal").with_columns(
        pl.lit(calc_id).alias("Calculation ID"),
        pl.lit(file_path.stem).alias("source_file"),
    )


def extract_notes(soup: BeautifulSoup) -> pl.DataFrame:
    result: dict[str, str] = {}
    notes = soup.find("b", string="NOTES")

    if not isinstance(notes, Tag):
        return pl.DataFrame(result).with_columns(
            pl.lit("NOTES").alias("table_description")
        )

    for tag in notes.next_siblings:
        if isinstance(tag, Tag):
            if tag.name == "b":
                break
            text = tag.get_text(strip=True)
        elif isinstance(tag, NavigableString):
            text = str(tag).strip()
        else:
            continue

        if not text:
            continue

        if "Calculation date" in text:
            result.update({"Calculation date": text.split(":", 1)[1].strip()})

        if "TWS/TWA" in text:
            result.update(
                {
                    k: v
                    for k, v in (
                        part.split(":", 1) for part in text.split(" - ") if ":" in part
                    )
                }
            )

        if "BS" in text:
            result.update(
                {
                    k: v
                    for k, v in (
                        part.split(":", 1) for part in text.split(" - ") if ":" in part
                    )
                }
            )

    return pl.DataFrame(result).with_columns(pl.lit("NOTES").alias("table_description"))


def expand_header(header: list):
    expanded_header = []
    for th in header:
        expanded_header.extend([th.get_text(strip=True)] * int(th.get("colspan", 1)))
    return expanded_header


def merge_headers(headers: list[list]) -> list[str]:
    if not headers:
        return []
    elif len(headers) == 1:
        return headers[0]
    elif len(headers) == 2:
        return [
            f"{second} - {first}" if first else second
            for first, second in zip(headers[0], headers[1])
        ]
    else:
        raise ValueError(f"More than two head rows found: {headers}")


def parse_tables(file_path: Path, soup: BeautifulSoup) -> list[pl.DataFrame]:
    tables = soup.find_all("table")
    result = []
    for table in tables:
        previous_tag = table.find_previous("b")
        table_description = previous_tag.get_text(strip=True) if previous_tag else ""

        if not table_description or table_description == "HEEL":
            continue  # TODO: check condition to skip HEEL table

        header = merge_headers(
            [
                expand_header(tr.find_all("th"))
                for tr in table.find_all("tr")
                if tr.find_all("th")
            ]
        )

        if not header:
            continue

        rows = [
            [td.get_text(strip=True) for td in tr.find_all("td")]
            for tr in table.find_all("tr")
            if tr.find_all("td")
        ]

        try:
            result.append(
                pl.DataFrame(rows, schema=header, orient="row").with_columns(
                    pl.lit(table_description).alias("table_description"),
                )
            )
        except Exception as e:
            print(
                f"Error parsing table: {table_description}, rows: {rows}, header: {header}"
            )
            print(e)

    return result
