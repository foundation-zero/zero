use crate::config::{Port, Var};
use crate::layout::{Layout, Variable, VariableValue};
use crate::metrics::PortMetrics;
use log::{debug, error, warn};
use nom::{
    number::complete::{
        be_i16, be_i32, be_i64, be_i8, be_u16, be_u32, be_u64, be_u8, le_f32, le_f64,
    },
    IResult,
};
use std::sync::Arc;
use tokio_stream::{Stream, StreamExt};

/// Parse one UDP packet according to `port_config` and return a `Vec<Variable>`
/// where every key is borrowed from `layout`.
pub fn parse_packet<'input, 'layout>(
    input: &'input [u8],
    port_config: &Port,
    layout: &'layout Layout,
) -> IResult<&'input [u8], Vec<Variable<'layout>>> {
    port_config
        .variables
        .iter()
        .try_fold((input, Vec::new()), |(remaining, mut vars), var| {
            let (next, mut parsed) = parse_variable(remaining, var, layout)?;
            vars.append(&mut parsed);
            Ok((next, vars))
        })
}

/// Convert a packet byte stream into a stream of parsed variable batches.
///
/// Decode failures are logged and counted here rather than by the caller, since
/// this is the last point that still holds the raw bytes for diagnostics.
pub fn parse_packet_stream<'layout, S>(
    packets: S,
    port_config: &'layout Port,
    layout: &'layout Layout,
    metrics: Arc<PortMetrics>,
) -> impl Stream<Item = Result<Vec<Variable<'layout>>, String>> + 'layout
where
    S: Stream<Item = Vec<u8>> + 'layout,
{
    let expected_len = expected_packet_len(port_config);
    packets.map(move |packet| {
        if packet.len() != expected_len {
            metrics.incr_length_mismatches();
            warn!(
                "port {}: packet length {} does not match expected length {} \
                 (wrong config file for this feed?)",
                port_config.numport,
                packet.len(),
                expected_len
            );
        }

        match parse_packet(&packet, port_config, layout) {
            Ok((_, vars)) => {
                debug!(
                    "port {}: parsed {} variables from {} bytes",
                    port_config.numport,
                    vars.len(),
                    packet.len()
                );
                Ok(vars)
            }
            Err(e) => {
                metrics.incr_parse_errors();
                error!(
                    "port {}: failed to parse {} bytes [{}]: {}",
                    port_config.numport,
                    packet.len(),
                    hex_preview(&packet),
                    e
                );
                Err(e.to_string())
            }
        }
    })
}

/// Render the leading bytes of a packet as hex, so a bad frame can be inspected
/// from the logs without a packet capture.
fn hex_preview(bytes: &[u8]) -> String {
    const PREVIEW_LEN: usize = 16;
    bytes
        .iter()
        .take(PREVIEW_LEN)
        .map(|byte| format!("{:02x}", byte))
        .collect::<Vec<_>>()
        .join(" ")
}

/// Total packet length implied by the configured variables.
pub(crate) fn expected_packet_len(port_config: &Port) -> usize {
    port_config
        .variables
        .iter()
        .map(expected_var_len)
        .sum::<usize>()
}

fn expected_var_len(var: &Var) -> usize {
    match var.var_type.as_str() {
        "CounterU32" | "UnSignedInt32" | "SignedInt32" | "Float" | "32BitBoolRegister" => 4,
        "UnSignedInt16" | "SignedInt16" | "16BitBoolRegister" => 2,
        "UnSignedInt8" | "SignedInt8" | "8BitBoolRegister" => 1,
        "UnSignedInt64" | "SignedInt64" | "Double" => 8,
        _ => 0,
    }
}

