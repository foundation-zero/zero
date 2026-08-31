"""Golden tests for the pure `parse` function against real captured A+T sentences.

Each case is `topic -> raw sentence`, all under `atpx/nmea0183/<sender>/<TYPE>`.
Expected dicts were determined empirically by running pynmea2 against each
sentence and pinned here so the schema per sentence type is
locked and regressions are caught.
"""

import json

from zero_atpx_nmea.parser import parse


def test_rot() -> None:
    envelope = parse("$HEROT,000.1,A*2A", "atpx/nmea0183/3143/ROT")
    assert envelope is not None
    assert envelope == {
        "rate_of_turn": "000.1",  # pynmea2 declares no converter for this field
        "status": "A",
        "type": "rot",
        "sender": "3143",
        "talker": "HE",
        "raw": "$HEROT,000.1,A*2A",
    }
    json.dumps(envelope)


def test_hdt() -> None:
    envelope = parse("$HEHDT,199.1,T*2F", "atpx/nmea0183/3143/HDT")
    assert envelope is not None
    assert envelope == {
        "heading": 199.1,
        "hdg_true": "T",
        "type": "hdt",
        "sender": "3143",
        "talker": "HE",
        "raw": "$HEHDT,199.1,T*2F",
    }
    assert isinstance(envelope["heading"], float)
    json.dumps(envelope)


def test_fec_proprietary_generic() -> None:
    envelope = parse("$PFEC,xdr,FORE,050,1*64", "atpx/nmea0183/3141/FEC")
    assert envelope is not None
    assert envelope == {
        "manufacturer": "FEC",
        "data": ["", "xdr", "FORE", "050", "1"],
        "type": "fec",
        "sender": "3141",
        "talker": None,
        "raw": "$PFEC,xdr,FORE,050,1*64",
    }
    json.dumps(envelope)


def test_gga_position() -> None:
    raw = "$GPGGA,104450.00,5311.41276,N,00526.15347,E,1,40,0.4,12.1,M,46.3,M,,*5E"
    envelope = parse(raw, "atpx/nmea0183/3145/GGA")
    assert envelope is not None
    assert envelope == {
        "nmea_time": "10:44:50+00:00",
        "lat": "5311.41276",
        "lat_dir": "N",
        "lon": "00526.15347",
        "lon_dir": "E",
        "gps_qual": 1,
        "num_sats": "40",
        "horizontal_dil": "0.4",
        "altitude": 12.1,
        "altitude_units": "M",
        "geo_sep": "46.3",
        "geo_sep_units": "M",
        "age_gps_data": None,
        "ref_station_id": None,
        "latitude": 53.19021266666667,
        "longitude": 5.435891166666667,
        "type": "gga",
        "sender": "3145",
        "talker": "GP",
        "raw": raw,
    }
    assert isinstance(envelope["gps_qual"], int)
    assert isinstance(envelope["altitude"], float)
    assert isinstance(envelope["latitude"], float)
    assert isinstance(envelope["longitude"], float)
    assert envelope["age_gps_data"] is None
    assert envelope["ref_station_id"] is None
    assert "timestamp" not in envelope
    json.dumps(envelope)


def test_dbt() -> None:
    raw = "$SDDBT,23.7,f,7.2,M,3.9,F*3F"
    envelope = parse(raw, "atpx/nmea0183/3141/DBT")
    assert envelope is not None
    assert envelope == {
        "depth_feet": 23.7,
        "unit_feet": "f",
        "depth_meters": 7.2,
        "unit_meters": "M",
        "depth_fathoms": 3.9,
        "unit_fathoms": "F",
        "type": "dbt",
        "sender": "3141",
        "talker": "SD",
        "raw": raw,
    }
    assert isinstance(envelope["depth_meters"], float)
    json.dumps(envelope)


def test_dpt() -> None:
    raw = "$SDDPT,7.2,0.0,21.1*62"
    envelope = parse(raw, "atpx/nmea0183/3141/DPT")
    assert envelope is not None
    assert envelope == {
        "depth": 7.2,
        "offset": 0.0,
        "range": 21.1,
        "type": "dpt",
        "sender": "3141",
        "talker": "SD",
        "raw": raw,
    }
    assert isinstance(envelope["depth"], float)
    json.dumps(envelope)


