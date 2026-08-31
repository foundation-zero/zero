
    const schema = {
  "asyncapi": "3.0.0",
  "info": {
    "title": "Zero ATPX NMEA",
    "version": "0.1.0",
    "description": "Zero ATPX NMEA bridges A+T's raw NMEA 0183 stream onto our own MQTT broker. It subscribes to `atpx/nmea0183/<sender>/<TYPE>` on **A+T's onboard broker** (the ATPX MQTT host), parses each sentence with pynmea2 into a JSON envelope, and republishes it to `atpx/processed/nmea/<type>/<sender>` on **our own MQTT broker** (the output MQTT host). Vector then ingests `atpx/processed/nmea/#` into Greptime tables named `atpx__nmea_<type>`.\n\n**Known-type scope.** The documented type set below is the known/supported subset for which this service has been tested with real A+T data. The service subscribes to `atpx/nmea0183/#` and will parse any well-formed NMEA 0183 sentence it receives, including types not listed here — the envelope for an undocumented type will simply carry whatever fields pynmea2 produces for it rather than a curated schema. Adding a new documented type is a one-line corpus addition plus a spec regeneration."
  },
  "channels": {
    "atpx/nmea0183/{sender}/{TYPE}": {
      "address": "atpx/nmea0183/{sender}/{TYPE}",
      "title": "Raw NMEA 0183 input from A+T broker",
      "description": "Raw NMEA 0183 sentences published by A+T's onboard systems. ``{sender}`` identifies the A+T device (e.g. ``3143``, ``3145``), ``{TYPE}`` is the uppercase NMEA 0183 sentence type (e.g. ``ROT``, ``GGA``).",
      "parameters": {
        "sender": {
          "description": "A+T device identifier (e.g. 3143, 3145, 3141, 3142)",
          "location": "$message.header#/topic/parts/2"
        },
        "TYPE": {
          "description": "Uppercase NMEA 0183 sentence type (e.g. ROT, GGA, RMC)",
          "location": "$message.header#/topic/parts/3"
        }
      },
      "messages": {
        "raw_nmea_sentence": {
          "name": "raw_nmea_sentence",
          "title": "Raw NMEA 0183 sentence",
          "description": "A single raw NMEA 0183 sentence as received from A+T",
          "contentType": "text/plain",
          "payload": {
            "type": "string",
            "description": "Raw NMEA 0183 sentence string, e.g. ``$GPGGA,...*hh``",
            "x-parser-schema-id": "<anonymous-schema-3>"
          },
          "x-parser-unique-object-id": "raw_nmea_sentence"
        }
      },
      "x-parser-unique-object-id": "atpx/nmea0183/{sender}/{TYPE}"
    },
    "atpx/processed/nmea/rot/{sender}": {
      "address": "atpx/processed/nmea/rot/{sender}",
      "title": "ROT processed envelope",
      "description": "Parsed JSON envelope for NMEA 0183 ROT sentences. ``{sender}`` identifies the originating A+T device.",
      "parameters": {
        "sender": {
          "description": "A+T device identifier (e.g. 3143, 3145)",
          "location": "$message.header#/topic/parts/4"
        }
      },
      "messages": {
        "rot_envelope": {
          "name": "rot_envelope",
          "title": "ROT envelope",
          "description": "Parsed payload for NMEA 0183 ROT sentence type",
          "contentType": "application/json",
          "payload": {
            "type": "object",
            "properties": {
              "rate_of_turn": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-6>"
              },
              "status": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-7>"
              },
              "type": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-8>"
              },
              "sender": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-9>"
              },
              "talker": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-10>"
              },
              "raw": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-11>"
              }
            },
            "required": [
              "type",
              "sender",
              "talker",
              "raw"
            ],
            "x-parser-schema-id": "<anonymous-schema-5>"
          },
          "x-parser-unique-object-id": "rot_envelope"
        }
      },
      "x-parser-unique-object-id": "atpx/processed/nmea/rot/{sender}"
    },
    "atpx/processed/nmea/hdt/{sender}": {
      "address": "atpx/processed/nmea/hdt/{sender}",
      "title": "HDT processed envelope",
      "description": "Parsed JSON envelope for NMEA 0183 HDT sentences. ``{sender}`` identifies the originating A+T device.",
      "parameters": {
        "sender": {
          "description": "A+T device identifier (e.g. 3143, 3145)",
          "location": "$message.header#/topic/parts/4"
        }
      },
      "messages": {
        "hdt_envelope": {
          "name": "hdt_envelope",
          "title": "HDT envelope",
          "description": "Parsed payload for NMEA 0183 HDT sentence type",
          "contentType": "application/json",
          "payload": {
            "type": "object",
            "properties": {
              "heading": {
                "type": [
                  "number",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-14>"
              },
              "hdg_true": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-15>"
              },
              "type": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-16>"
              },
              "sender": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-17>"
              },
              "talker": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-18>"
              },
              "raw": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-19>"
              }
            },
            "required": [
              "type",
              "sender",
              "talker",
              "raw"
            ],
            "x-parser-schema-id": "<anonymous-schema-13>"
          },
          "x-parser-unique-object-id": "hdt_envelope"
        }
      },
      "x-parser-unique-object-id": "atpx/processed/nmea/hdt/{sender}"
    },
    "atpx/processed/nmea/fec/{sender}": {
      "address": "atpx/processed/nmea/fec/{sender}",
      "title": "FEC processed envelope",
      "description": "Parsed JSON envelope for NMEA 0183 FEC sentences. ``{sender}`` identifies the originating A+T device.",
      "parameters": {
        "sender": {
          "description": "A+T device identifier (e.g. 3143, 3145)",
          "location": "$message.header#/topic/parts/4"
        }
      },
      "messages": {
        "fec_envelope": {
          "name": "fec_envelope",
          "title": "FEC envelope",
          "description": "Parsed payload for NMEA 0183 FEC sentence type",
          "contentType": "application/json",
          "payload": {
            "type": "object",
            "properties": {
              "manufacturer": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-22>"
              },
              "data": {
                "type": [
                  "array",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-23>"
              },
              "type": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-24>"
              },
              "sender": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-25>"
              },
              "talker": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-26>"
              },
              "raw": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-27>"
              }
            },
            "required": [
              "type",
              "sender",
              "talker",
              "raw"
            ],
            "x-parser-schema-id": "<anonymous-schema-21>"
          },
          "x-parser-unique-object-id": "fec_envelope"
        }
      },
      "x-parser-unique-object-id": "atpx/processed/nmea/fec/{sender}"
    },
    "atpx/processed/nmea/gga/{sender}": {
      "address": "atpx/processed/nmea/gga/{sender}",
      "title": "GGA processed envelope",
      "description": "Parsed JSON envelope for NMEA 0183 GGA sentences. ``{sender}`` identifies the originating A+T device.",
      "parameters": {
        "sender": {
          "description": "A+T device identifier (e.g. 3143, 3145)",
          "location": "$message.header#/topic/parts/4"
        }
      },
      "messages": {
        "gga_envelope": {
          "name": "gga_envelope",
          "title": "GGA envelope",
          "description": "Parsed payload for NMEA 0183 GGA sentence type",
          "contentType": "application/json",
          "payload": {
            "type": "object",
            "properties": {
              "nmea_time": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-30>"
              },
              "lat": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-31>"
              },
              "lat_dir": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-32>"
              },
              "lon": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-33>"
              },
              "lon_dir": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-34>"
              },
              "gps_qual": {
                "type": [
                  "integer",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-35>"
              },
              "num_sats": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-36>"
              },
              "horizontal_dil": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-37>"
              },
              "altitude": {
                "type": [
                  "number",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-38>"
              },
              "altitude_units": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-39>"
              },
              "geo_sep": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-40>"
              },
              "geo_sep_units": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-41>"
              },
              "age_gps_data": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-42>"
              },
              "ref_station_id": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-43>"
              },
              "latitude": {
                "type": [
                  "number",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-44>"
              },
              "longitude": {
                "type": [
                  "number",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-45>"
              },
              "type": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-46>"
              },
              "sender": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-47>"
              },
              "talker": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-48>"
              },
              "raw": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-49>"
              }
            },
            "required": [
              "type",
              "sender",
              "talker",
              "raw"
            ],
            "x-parser-schema-id": "<anonymous-schema-29>"
          },
          "x-parser-unique-object-id": "gga_envelope"
        }
      },
      "x-parser-unique-object-id": "atpx/processed/nmea/gga/{sender}"
    },
    "atpx/processed/nmea/dbt/{sender}": {
      "address": "atpx/processed/nmea/dbt/{sender}",
      "title": "DBT processed envelope",
      "description": "Parsed JSON envelope for NMEA 0183 DBT sentences. ``{sender}`` identifies the originating A+T device.",
      "parameters": {
        "sender": {
          "description": "A+T device identifier (e.g. 3143, 3145)",
          "location": "$message.header#/topic/parts/4"
        }
      },
      "messages": {
        "dbt_envelope": {
          "name": "dbt_envelope",
          "title": "DBT envelope",
          "description": "Parsed payload for NMEA 0183 DBT sentence type",
          "contentType": "application/json",
          "payload": {
            "type": "object",
            "properties": {
              "depth_feet": {
                "type": [
                  "number",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-52>"
              },
              "unit_feet": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-53>"
              },
              "depth_meters": {
                "type": [
                  "number",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-54>"
              },
              "unit_meters": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-55>"
              },
              "depth_fathoms": {
                "type": [
                  "number",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-56>"
              },
              "unit_fathoms": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-57>"
              },
              "type": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-58>"
              },
              "sender": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-59>"
              },
              "talker": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-60>"
              },
              "raw": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-61>"
              }
            },
            "required": [
              "type",
              "sender",
              "talker",
              "raw"
            ],
            "x-parser-schema-id": "<anonymous-schema-51>"
          },
          "x-parser-unique-object-id": "dbt_envelope"
        }
      },
      "x-parser-unique-object-id": "atpx/processed/nmea/dbt/{sender}"
    },
    "atpx/processed/nmea/dpt/{sender}": {
      "address": "atpx/processed/nmea/dpt/{sender}",
      "title": "DPT processed envelope",
      "description": "Parsed JSON envelope for NMEA 0183 DPT sentences. ``{sender}`` identifies the originating A+T device.",
      "parameters": {
        "sender": {
          "description": "A+T device identifier (e.g. 3143, 3145)",
          "location": "$message.header#/topic/parts/4"
        }
      },
      "messages": {
        "dpt_envelope": {
          "name": "dpt_envelope",
          "title": "DPT envelope",
          "description": "Parsed payload for NMEA 0183 DPT sentence type",
          "contentType": "application/json",
          "payload": {
            "type": "object",
            "properties": {
              "depth": {
                "type": [
                  "number",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-64>"
              },
              "offset": {
                "type": [
                  "number",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-65>"
              },
              "range": {
                "type": [
                  "number",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-66>"
              },
              "type": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-67>"
              },
              "sender": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-68>"
              },
              "talker": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-69>"
              },
              "raw": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-70>"
              }
            },
            "required": [
              "type",
              "sender",
              "talker",
              "raw"
            ],
            "x-parser-schema-id": "<anonymous-schema-63>"
          },
          "x-parser-unique-object-id": "dpt_envelope"
        }
      },
      "x-parser-unique-object-id": "atpx/processed/nmea/dpt/{sender}"
    },
    "atpx/processed/nmea/gll/{sender}": {
      "address": "atpx/processed/nmea/gll/{sender}",
      "title": "GLL processed envelope",
      "description": "Parsed JSON envelope for NMEA 0183 GLL sentences. ``{sender}`` identifies the originating A+T device.",
      "parameters": {
        "sender": {
          "description": "A+T device identifier (e.g. 3143, 3145)",
          "location": "$message.header#/topic/parts/4"
        }
      },
      "messages": {
        "gll_envelope": {
          "name": "gll_envelope",
          "title": "GLL envelope",
          "description": "Parsed payload for NMEA 0183 GLL sentence type",
          "contentType": "application/json",
          "payload": {
            "type": "object",
            "properties": {
              "lat": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-73>"
              },
              "lat_dir": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-74>"
              },
              "lon": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-75>"
              },
              "lon_dir": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-76>"
              },
              "nmea_time": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-77>"
              },
              "status": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-78>"
              },
              "faa_mode": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-79>"
              },
              "latitude": {
                "type": [
                  "number",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-80>"
              },
              "longitude": {
                "type": [
                  "number",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-81>"
              },
              "type": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-82>"
              },
              "sender": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-83>"
              },
              "talker": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-84>"
              },
              "raw": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-85>"
              }
            },
            "required": [
              "type",
              "sender",
              "talker",
              "raw"
            ],
            "x-parser-schema-id": "<anonymous-schema-72>"
          },
          "x-parser-unique-object-id": "gll_envelope"
        }
      },
      "x-parser-unique-object-id": "atpx/processed/nmea/gll/{sender}"
    },
    "atpx/processed/nmea/vtg/{sender}": {
      "address": "atpx/processed/nmea/vtg/{sender}",
      "title": "VTG processed envelope",
      "description": "Parsed JSON envelope for NMEA 0183 VTG sentences. ``{sender}`` identifies the originating A+T device.",
      "parameters": {
        "sender": {
          "description": "A+T device identifier (e.g. 3143, 3145)",
          "location": "$message.header#/topic/parts/4"
        }
      },
      "messages": {
        "vtg_envelope": {
          "name": "vtg_envelope",
          "title": "VTG envelope",
          "description": "Parsed payload for NMEA 0183 VTG sentence type",
          "contentType": "application/json",
          "payload": {
            "type": "object",
            "properties": {
              "true_track": {
                "type": [
                  "number",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-88>"
              },
              "true_track_sym": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-89>"
              },
              "mag_track": {
                "type": [
                  "number",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-90>"
              },
              "mag_track_sym": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-91>"
              },
              "spd_over_grnd_kts": {
                "type": [
                  "number",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-92>"
              },
              "spd_over_grnd_kts_sym": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-93>"
              },
              "spd_over_grnd_kmph": {
                "type": [
                  "number",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-94>"
              },
              "spd_over_grnd_kmph_sym": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-95>"
              },
              "faa_mode": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-96>"
              },
              "type": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-97>"
              },
              "sender": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-98>"
              },
              "talker": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-99>"
              },
              "raw": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-100>"
              }
            },
            "required": [
              "type",
              "sender",
              "talker",
              "raw"
            ],
            "x-parser-schema-id": "<anonymous-schema-87>"
          },
          "x-parser-unique-object-id": "vtg_envelope"
        }
      },
      "x-parser-unique-object-id": "atpx/processed/nmea/vtg/{sender}"
    },
    "atpx/processed/nmea/vbw/{sender}": {
      "address": "atpx/processed/nmea/vbw/{sender}",
      "title": "VBW processed envelope",
      "description": "Parsed JSON envelope for NMEA 0183 VBW sentences. ``{sender}`` identifies the originating A+T device.",
      "parameters": {
        "sender": {
          "description": "A+T device identifier (e.g. 3143, 3145)",
          "location": "$message.header#/topic/parts/4"
        }
      },
      "messages": {
        "vbw_envelope": {
          "name": "vbw_envelope",
          "title": "VBW envelope",
          "description": "Parsed payload for NMEA 0183 VBW sentence type",
          "contentType": "application/json",
          "payload": {
            "type": "object",
            "properties": {
              "lon_water_spd": {
                "type": [
                  "number",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-103>"
              },
              "trans_water_spd": {
                "type": [
                  "number",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-104>"
              },
              "data_validity_water_spd": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-105>"
              },
              "lon_grnd_spd": {
                "type": [
                  "number",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-106>"
              },
              "trans_grnd_spd": {
                "type": [
                  "number",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-107>"
              },
              "data_validity_grnd_spd": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-108>"
              },
              "type": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-109>"
              },
              "sender": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-110>"
              },
              "talker": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-111>"
              },
              "raw": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-112>"
              }
            },
            "required": [
              "type",
              "sender",
              "talker",
              "raw"
            ],
            "x-parser-schema-id": "<anonymous-schema-102>"
          },
          "x-parser-unique-object-id": "vbw_envelope"
        }
      },
      "x-parser-unique-object-id": "atpx/processed/nmea/vbw/{sender}"
    },
    "atpx/processed/nmea/zda/{sender}": {
      "address": "atpx/processed/nmea/zda/{sender}",
      "title": "ZDA processed envelope",
      "description": "Parsed JSON envelope for NMEA 0183 ZDA sentences. ``{sender}`` identifies the originating A+T device.",
      "parameters": {
        "sender": {
          "description": "A+T device identifier (e.g. 3143, 3145)",
          "location": "$message.header#/topic/parts/4"
        }
      },
      "messages": {
        "zda_envelope": {
          "name": "zda_envelope",
          "title": "ZDA envelope",
          "description": "Parsed payload for NMEA 0183 ZDA sentence type",
          "contentType": "application/json",
          "payload": {
            "type": "object",
            "properties": {
              "nmea_time": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-115>"
              },
              "day": {
                "type": [
                  "integer",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-116>"
              },
              "month": {
                "type": [
                  "integer",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-117>"
              },
              "year": {
                "type": [
                  "integer",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-118>"
              },
              "local_zone": {
                "type": [
                  "integer",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-119>"
              },
              "local_zone_minutes": {
                "type": [
                  "integer",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-120>"
              },
              "type": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-121>"
              },
              "sender": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-122>"
              },
              "talker": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-123>"
              },
              "raw": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-124>"
              }
            },
            "required": [
              "type",
              "sender",
              "talker",
              "raw"
            ],
            "x-parser-schema-id": "<anonymous-schema-114>"
          },
          "x-parser-unique-object-id": "zda_envelope"
        }
      },
      "x-parser-unique-object-id": "atpx/processed/nmea/zda/{sender}"
    },
    "atpx/processed/nmea/vhw/{sender}": {
      "address": "atpx/processed/nmea/vhw/{sender}",
      "title": "VHW processed envelope",
      "description": "Parsed JSON envelope for NMEA 0183 VHW sentences. ``{sender}`` identifies the originating A+T device.",
      "parameters": {
        "sender": {
          "description": "A+T device identifier (e.g. 3143, 3145)",
          "location": "$message.header#/topic/parts/4"
        }
      },
      "messages": {
        "vhw_envelope": {
          "name": "vhw_envelope",
          "title": "VHW envelope",
          "description": "Parsed payload for NMEA 0183 VHW sentence type",
          "contentType": "application/json",
          "payload": {
            "type": "object",
            "properties": {
              "heading_true": {
                "type": [
                  "number",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-127>"
              },
              "true": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-128>"
              },
              "heading_magnetic": {
                "type": [
                  "number",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-129>"
              },
              "magnetic": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-130>"
              },
              "water_speed_knots": {
                "type": [
                  "number",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-131>"
              },
              "knots": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-132>"
              },
              "water_speed_km": {
                "type": [
                  "number",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-133>"
              },
              "kilometers": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-134>"
              },
              "type": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-135>"
              },
              "sender": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-136>"
              },
              "talker": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-137>"
              },
              "raw": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-138>"
              }
            },
            "required": [
              "type",
              "sender",
              "talker",
              "raw"
            ],
            "x-parser-schema-id": "<anonymous-schema-126>"
          },
          "x-parser-unique-object-id": "vhw_envelope"
        }
      },
      "x-parser-unique-object-id": "atpx/processed/nmea/vhw/{sender}"
    },
    "atpx/processed/nmea/vlw/{sender}": {
      "address": "atpx/processed/nmea/vlw/{sender}",
      "title": "VLW processed envelope",
      "description": "Parsed JSON envelope for NMEA 0183 VLW sentences. ``{sender}`` identifies the originating A+T device.",
      "parameters": {
        "sender": {
          "description": "A+T device identifier (e.g. 3143, 3145)",
          "location": "$message.header#/topic/parts/4"
        }
      },
      "messages": {
        "vlw_envelope": {
          "name": "vlw_envelope",
          "title": "VLW envelope",
          "description": "Parsed payload for NMEA 0183 VLW sentence type",
          "contentType": "application/json",
          "payload": {
            "type": "object",
            "properties": {
              "trip_distance": {
                "type": [
                  "number",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-141>"
              },
              "trip_distance_miles": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-142>"
              },
              "trip_distance_reset": {
                "type": [
                  "number",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-143>"
              },
              "trip_distance_reset_miles": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-144>"
              },
              "type": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-145>"
              },
              "sender": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-146>"
              },
              "talker": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-147>"
              },
              "raw": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-148>"
              }
            },
            "required": [
              "type",
              "sender",
              "talker",
              "raw"
            ],
            "x-parser-schema-id": "<anonymous-schema-140>"
          },
          "x-parser-unique-object-id": "vlw_envelope"
        }
      },
      "x-parser-unique-object-id": "atpx/processed/nmea/vlw/{sender}"
    },
    "atpx/processed/nmea/rmc/{sender}": {
      "address": "atpx/processed/nmea/rmc/{sender}",
      "title": "RMC processed envelope",
      "description": "Parsed JSON envelope for NMEA 0183 RMC sentences. ``{sender}`` identifies the originating A+T device.",
      "parameters": {
        "sender": {
          "description": "A+T device identifier (e.g. 3143, 3145)",
          "location": "$message.header#/topic/parts/4"
        }
      },
      "messages": {
        "rmc_envelope": {
          "name": "rmc_envelope",
          "title": "RMC envelope",
          "description": "Parsed payload for NMEA 0183 RMC sentence type",
          "contentType": "application/json",
          "payload": {
            "type": "object",
            "properties": {
              "nmea_time": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-151>"
              },
              "status": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-152>"
              },
              "lat": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-153>"
              },
              "lat_dir": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-154>"
              },
              "lon": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-155>"
              },
              "lon_dir": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-156>"
              },
              "spd_over_grnd": {
                "type": [
                  "number",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-157>"
              },
              "true_course": {
                "type": [
                  "number",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-158>"
              },
              "datestamp": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-159>"
              },
              "mag_variation": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-160>"
              },
              "mag_var_dir": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-161>"
              },
              "mode_indicator": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-162>"
              },
              "nav_status": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-163>"
              },
              "latitude": {
                "type": [
                  "number",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-164>"
              },
              "longitude": {
                "type": [
                  "number",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-165>"
              },
              "type": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-166>"
              },
              "sender": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-167>"
              },
              "talker": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-168>"
              },
              "raw": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-169>"
              }
            },
            "required": [
              "type",
              "sender",
              "talker",
              "raw"
            ],
            "x-parser-schema-id": "<anonymous-schema-150>"
          },
          "x-parser-unique-object-id": "rmc_envelope"
        }
      },
      "x-parser-unique-object-id": "atpx/processed/nmea/rmc/{sender}"
    },
    "atpx/processed/nmea/alr/{sender}": {
      "address": "atpx/processed/nmea/alr/{sender}",
      "title": "ALR processed envelope",
      "description": "Parsed JSON envelope for NMEA 0183 ALR sentences. ``{sender}`` identifies the originating A+T device.",
      "parameters": {
        "sender": {
          "description": "A+T device identifier (e.g. 3143, 3145)",
          "location": "$message.header#/topic/parts/4"
        }
      },
      "messages": {
        "alr_envelope": {
          "name": "alr_envelope",
          "title": "ALR envelope",
          "description": "Parsed payload for NMEA 0183 ALR sentence type",
          "contentType": "application/json",
          "payload": {
            "type": "object",
            "properties": {
              "nmea_time": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-172>"
              },
              "alarm_number": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-173>"
              },
              "alarm_condition": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-174>"
              },
              "alarm_ack_state": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-175>"
              },
              "alarm_text": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-176>"
              },
              "type": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-177>"
              },
              "sender": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-178>"
              },
              "talker": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-179>"
              },
              "raw": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-180>"
              }
            },
            "required": [
              "type",
              "sender",
              "talker",
              "raw"
            ],
            "x-parser-schema-id": "<anonymous-schema-171>"
          },
          "x-parser-unique-object-id": "alr_envelope"
        }
      },
      "x-parser-unique-object-id": "atpx/processed/nmea/alr/{sender}"
    },
    "atpx/processed/nmea/alc/{sender}": {
      "address": "atpx/processed/nmea/alc/{sender}",
      "title": "ALC processed envelope",
      "description": "Parsed JSON envelope for NMEA 0183 ALC sentences. ``{sender}`` identifies the originating A+T device.",
      "parameters": {
        "sender": {
          "description": "A+T device identifier (e.g. 3143, 3145)",
          "location": "$message.header#/topic/parts/4"
        }
      },
      "messages": {
        "alc_envelope": {
          "name": "alc_envelope",
          "title": "ALC envelope",
          "description": "Parsed payload for NMEA 0183 ALC sentence type",
          "contentType": "application/json",
          "payload": {
            "type": "object",
            "properties": {
              "total_sentences": {
                "type": [
                  "integer",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-183>"
              },
              "sentence_number": {
                "type": [
                  "integer",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-184>"
              },
              "sequence_id": {
                "type": [
                  "integer",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-185>"
              },
              "num_alerts": {
                "type": [
                  "integer",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-186>"
              },
              "type": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-187>"
              },
              "sender": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-188>"
              },
              "talker": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-189>"
              },
              "raw": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-190>"
              }
            },
            "required": [
              "type",
              "sender",
              "talker",
              "raw"
            ],
            "x-parser-schema-id": "<anonymous-schema-182>"
          },
          "x-parser-unique-object-id": "alc_envelope"
        }
      },
      "x-parser-unique-object-id": "atpx/processed/nmea/alc/{sender}"
    },
    "atpx/processed/nmea/pos/{sender}": {
      "address": "atpx/processed/nmea/pos/{sender}",
      "title": "POS processed envelope",
      "description": "Parsed JSON envelope for NMEA 0183 POS sentences. ``{sender}`` identifies the originating A+T device.",
      "parameters": {
        "sender": {
          "description": "A+T device identifier (e.g. 3143, 3145)",
          "location": "$message.header#/topic/parts/4"
        }
      },
      "messages": {
        "pos_envelope": {
          "name": "pos_envelope",
          "title": "POS envelope",
          "description": "Parsed payload for NMEA 0183 POS sentence type",
          "contentType": "application/json",
          "payload": {
            "type": "object",
            "properties": {
              "device_talker": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-193>"
              },
              "equipment_number": {
                "type": [
                  "integer",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-194>"
              },
              "status": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-195>"
              },
              "x_offset": {
                "type": [
                  "number",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-196>"
              },
              "y_offset": {
                "type": [
                  "number",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-197>"
              },
              "z_offset": {
                "type": [
                  "number",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-198>"
              },
              "position_valid": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-199>"
              },
              "length": {
                "type": [
                  "number",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-200>"
              },
              "beam": {
                "type": [
                  "number",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-201>"
              },
              "sentence_status": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-202>"
              },
              "type": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-203>"
              },
              "sender": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-204>"
              },
              "talker": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-205>"
              },
              "raw": {
                "type": [
                  "string",
                  "null"
                ],
                "x-parser-schema-id": "<anonymous-schema-206>"
              }
            },
            "required": [
              "type",
              "sender",
              "talker",
              "raw"
            ],
            "x-parser-schema-id": "<anonymous-schema-192>"
          },
          "x-parser-unique-object-id": "pos_envelope"
        }
      },
      "x-parser-unique-object-id": "atpx/processed/nmea/pos/{sender}"
    }
  },
  "operations": {
    "receive_raw_nmea": {
      "action": "receive",
      "channel": "$ref:$.channels.atpx/nmea0183/{sender}/{TYPE}",
      "x-parser-unique-object-id": "receive_raw_nmea"
    },
    "send_rot_envelope": {
      "action": "send",
      "channel": "$ref:$.channels.atpx/processed/nmea/rot/{sender}",
      "x-parser-unique-object-id": "send_rot_envelope"
    },
    "send_hdt_envelope": {
      "action": "send",
      "channel": "$ref:$.channels.atpx/processed/nmea/hdt/{sender}",
      "x-parser-unique-object-id": "send_hdt_envelope"
    },
    "send_fec_envelope": {
      "action": "send",
      "channel": "$ref:$.channels.atpx/processed/nmea/fec/{sender}",
      "x-parser-unique-object-id": "send_fec_envelope"
    },
    "send_gga_envelope": {
      "action": "send",
      "channel": "$ref:$.channels.atpx/processed/nmea/gga/{sender}",
      "x-parser-unique-object-id": "send_gga_envelope"
    },
    "send_dbt_envelope": {
      "action": "send",
      "channel": "$ref:$.channels.atpx/processed/nmea/dbt/{sender}",
      "x-parser-unique-object-id": "send_dbt_envelope"
    },
    "send_dpt_envelope": {
      "action": "send",
      "channel": "$ref:$.channels.atpx/processed/nmea/dpt/{sender}",
      "x-parser-unique-object-id": "send_dpt_envelope"
    },
    "send_gll_envelope": {
      "action": "send",
      "channel": "$ref:$.channels.atpx/processed/nmea/gll/{sender}",
      "x-parser-unique-object-id": "send_gll_envelope"
    },
    "send_vtg_envelope": {
      "action": "send",
      "channel": "$ref:$.channels.atpx/processed/nmea/vtg/{sender}",
      "x-parser-unique-object-id": "send_vtg_envelope"
    },
    "send_vbw_envelope": {
      "action": "send",
      "channel": "$ref:$.channels.atpx/processed/nmea/vbw/{sender}",
      "x-parser-unique-object-id": "send_vbw_envelope"
    },
    "send_zda_envelope": {
      "action": "send",
      "channel": "$ref:$.channels.atpx/processed/nmea/zda/{sender}",
      "x-parser-unique-object-id": "send_zda_envelope"
    },
    "send_vhw_envelope": {
      "action": "send",
      "channel": "$ref:$.channels.atpx/processed/nmea/vhw/{sender}",
      "x-parser-unique-object-id": "send_vhw_envelope"
    },
    "send_vlw_envelope": {
      "action": "send",
      "channel": "$ref:$.channels.atpx/processed/nmea/vlw/{sender}",
      "x-parser-unique-object-id": "send_vlw_envelope"
    },
    "send_rmc_envelope": {
      "action": "send",
      "channel": "$ref:$.channels.atpx/processed/nmea/rmc/{sender}",
      "x-parser-unique-object-id": "send_rmc_envelope"
    },
    "send_alr_envelope": {
      "action": "send",
      "channel": "$ref:$.channels.atpx/processed/nmea/alr/{sender}",
      "x-parser-unique-object-id": "send_alr_envelope"
    },
    "send_alc_envelope": {
      "action": "send",
      "channel": "$ref:$.channels.atpx/processed/nmea/alc/{sender}",
      "x-parser-unique-object-id": "send_alc_envelope"
    },
    "send_pos_envelope": {
      "action": "send",
      "channel": "$ref:$.channels.atpx/processed/nmea/pos/{sender}",
      "x-parser-unique-object-id": "send_pos_envelope"
    }
  },
  "components": {
    "messages": {
      "raw_nmea_sentence": "$ref:$.channels.atpx/nmea0183/{sender}/{TYPE}.messages.raw_nmea_sentence",
      "rot_envelope": "$ref:$.channels.atpx/processed/nmea/rot/{sender}.messages.rot_envelope",
      "hdt_envelope": "$ref:$.channels.atpx/processed/nmea/hdt/{sender}.messages.hdt_envelope",
      "fec_envelope": "$ref:$.channels.atpx/processed/nmea/fec/{sender}.messages.fec_envelope",
      "gga_envelope": "$ref:$.channels.atpx/processed/nmea/gga/{sender}.messages.gga_envelope",
      "dbt_envelope": "$ref:$.channels.atpx/processed/nmea/dbt/{sender}.messages.dbt_envelope",
      "dpt_envelope": "$ref:$.channels.atpx/processed/nmea/dpt/{sender}.messages.dpt_envelope",
      "gll_envelope": "$ref:$.channels.atpx/processed/nmea/gll/{sender}.messages.gll_envelope",
      "vtg_envelope": "$ref:$.channels.atpx/processed/nmea/vtg/{sender}.messages.vtg_envelope",
      "vbw_envelope": "$ref:$.channels.atpx/processed/nmea/vbw/{sender}.messages.vbw_envelope",
      "zda_envelope": "$ref:$.channels.atpx/processed/nmea/zda/{sender}.messages.zda_envelope",
      "vhw_envelope": "$ref:$.channels.atpx/processed/nmea/vhw/{sender}.messages.vhw_envelope",
      "vlw_envelope": "$ref:$.channels.atpx/processed/nmea/vlw/{sender}.messages.vlw_envelope",
      "rmc_envelope": "$ref:$.channels.atpx/processed/nmea/rmc/{sender}.messages.rmc_envelope",
      "alr_envelope": "$ref:$.channels.atpx/processed/nmea/alr/{sender}.messages.alr_envelope",
      "alc_envelope": "$ref:$.channels.atpx/processed/nmea/alc/{sender}.messages.alc_envelope",
      "pos_envelope": "$ref:$.channels.atpx/processed/nmea/pos/{sender}.messages.pos_envelope"
    }
  },
  "x-parser-spec-parsed": true,
  "x-parser-api-version": 3,
  "x-parser-spec-stringified": true
};
    const config = {"show":{"sidebar":true},"sidebar":{"showOperations":"byDefault"}};
    const appRoot = document.getElementById('root');
    AsyncApiStandalone.render(
        { schema, config, }, appRoot
    );
  