fn parse_variable<'input, 'layout>(
    input: &'input [u8],
    var: &Var,
    layout: &'layout Layout,
) -> IResult<&'input [u8], Vec<Variable<'layout>>> {
    match var.var_type.as_str() {
        "CounterU32" => {
            let (i, v) = be_u32(input)?;
            Ok((
                i,
                vec![Variable {
                    key: layout.key(&var.name),
                    value: VariableValue::Number(v as f64),
                }],
            ))
        }
        "SignedInt8" => {
            let (i, v) = be_i8(input)?;
            Ok((
                i,
                vec![Variable {
                    key: layout.key(&var.name),
                    value: VariableValue::Number(apply_scaling(v as f64, var)),
                }],
            ))
        }
        "SignedInt16" => {
            let (i, v) = be_i16(input)?;
            Ok((
                i,
                vec![Variable {
                    key: layout.key(&var.name),
                    value: VariableValue::Number(apply_scaling(v as f64, var)),
                }],
            ))
        }
        "SignedInt32" => {
            let (i, v) = be_i32(input)?;
            Ok((
                i,
                vec![Variable {
                    key: layout.key(&var.name),
                    value: VariableValue::Number(apply_scaling(v as f64, var)),
                }],
            ))
        }
        "SignedInt64" => {
            let (i, v) = be_i64(input)?;
            Ok((
                i,
                vec![Variable {
                    key: layout.key(&var.name),
                    value: VariableValue::Number(apply_scaling(v as f64, var)),
                }],
            ))
        }
        "UnSignedInt8" => {
            let (i, v) = be_u8(input)?;
            Ok((
                i,
                vec![Variable {
                    key: layout.key(&var.name),
                    value: VariableValue::Number(apply_scaling(v as f64, var)),
                }],
            ))
        }
        "UnSignedInt16" => {
            let (i, v) = be_u16(input)?;
            Ok((
                i,
                vec![Variable {
                    key: layout.key(&var.name),
                    value: VariableValue::Number(apply_scaling(v as f64, var)),
                }],
            ))
        }
        "UnSignedInt32" => {
            let (i, v) = be_u32(input)?;
            Ok((
                i,
                vec![Variable {
                    key: layout.key(&var.name),
                    value: VariableValue::Number(apply_scaling(v as f64, var)),
                }],
            ))
        }
        "UnSignedInt64" => {
            let (i, v) = be_u64(input)?;
            Ok((
                i,
                vec![Variable {
                    key: layout.key(&var.name),
                    value: VariableValue::Number(apply_scaling(v as f64, var)),
                }],
            ))
        }
        "Float" => {
            let (i, v) = le_f32(input)?;
            Ok((
                i,
                vec![Variable {
                    key: layout.key(&var.name),
                    value: VariableValue::Number(apply_scaling(v as f64, var)),
                }],
            ))
        }
        "Double" => {
            let (i, v) = le_f64(input)?;
            Ok((
                i,
                vec![Variable {
                    key: layout.key(&var.name),
                    value: VariableValue::Number(apply_scaling(v, var)),
                }],
            ))
        }
        "8BitBoolRegister" => {
            let (i, v) = be_u8(input)?;
            Ok((i, expand_bit_register(v as u64, 8, var, layout)))
        }
        "16BitBoolRegister" => {
            let (i, v) = be_u16(input)?;
            Ok((i, expand_bit_register(v as u64, 16, var, layout)))
        }
        "32BitBoolRegister" => {
            let (i, v) = be_u32(input)?;
            Ok((i, expand_bit_register(v as u64, 32, var, layout)))
        }
        _ => Err(nom::Err::Error(nom::error::Error::new(
            input,
            nom::error::ErrorKind::Tag,
        ))),
    }
}

/// Emit the raw register value followed by one entry per declared bit (0.0 or 1.0).
fn expand_bit_register<'layout>(
    val: u64,
    width: u8,
    var: &Var,
    layout: &'layout Layout,
) -> Vec<Variable<'layout>> {
    let mut results = vec![Variable {
        key: layout.key(&var.name),
        value: VariableValue::Number(val as f64),
    }];
    for bit_def in &var.bits {
        if bit_def.num < width {
            let bit_val = (val >> bit_def.num) & 1 == 1;
            results.push(Variable {
                key: layout.key(&bit_def.name),
                value: VariableValue::Boolean(bit_val),
            });
        }
    }
    results
}

