from domestic_control.services.modbus import AddressRange

ROOM_INDICES = {
    "owners-cabin": 0,
    "dutch-cabin": 1,
    "french-cabin": 2,
    "italian-cabin": 3,
    "californian-lounge": 4,
    "polynesian-cabin": 5,
    "galley": 6,
    "crew-mess": 7,
    "mission-room": 8,
    "laundry": 9,
    "engineers-office": 10,
    "captains-cabin": 11,
    "crew-sb-aft-cabin": 12,
    "crew-sb-mid-cabin": 13,
    "crew-sb-fwd-cabin": 14,
    "crew-ps-mid-cabin": 15,
    "crew-ps-fwd-cabin": 16,
    "owners-deckhouse": 17,
    # "owners-cockpit": 18,
    "main-deckhouse": 19,
    # "main-cockpit": 20,
    "owners-stairway": 21,
    "guest-corridor": 22,
    "polynesian-corridor": 23,
}

# TODO: correct these to the actual addresses when we receive those
ACTUAL_TEMPERATURE_START_ADDRESS = AddressRange(100, 0.1)
TEMPERATURE_SETPOINT_START_ADDRESS = AddressRange(200, 0.1)
ACTUAL_HUMIDITY_START_ADDRESS = AddressRange(300, 0.1)
HUMIDITY_SETPOINT_START_ADDRESS = AddressRange(400, 0.1)
