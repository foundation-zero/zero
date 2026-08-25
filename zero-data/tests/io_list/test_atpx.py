import json
from pathlib import Path

from zero_data.io_list import read_io_list
from zero_data.io_list.atpx_meta import (
    RawField,
    classify_fields,
    read_senders,
    slugify,
)

_IO_LISTS_DIR = Path(__file__).parent / "../../io_lists/atpx"


def test_slugify():
    assert slugify("App Wind Angle") == "app_wind_angle"
    assert slugify("Heading &deg;T") == "heading_degt"
    assert slugify("ET->UT Time Delta") == "et_to_ut_time_delta"
    assert slugify("0-20ma Current") == "0_20ma_current"


def test_classify_fields_slugifies_description():
    fields = classify_fields([RawField(id=4866, description="App Wind Angle")])
    assert len(fields) == 1
    assert fields[0].id == 4866
    assert fields[0].key == "app_wind_angle"


def test_classify_fields_allows_duplicate_slugs():
    # Field_ids sharing a description keep their duplicate slug; not deduplicated.
    fields = classify_fields(
        [
            RawField(id=514, description="Boat Speed (kts)"),
            RawField(id=4610, description="Boat Speed (kts)"),
        ]
    )
    by_id = {f.id: f for f in fields}
    assert by_id[514].key == "boat_speed_kts"
    assert by_id[4610].key == "boat_speed_kts"


def test_atpx_reader_covers_every_field():
    result = read_io_list([_IO_LISTS_DIR / "atpx_fields.json"], "atpx")
    assert result.io_list.shape[0] == 378
    assert set(result.io_list.columns) == {"id", "key"}


def test_classify_fields_slugifies_user_data():
    # Fastnet "User Data N" channels from atpx_extra.json (0x7000 + N).
    fields = classify_fields([RawField(id=0x700B, description="User Data 11")])
    assert fields[0].key == "user_data_11"


def test_atpx_reader_merges_extra_fields():
    base = read_io_list([_IO_LISTS_DIR / "atpx_fields.json"], "atpx")
    extra_count = len(
        json.loads((_IO_LISTS_DIR / "atpx_extra.json").read_text())["fields"]
    )
    merged = read_io_list(
        [_IO_LISTS_DIR / "atpx_fields.json", _IO_LISTS_DIR / "atpx_extra.json"],
        "atpx",
    )
    assert merged.io_list.shape[0] == base.io_list.shape[0] + extra_count


def test_read_senders():
    senders = read_senders(_IO_LISTS_DIR / "atpx_senders.json")
    assert senders[15] == "ATProcessor"
    assert senders[5] == "Wind Board"


def test_read_senders_from_extra_file():
    # atpx_extra.json nests senders under a `senders` key alongside `fields`.
    senders = read_senders(_IO_LISTS_DIR / "atpx_extra.json")
    assert senders[8] == "MFD"
    assert senders[22] == "BFD"
    assert senders[32] == "PHD"