def test_gll_position() -> None:
    raw = "$GNGLL,5311.41276,N,00526.15347,E,104450.00,A,A*76"
    envelope = parse(raw, "atpx/nmea0183/3145/GLL")
    assert envelope is not None
    assert envelope == {
        "lat": "5311.41276",
        "lat_dir": "N",
        "lon": "00526.15347",
        "lon_dir": "E",
        "nmea_time": "10:44:50+00:00",
        "status": "A",
        "faa_mode": "A",
        "latitude": 53.19021266666667,
        "longitude": 5.435891166666667,
        "type": "gll",
        "sender": "3145",
        "talker": "GN",
        "raw": raw,
    }
    assert isinstance(envelope["latitude"], float)
    assert isinstance(envelope["longitude"], float)
    assert "timestamp" not in envelope
    json.dumps(envelope)


def test_vtg() -> None:
    raw = "$GNVTG,118.99,T,115.93,M,0.06,N,0.11,K,A*3C"
    envelope = parse(raw, "atpx/nmea0183/3145/VTG")
    assert envelope is not None
    assert envelope == {
        "true_track": 118.99,
        "true_track_sym": "T",
        "mag_track": 115.93,
        "mag_track_sym": "M",
        "spd_over_grnd_kts": 0.06,
        "spd_over_grnd_kts_sym": "N",
        "spd_over_grnd_kmph": 0.11,
        "spd_over_grnd_kmph_sym": "K",
        "faa_mode": "A",
        "type": "vtg",
        "sender": "3145",
        "talker": "GN",
        "raw": raw,
    }
    assert isinstance(envelope["true_track"], float)
    json.dumps(envelope)


def test_vbw_empty_fields_become_none() -> None:
    raw = "$VDVBW,-0.08,,A,,,V,,V,,V*7D"
    envelope = parse(raw, "atpx/nmea0183/3142/VBW")
    assert envelope is not None
    assert envelope == {
        "lon_water_spd": -0.08,
        "trans_water_spd": None,
        "data_validity_water_spd": "A",
        "lon_grnd_spd": None,
        "trans_grnd_spd": None,
        "data_validity_grnd_spd": "V",
        "type": "vbw",
        "sender": "3142",
        "talker": "VD",
        "raw": raw,
    }
    assert envelope["trans_water_spd"] is None
    assert envelope["lon_grnd_spd"] is None
    assert envelope["trans_grnd_spd"] is None
    json.dumps(envelope)


def test_zda() -> None:
    raw = "$GNZDA,104450.00,26,08,2026,-00,00*5B"
    envelope = parse(raw, "atpx/nmea0183/3145/ZDA")
    assert envelope is not None
    assert envelope == {
        "nmea_time": "10:44:50+00:00",
        "day": 26,
        "month": 8,
        "year": 2026,
        "local_zone": 0,
        "local_zone_minutes": 0,
        "type": "zda",
        "sender": "3145",
        "talker": "GN",
        "raw": raw,
    }
    assert isinstance(envelope["year"], int)
    assert "timestamp" not in envelope
    json.dumps(envelope)


def test_vhw() -> None:
    raw = "$VDVHW,,T,,M,-0.08,N,-0.15,K*4B"
    envelope = parse(raw, "atpx/nmea0183/3142/VHW")
    assert envelope is not None
    assert envelope == {
        "heading_true": None,
        "true": "T",
        "heading_magnetic": None,
        "magnetic": "M",
        "water_speed_knots": -0.08,
        "knots": "N",
        "water_speed_km": -0.15,
        "kilometers": "K",
        "type": "vhw",
        "sender": "3142",
        "talker": "VD",
        "raw": raw,
    }
    assert envelope["heading_true"] is None
    assert envelope["heading_magnetic"] is None
    assert isinstance(envelope["water_speed_knots"], float)
    json.dumps(envelope)


def test_vlw() -> None:
    raw = "$VDVLW,13.79,N,13.79,N,,N,,N*5F"
    envelope = parse(raw, "atpx/nmea0183/3142/VLW")
    assert envelope is not None
    assert envelope == {
        "trip_distance": 13.79,
        "trip_distance_miles": "N",
        "trip_distance_reset": 13.79,
        "trip_distance_reset_miles": "N",
        "type": "vlw",
        "sender": "3142",
        "talker": "VD",
        "raw": raw,
    }
    assert isinstance(envelope["trip_distance"], float)
    json.dumps(envelope)