fn apply_scaling(val: f64, var: &Var) -> f64 {
    let factor = var.factor.unwrap_or(1.0);
    let offset = var.offset.unwrap_or(0.0);
    (val / factor) + offset
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::config::{Bit, Port, Var};
    use crate::layout::Layout;

    fn make_var(name: &str, var_type: &str, factor: Option<f64>, bits: Vec<Bit>) -> Var {
        Var {
            num: None,
            var_type: var_type.to_string(),
            units: None,
            factor,
            offset: None,
            decimals: None,
            class: None,
            tags: None,
            description: None,
            name: name.to_string(),
            bits,
        }
    }

    fn find_number(vars: &[Variable<'_>], name: &str) -> f64 {
        let value = &vars
            .iter()
            .find(|v| v.key == name)
            .unwrap_or_else(|| panic!("variable '{}' not found", name))
            .value;
        match value {
            VariableValue::Number(v) => *v,
            VariableValue::Boolean(_) => panic!("variable '{}' is not numeric", name),
        }
    }

    fn find_bool(vars: &[Variable<'_>], name: &str) -> bool {
        let value = &vars
            .iter()
            .find(|v| v.key == name)
            .unwrap_or_else(|| panic!("variable '{}' not found", name))
            .value;
        match value {
            VariableValue::Boolean(v) => *v,
            VariableValue::Number(_) => panic!("variable '{}' is not boolean", name),
        }
    }

    #[test]
    fn test_parse_simple() {
        let port = Port {
            numport: 50000,
            channel: "Test".to_string(),
            frequency: None,
            mode: None,
            variables: vec![
                make_var("Foo", "UnSignedInt8", None, vec![]),
                make_var("Bar", "SignedInt16", Some(10.0), vec![]),
            ],
        };
        let layout = Layout::from_port(&port);

        // Foo = 10, Bar raw = 100 => 100 / 10 = 10.0
        let data: &[u8] = &[0x0A, 0x00, 0x64];
        let (_, values) = parse_packet(data, &port, &layout).unwrap();

        assert_eq!(find_number(&values, "Foo"), 10.0);
        assert!((find_number(&values, "Bar") - 10.0).abs() < 1e-6);
    }

    #[test]
    fn test_parse_every_integer_type_big_endian() {
        let mut offset = make_var("Offset", "SignedInt64", None, vec![]);
        offset.offset = Some(-1.0);
        let port = Port {
            numport: 50000,
            channel: "Test".to_string(),
            frequency: None,
            mode: None,
            variables: vec![
                make_var("Counter", "CounterU32", Some(10.0), vec![]),
                make_var("Tilt", "SignedInt8", None, vec![]),
                make_var("Torque", "SignedInt32", Some(10.0), vec![]),
                offset,
                make_var("Speed", "UnSignedInt16", Some(100.0), vec![]),
                make_var("Hours", "UnSignedInt32", None, vec![]),
                make_var("Energy", "UnSignedInt64", Some(1000.0), vec![]),
            ],
        };
        let layout = Layout::from_port(&port);

        let data: &[u8] = &[
            0x00, 0x01, 0x00, 0x00, // Counter 65536, never scaled
            0xFE, // Tilt -2
            0xFF, 0xFE, 0x79, 0x60, // Torque -100000 / 10
            0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, // Offset 2^32, then -1
            0x30, 0x39, // Speed 12345 / 100
            0xDE, 0xAD, 0xBE, 0xEF, // Hours 3735928559
            0x00, 0x00, 0x00, 0x00, 0x00, 0x0F, 0x42, 0x40, // Energy 1000000 / 1000
        ];
        assert_eq!(expected_packet_len(&port), data.len());

        let (rest, values) = parse_packet(data, &port, &layout).unwrap();
        assert!(rest.is_empty());
        assert_eq!(find_number(&values, "Counter"), 65536.0);
        assert_eq!(find_number(&values, "Tilt"), -2.0);
        assert_eq!(find_number(&values, "Torque"), -10000.0);
        assert_eq!(find_number(&values, "Offset"), 4_294_967_295.0);
        assert!((find_number(&values, "Speed") - 123.45).abs() < 1e-9);
        assert_eq!(find_number(&values, "Hours"), 3_735_928_559.0);
        assert_eq!(find_number(&values, "Energy"), 1000.0);
    }

    #[test]
    fn test_parse_wide_bool_registers() {
        let bit = |num: u8, name: &str| Bit {
            num,
            name: name.to_string(),
        };
        let port = Port {
            numport: 50000,
            channel: "Test".to_string(),
            frequency: None,
            mode: None,
            variables: vec![
                make_var(
                    "Alarms",
                    "16BitBoolRegister",
                    None,
                    vec![bit(0, "AlarmLow"), bit(15, "AlarmHigh")],
                ),
                make_var(
                    "Status",
                    "32BitBoolRegister",
                    None,
                    vec![bit(1, "StatusLow"), bit(31, "StatusHigh")],
                ),
            ],
        };
        let layout = Layout::from_port(&port);

        let data: &[u8] = &[0x80, 0x00, 0x80, 0x00, 0x00, 0x02];
        assert_eq!(expected_packet_len(&port), data.len());

        let (_, values) = parse_packet(data, &port, &layout).unwrap();
        assert_eq!(find_number(&values, "Alarms"), 32768.0);
        assert!(!find_bool(&values, "AlarmLow"));
        assert!(find_bool(&values, "AlarmHigh"));
        assert_eq!(find_number(&values, "Status"), 2_147_483_650.0);
        assert!(find_bool(&values, "StatusLow"));
        assert!(find_bool(&values, "StatusHigh"));
    }

    #[test]
    fn test_truncated_packet_is_a_parse_error() {
        let port = Port {
            numport: 50000,
            channel: "Test".to_string(),
            frequency: None,
            mode: None,
            variables: vec![make_var("Hours", "UnSignedInt32", None, vec![])],
        };
        let layout = Layout::from_port(&port);

        assert!(parse_packet(&[0x00, 0x01, 0x02], &port, &layout).is_err());
    }

    #[test]
    fn test_parse_bool_register() {
        let port = Port {
            numport: 50000,
            channel: "Test".to_string(),
            frequency: None,
            mode: None,
            variables: vec![make_var(
                "Flag",
                "8BitBoolRegister",
                None,
                vec![
                    Bit {
                        num: 0,
                        name: "BitZero".to_string(),
                    },
                    Bit {
                        num: 2,
                        name: "BitTwo".to_string(),
                    },
                ],
            )],
        };
        let layout = Layout::from_port(&port);

        // 0x05 = 0b00000101 => bit 0 and bit 2 set
        let data: &[u8] = &[0x05];
        let (_, values) = parse_packet(data, &port, &layout).unwrap();

        assert_eq!(find_number(&values, "Flag"), 5.0);
        assert!(find_bool(&values, "BitZero"));
        assert!(find_bool(&values, "BitTwo"));
    }

    #[test]
    fn test_parse_with_factor_and_offset() {
        let mut var = make_var("Scaled", "SignedInt16", Some(2.0), vec![]);
        var.offset = Some(1.5);

        let port = Port {
            numport: 50000,
            channel: "Test".to_string(),
            frequency: None,
            mode: None,
            variables: vec![var],
        };
        let layout = Layout::from_port(&port);

        // raw 10 => (10 / 2.0) + 1.5 = 6.5
        let data: &[u8] = &[0x00, 0x0A];
        let (_, values) = parse_packet(data, &port, &layout).unwrap();
        assert!((find_number(&values, "Scaled") - 6.5).abs() < 1e-6);
    }

    #[test]
    fn test_parse_unknown_type_returns_error() {
        let port = Port {
            numport: 50000,
            channel: "Test".to_string(),
            frequency: None,
            mode: None,
            variables: vec![make_var("Unknown", "NotARealType", None, vec![])],
        };
        let layout = Layout::from_port(&port);

        let data: &[u8] = &[0x00];
        assert!(parse_packet(data, &port, &layout).is_err());
    }

    #[test]
    fn test_bit_index_out_of_width_is_ignored() {
        let port = Port {
            numport: 50000,
            channel: "Test".to_string(),
            frequency: None,
            mode: None,
            variables: vec![make_var(
                "Flag",
                "8BitBoolRegister",
                None,
                vec![
                    Bit {
                        num: 7,
                        name: "BitSeven".to_string(),
                    },
                    Bit {
                        num: 8,
                        name: "BitEightOutOfRange".to_string(),
                    },
                ],
            )],
        };
        let layout = Layout::from_port(&port);

        let data: &[u8] = &[0x80];
        let (_, values) = parse_packet(data, &port, &layout).unwrap();

        assert_eq!(find_number(&values, "Flag"), 128.0);
        assert!(find_bool(&values, "BitSeven"));
        assert!(values.iter().all(|v| v.key != "BitEightOutOfRange"));
    }

    #[test]
    fn test_parse_float_little_endian() {
        let port = Port {
            numport: 50000,
            channel: "Test".to_string(),
            frequency: None,
            mode: None,
            variables: vec![make_var("Value", "Float", None, vec![])],
        };
        let layout = Layout::from_port(&port);

        // 8C 2B 38 43 is 184.170105 in little-endian float32.
        let data: &[u8] = &[0x8C, 0x2B, 0x38, 0x43];
        let (_, values) = parse_packet(data, &port, &layout).unwrap();
        assert!((find_number(&values, "Value") - 184.170_105).abs() < 1e-5);
    }

    #[test]
    fn test_parse_float_zero_word_is_zero() {
        let port = Port {
            numport: 50000,
            channel: "Test".to_string(),
            frequency: None,
            mode: None,
            variables: vec![make_var("Zero", "Float", None, vec![])],
        };
        let layout = Layout::from_port(&port);

        let data: &[u8] = &[0x00, 0x00, 0x00, 0x00];
        let (_, values) = parse_packet(data, &port, &layout).unwrap();
        assert_eq!(find_number(&values, "Zero"), 0.0);
    }

    #[test]
    fn test_parse_double_little_endian() {
        let port = Port {
            numport: 50000,
            channel: "Test".to_string(),
            frequency: None,
            mode: None,
            variables: vec![make_var("Value", "Double", None, vec![])],
        };
        let layout = Layout::from_port(&port);

        // 77 BE 9F 1A 2F DD 5E 40 is 123.456 in little-endian float64.
        let data: &[u8] = &[0x77, 0xBE, 0x9F, 0x1A, 0x2F, 0xDD, 0x5E, 0x40];
        let (_, values) = parse_packet(data, &port, &layout).unwrap();
        assert!((find_number(&values, "Value") - 123.456).abs() < 1e-10);
    }

    #[tokio::test]
    async fn test_stream_counts_length_mismatches_and_parse_errors() {
        use tokio_stream::StreamExt;

        let port = Port {
            numport: 50000,
            channel: "Test".to_string(),
            frequency: None,
            mode: None,
            variables: vec![make_var("Foo", "UnSignedInt8", None, vec![])],
        };
        let layout = Layout::from_port(&port);
        let metrics = PortMetrics::new();

        let packets = vec![
            vec![0x0A],       // exact length, parses
            vec![0x0A, 0x0B], // too long: warns, but still parses
            Vec::new(),       // too short: mismatched length and unparseable
        ];

        let results: Vec<_> =
            parse_packet_stream(tokio_stream::iter(packets), &port, &layout, metrics.clone())
                .collect()
                .await;

        assert_eq!(results.len(), 3);
        assert!(results[0].is_ok());
        assert!(results[1].is_ok());
        assert!(results[2].is_err());

        let snapshot = metrics.snapshot();
        assert_eq!(snapshot.length_mismatches, 2);
        assert_eq!(snapshot.parse_errors, 1);
    }

    #[test]
    fn test_hex_preview_truncates_to_sixteen_bytes() {
        let bytes: Vec<u8> = (0..32).collect();
        assert_eq!(
            hex_preview(&bytes),
            "00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f"
        );
        assert_eq!(hex_preview(&[]), "");
    }
}
