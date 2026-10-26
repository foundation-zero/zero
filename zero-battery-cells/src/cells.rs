use serde::Serialize;

/// Strings a pack is split into.
pub const STRINGS_PER_PACK: usize = 3;
/// Modules inside one string.
pub const MODULES_PER_STRING: usize = 16;
/// Cell voltage probes in one module.
pub const VOLTAGES_PER_MODULE: usize = 14;
/// Temperature probes in one module.
pub const TEMPERATURES_PER_MODULE: usize = 8;
/// Cell voltages in one string.
pub const VOLTAGES_PER_STRING: usize = MODULES_PER_STRING * VOLTAGES_PER_MODULE;
/// Temperature probes in one string.
pub const TEMPERATURES_PER_STRING: usize = MODULES_PER_STRING * TEMPERATURES_PER_MODULE;
/// Cell voltages in a full pack.
pub const VOLTAGES_PER_PACK: usize = STRINGS_PER_PACK * VOLTAGES_PER_STRING;
/// Temperature probes in a full pack.
pub const TEMPERATURES_PER_PACK: usize = STRINGS_PER_PACK * TEMPERATURES_PER_STRING;
/// Cell values in a full pack: voltages first, then temperatures.
pub const VALUES_PER_PACK: usize = VOLTAGES_PER_PACK + TEMPERATURES_PER_PACK;
/// Bytes one `INT` occupies in a NetVar list payload.
const INT_BYTES: usize = std::mem::size_of::<i16>();
/// Bytes a full pack occupies in a NetVar list payload.
pub const PAYLOAD_BYTES: usize = VALUES_PER_PACK * INT_BYTES;

/// The PLC sends cell voltages as whole millivolts; this converts them to volts.
pub const MILLIVOLTS_PER_VOLT: f32 = 1000.0;

/// One decoded battery module: the values published on one MQTT topic.
///
/// Fixed-size and heap-free, so frames can be queued towards the publisher
/// without allocating; serialisation happens only at the MQTT boundary.
#[derive(Debug, Clone, Copy, PartialEq, Serialize)]
pub struct ModuleFrame<'a> {
    /// Pack name, e.g. `41-1`, matching the MQTT topic segment.
    pub pack: &'a str,
    /// String inside the pack, 1-based.
    pub string: u8,
    /// Module inside the string, 1-based.
    pub module: u8,
    /// Cell voltages in **volts**, converted from the PLC's millivolts.
    #[serde(rename = "voltages")]
    pub voltages_v: [f32; VOLTAGES_PER_MODULE],
    /// Probe temperatures in **degrees Celsius**, as sent (whole °C).
    #[serde(rename = "temperatures")]
    pub temperatures_c: [i16; TEMPERATURES_PER_MODULE],
}

impl ModuleFrame<'_> {
    /// MQTT topic of this module: `{prefix}/{pack}/{string}/{module}`.
    pub fn topic(&self, prefix: &str) -> String {
        format!("{}/{}/{}/{}", prefix, self.pack, self.string, self.module)
    }
}

/// Why a payload region could not be decoded.
#[derive(Debug, PartialEq, Eq)]
pub enum DecodeError {
    /// The payload byte count does not match the declared value count.
    PayloadLength { expected: usize, actual: usize },
}

impl std::fmt::Display for DecodeError {
    fn fmt(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            DecodeError::PayloadLength { expected, actual } => {
                write!(
                    formatter,
                    "expected {} payload bytes, received {}",
                    expected, actual
                )
            }
        }
    }
}

impl std::error::Error for DecodeError {}