def test_rmc_position() -> None:
    raw = "$GNRMC,104450.00,A,5311.41276,N,00526.15347,E,0.06,118.99,260826,3.1,E,A,S*51"
    envelope = parse(raw, "atpx/nmea0183/3145/RMC")
    assert envelope is not None
    assert envelope == {
        "nmea_time": "10:44:50+00:00",
        "status": "A",
        "lat": "5311.41276",
        "lat_dir": "N",
        "lon": "00526.15347",
        "lon_dir": "E",
        "spd_over_grnd": 0.06,
        "true_course": 118.99,
        "datestamp": "2026-08-26",
        "mag_variation": "3.1",
        "mag_var_dir": "E",
        "mode_indicator": "A",
        "nav_status": "S",
        "latitude": 53.19021266666667,
        "longitude": 5.435891166666667,
        "type": "rmc",
        "sender": "3145",
        "talker": "GN",
        "raw": raw,
    }
    assert isinstance(envelope["latitude"], float)
    assert isinstance(envelope["longitude"], float)
    assert isinstance(envelope["spd_over_grnd"], float)
    assert "timestamp" not in envelope
    json.dumps(envelope)


def test_bad_checksum_is_dropped() -> None:
    assert parse("$HEROT,000.1,A*00", "atpx/nmea0183/3143/ROT") is None


def test_unparseable_sentence_is_dropped() -> None:
    assert parse("not a nmea sentence at all", "atpx/nmea0183/3143/ROT") is None


def test_genuinely_unknown_sentence_type_is_dropped() -> None:
    # Well-formed (valid checksum, valid talker/formatter shape) but a
    # formatter neither pynmea2 nor our custom_sentences module knows about
    # -> pynmea2 raises SentenceTypeError (a ParseError subclass) and the
    # sentence is dropped, same as any other unparseable input. This proves
    # registering ALR/ALC/POS didn't turn parse() into an "accept anything"
    # function.
    assert parse("$SDXYZ,1,2,3*50", "atpx/nmea0183/3141/XYZ") is None


def test_alr_custom_sentence() -> None:
    # $SDALR was previously dropped: pynmea2 has no built-in ALR support.
    # zero_atpx_nmea.custom_sentences registers a custom ALR class (see
    # IEC 61162-1 §8.3.15 "Set alarm state"), so it now flows
    # through the same generic envelope as any other sentence.
    raw = "$SDALR,,,V,V,*64"
    envelope = parse(raw, "atpx/nmea0183/3141/ALR")
    assert envelope is not None
    assert envelope == {
        "nmea_time": None,
        "alarm_number": None,
        "alarm_condition": "V",
        "alarm_ack_state": "V",
        "alarm_text": None,
        "type": "alr",
        "sender": "3141",
        "talker": "SD",
        "raw": raw,
    }
    assert envelope["alarm_number"] is None
    assert envelope["nmea_time"] is None
    json.dumps(envelope)


def test_alc_custom_sentence() -> None:
    # $VDALC was previously dropped: pynmea2 has no built-in ALC support.
    # zero_atpx_nmea.custom_sentences registers a custom ALC class (IEC
    # 61162-1 §8.3.13 "Cyclic alert list").
    raw = "$VDALC,01,01,65,0*6F"
    envelope = parse(raw, "atpx/nmea0183/3141/ALC")
    assert envelope is not None
    assert envelope == {
        "total_sentences": 1,
        "sentence_number": 1,
        "sequence_id": 65,
        "num_alerts": 0,
        "type": "alc",
        "sender": "3141",
        "talker": "VD",
        "raw": raw,
    }
    assert isinstance(envelope["total_sentences"], int)
    assert isinstance(envelope["num_alerts"], int)
    json.dumps(envelope)


def test_pos_custom_sentence() -> None:
    # $VDPOS was previously dropped: pynmea2 has no built-in POS support.
    # zero_atpx_nmea.custom_sentences registers a custom POS class (IEC
    # 61162-1 §8.3.76 "Device position and ship dimensions report or
    # configuration command").
    raw = "$VDPOS,VD,01,A,0.0,0.0,,V,,,R*08"
    envelope = parse(raw, "atpx/nmea0183/3141/POS")
    assert envelope is not None
    assert envelope == {
        "device_talker": "VD",
        "equipment_number": 1,
        "status": "A",
        "x_offset": 0.0,
        "y_offset": 0.0,
        "z_offset": None,
        "position_valid": "V",
        "length": None,
        "beam": None,
        "sentence_status": "R",
        "type": "pos",
        "sender": "3141",
        "talker": "VD",
        "raw": raw,
    }
    assert isinstance(envelope["equipment_number"], int)
    assert isinstance(envelope["x_offset"], float)
    assert isinstance(envelope["y_offset"], float)
    assert envelope["z_offset"] is None
    assert envelope["length"] is None
    assert envelope["beam"] is None
    json.dumps(envelope)
