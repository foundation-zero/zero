"""Devices outside the managed systems that the Spec carries by hand.

The propulsion drives, uGrid converters and shore power converters publish outside the managed
systems, and the converters' values come from the PMS node configuration, which the IO list
doesn't have. Each is named as the topic-structure proposal names it (system, kind, instance), at
the address it publishes on: the MQTT GraphQL API follows the address. The uGrid and shore power
converters publish on the convention's topics; the drives keep today's until the 150000 pass. The
fields are the ones thrs-control reads.
"""

# TODO: drop this table once the IO list carries these devices, after the topic cut-over.

from .managed_topics import ComponentType, ManagedTopic
from .types import IOTopic, IOValue

FIELDS: dict[ComponentType, dict[str, str]] = {
    ComponentType.DRIVE: {
        "VpEnable": "BOOLEAN",
        # The IO list says INTEGER, but Power arrives as a decimal (`0.0`); REAL takes both.
        "TempPowerStage": "REAL",
        "Power": "REAL",
    },
    ComponentType.CONVERTER: {
        "Running": "BOOLEAN",
        "TempPowerStage": "REAL",
        "PvPower": "REAL",
    },
    ComponentType.SHORE_CONVERTER: {
        "Online": "BOOLEAN",
        "EsiTransformerTemperature": "REAL",
        "EsiIgbtMinTemperature": "REAL",
        "EsiIgbtMaxTemperature": "REAL",
        "EsiAcBusActivePower3Phase": "REAL",
    },
}


def extra_topic(
    *, address: str, system: str, kind: ComponentType, instance: str, yard_tag: str
) -> ManagedTopic:
    fields = [
        IOValue(name, data_type, yard_tag) for name, data_type in FIELDS[kind].items()
    ]
    return ManagedTopic(
        system_name=system,
        module_name=kind.replace("_", "-"),
        technical_name=instance,
        component=kind,
        topic=IOTopic(address, fields),
    )


# The yard tags are the ones thrs-control gives these devices.
EXTRA_TOPICS = [
    # The proposal's next pass has no designations for the drives yet.
    extra_topic(
        address="marpower/150000-propulsion/pcs-aft-ara1",
        system="propulsion",
        kind=ComponentType.DRIVE,
        instance="pcs-aft-ara1",
        yard_tag="45002079",
    ),
    extra_topic(
        address="marpower/150000-propulsion/pcs-aft-ara2",
        system="propulsion",
        kind=ComponentType.DRIVE,
        instance="pcs-aft-ara2",
        yard_tag="45002079",
    ),
    extra_topic(
        address="marpower/150000-propulsion/pcs-fwd-ara1",
        system="propulsion",
        kind=ComponentType.DRIVE,
        instance="pcs-fwd-ara1",
        yard_tag="45002080",
    ),
    extra_topic(
        address="marpower/150000-propulsion/pcs-fwd-ara2",
        system="propulsion",
        kind=ComponentType.DRIVE,
        instance="pcs-fwd-ara2",
        yard_tag="45002080",
    ),
    extra_topic(
        address="marpower/45-dc-ac/inverter/05-11-u101",
        system="dc_ac",
        kind=ComponentType.CONVERTER,
        instance="05-11-u101",
        yard_tag="45002082",
    ),
    extra_topic(
        address="marpower/45-dc-ac/inverter/05-12-u101",
        system="dc_ac",
        kind=ComponentType.CONVERTER,
        instance="05-12-u101",
        yard_tag="45002081",
    ),
    extra_topic(
        address="marpower/45-dc-700v/shore-converter/07-11-tbc1a",
        system="dc_700v",
        kind=ComponentType.SHORE_CONVERTER,
        instance="07-11-tbc1a",
        yard_tag="45002001",
    ),
    extra_topic(
        address="marpower/45-dc-700v/shore-converter/07-11-tbc1b",
        system="dc_700v",
        kind=ComponentType.SHORE_CONVERTER,
        instance="07-11-tbc1b",
        yard_tag="45002001",
    ),
    extra_topic(
        address="marpower/45-dc-700v/shore-converter/07-12-tbc1a",
        system="dc_700v",
        kind=ComponentType.SHORE_CONVERTER,
        instance="07-12-tbc1a",
        yard_tag="45002001",
    ),
    extra_topic(
        address="marpower/45-dc-700v/shore-converter/07-12-tbc1b",
        system="dc_700v",
        kind=ComponentType.SHORE_CONVERTER,
        instance="07-12-tbc1b",
        yard_tag="45002001",
    ),
]