/// Split a pack payload into its module frames, lazily.
///
/// The payload holds `declared_voltages` cell voltages followed by
/// `declared_temperatures` temperatures, each an `INT`. A pack may declare fewer
/// values than a fully wired one; the undeclared tail of each section reads as
/// zero up to [`VOLTAGES_PER_PACK`] / [`TEMPERATURES_PER_PACK`] so every module
/// still maps to a frame. Voltages are converted from millivolts to volts;
/// temperatures are published as the whole degrees Celsius the PLC sends.
///
/// Only the length is checked up front; values are read straight out of
/// `payload` as each frame is produced, so decoding allocates nothing.
pub fn decode_pack<'p, 'b>(
    pack: &'p str,
    payload: &'b [u8],
    declared_voltages: usize,
    declared_temperatures: usize,
) -> Result<impl Iterator<Item = ModuleFrame<'p>> + use<'p, 'b>, DecodeError> {
    let expected_bytes = (declared_voltages + declared_temperatures) * INT_BYTES;
    if payload.len() != expected_bytes {
        return Err(DecodeError::PayloadLength {
            expected: expected_bytes,
            actual: payload.len(),
        });
    }

    let (voltages, temperatures) = payload.split_at(declared_voltages * INT_BYTES);
    Ok((0..STRINGS_PER_PACK).flat_map(move |string| {
        (0..MODULES_PER_STRING).map(move |module| {
            let voltage_start = string * VOLTAGES_PER_STRING + module * VOLTAGES_PER_MODULE;
            let temperature_start =
                string * TEMPERATURES_PER_STRING + module * TEMPERATURES_PER_MODULE;
            ModuleFrame {
                pack,
                string: string as u8 + 1,
                module: module as u8 + 1,
                voltages_v: std::array::from_fn(|cell| {
                    int_at(voltages, voltage_start + cell) as f32 / MILLIVOLTS_PER_VOLT
                }),
                temperatures_c: std::array::from_fn(|probe| {
                    int_at(temperatures, temperature_start + probe)
                }),
            }
        })
    }))
}

/// The `index`-th little-endian `INT` of a payload section; zero past its end.
fn int_at(section: &[u8], index: usize) -> i16 {
    let offset = index * INT_BYTES;
    match section.get(offset..offset + INT_BYTES) {
        Some(&[low, high]) => i16::from_le_bytes([low, high]),
        _ => 0,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// Build a payload of `count` values where each value is its flat index.
    fn payload_of(count: usize) -> Vec<u8> {
        (0..count)
            .flat_map(|index| (index as i16).to_le_bytes())
            .collect()
    }

    fn full_payload() -> Vec<u8> {
        payload_of(VALUES_PER_PACK)
    }

    fn decode_all<'p>(
        pack: &'p str,
        payload: &[u8],
        declared_voltages: usize,
        declared_temperatures: usize,
    ) -> Result<Vec<ModuleFrame<'p>>, DecodeError> {
        decode_pack(pack, payload, declared_voltages, declared_temperatures).map(Iterator::collect)
    }

    #[test]
    fn decode_pack_produces_all_module_frames() {
        let payload = full_payload();
        assert_eq!(payload.len(), PAYLOAD_BYTES);

        let frames = decode_all("41-1", &payload, VOLTAGES_PER_PACK, TEMPERATURES_PER_PACK)
            .expect("full payload should decode");
        assert_eq!(frames.len(), STRINGS_PER_PACK * MODULES_PER_STRING);

        let first = &frames[0];
        assert_eq!(first.pack, "41-1");
        assert_eq!(first.string, 1);
        assert_eq!(first.module, 1);
        assert_eq!(first.voltages_v[0], 0.0);
        assert_eq!(first.voltages_v[13], 0.013);
        // Temperatures start after all voltages, and are whole degrees.
        assert_eq!(first.temperatures_c[0], VOLTAGES_PER_PACK as i16);

        let last = frames.last().unwrap();
        assert_eq!(last.string, STRINGS_PER_PACK as u8);
        assert_eq!(last.module, MODULES_PER_STRING as u8);
        assert_eq!(
            last.temperatures_c[TEMPERATURES_PER_MODULE - 1],
            (VALUES_PER_PACK - 1) as i16
        );
    }

    #[test]
    fn decode_pack_maps_string_module_and_cell_indices() {
        let payload = full_payload();
        let frames =
            decode_all("41-1", &payload, VOLTAGES_PER_PACK, TEMPERATURES_PER_PACK).unwrap();

        // string 2, module 7 is the 22nd module overall.
        let module = frames
            .iter()
            .find(|frame| frame.string == 2 && frame.module == 7)
            .expect("module should exist");
        let voltage_start = VOLTAGES_PER_STRING + 6 * VOLTAGES_PER_MODULE;
        assert_eq!(
            module.voltages_v[0],
            voltage_start as f32 / MILLIVOLTS_PER_VOLT
        );
        let temperature_start = TEMPERATURES_PER_STRING + 6 * TEMPERATURES_PER_MODULE;
        assert_eq!(
            module.temperatures_c[0],
            (VOLTAGES_PER_PACK + temperature_start) as i16
        );
    }

    #[test]
    fn short_pack_is_zero_padded() {
        // The bench capture carried 224 voltages + 228 temperatures per cycle.
        let payload = payload_of(224 + 228);
        let frames = decode_all("41-1", &payload, 224, 228).expect("short pack should decode");
        assert_eq!(frames.len(), STRINGS_PER_PACK * MODULES_PER_STRING);

        // Declared voltages fill string 1; string 2 and 3 are zeroed.
        assert_eq!(frames[0].voltages_v[0], 0.0);
        assert_eq!(frames[15].voltages_v[13], 0.223);
        assert!(frames[16].voltages_v.iter().all(|value| *value == 0.0));

        // Declared temperatures fill the first 228 slots (28.5 modules of string 1).
        assert_eq!(frames[0].temperatures_c[0], 224);
        let beyond = frames
            .iter()
            .flat_map(|frame| frame.temperatures_c.iter())
            .filter(|value| **value != 0)
            .count();
        assert_eq!(beyond, 228);
    }

    #[test]
    fn voltages_convert_millivolts_to_volts() {
        let mut payload = vec![0u8; 2 * 2];
        payload[0..2].copy_from_slice(&3300i16.to_le_bytes());
        payload[2..4].copy_from_slice(&25i16.to_le_bytes());
        let frame = decode_pack("41-1", &payload, 1, 1).unwrap().next().unwrap();
        assert_eq!(frame.voltages_v[0], 3.3);
        assert_eq!(frame.temperatures_c[0], 25);
    }

    #[test]
    fn decode_pack_rejects_wrong_payload_length() {
        let payload = payload_of(10);
        assert_eq!(
            decode_all("41-1", &payload, 224, 228),
            Err(DecodeError::PayloadLength {
                expected: (224 + 228) * 2,
                actual: 20
            })
        );
    }

    #[test]
    fn module_frame_json_keeps_the_agreed_keys() {
        let frame = decode_pack(
            "41-1",
            &full_payload(),
            VOLTAGES_PER_PACK,
            TEMPERATURES_PER_PACK,
        )
        .unwrap()
        .next()
        .unwrap();
        let json = serde_json::to_value(frame).unwrap();
        assert_eq!(
            json["voltages"].as_array().unwrap().len(),
            VOLTAGES_PER_MODULE
        );
        assert_eq!(
            json["temperatures"].as_array().unwrap().len(),
            TEMPERATURES_PER_MODULE
        );
        assert_eq!(json["pack"], "41-1");
        assert_eq!(json["string"], 1);
        assert_eq!(json["module"], 1);
    }

    #[test]
    fn topics_follow_the_prefix() {
        let frame = decode_pack(
            "41-1",
            &full_payload(),
            VOLTAGES_PER_PACK,
            TEMPERATURES_PER_PACK,
        )
        .unwrap()
        .nth(20)
        .unwrap();
        assert_eq!(frame.topic("battery"), "battery/41-1/2/5");
        assert!(serde_json::to_string(&frame)
            .unwrap()
            .starts_with("{\"pack\":\"41-1\""));
    }
}
