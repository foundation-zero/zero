use nom::bytes::complete::take;
use nom::combinator::map;
use nom::number::complete::{le_u16, le_u32};
use nom::sequence::tuple;
use nom::IResult;

/// Byte length of the fixed NetVar UDP header.
pub const HEADER_LEN: usize = 20;

/// Byte length of the constant that opens every NetVar datagram.
const PREAMBLE_LEN: usize = 8;

/// Bytes datagrams start with, as sent by the CODESYS PLC (`00 2D 53 33`, i.e. `\0-S3`).
///
/// Confirmed against the bench capture, whose full preamble is
/// `00 2D 53 33 00 00 00 00`. Only this prefix is required: the remaining
/// preamble bytes may differ between protocol revisions.
pub const KNOWN_PREAMBLE_PREFIX: &[u8] = b"\0-S3";

/// Fixed header of a CODESYS UDP NetVar datagram.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct NetvarHeader {
    /// `ListIdentifier` of the sending list; identifies the stream within the PLC.
    pub list_id: u16,
    /// Index of the datagram within the list; zero in packed mode.
    pub packet_index: u16,
    /// Number of variables carried in this datagram.
    pub variables: u16,
    /// Total datagram length, header included, as declared by the sender.
    pub total_len: u16,
    /// Sender-provided counter, incrementing with every transmission cycle.
    pub cycle: u32,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum NetvarError {
    /// The datagram is shorter than the fixed header.
    TooShort { actual: usize },
    /// The declared length does not match the received byte count.
    LengthMismatch { declared: u16, actual: usize },
    /// nom could not read the fixed header offsets.
    Nom(String),
}

impl std::fmt::Display for NetvarError {
    fn fmt(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            NetvarError::TooShort { actual } => {
                write!(
                    formatter,
                    "expected at least {} header bytes, received {}",
                    HEADER_LEN, actual
                )
            }
            NetvarError::LengthMismatch { declared, actual } => {
                write!(
                    formatter,
                    "declared length {} does not match received {} bytes",
                    declared, actual
                )
            }
            NetvarError::Nom(message) => write!(formatter, "header parse error: {}", message),
        }
    }
}

impl std::error::Error for NetvarError {}

/// Result of splitting a datagram into the fixed header and the variable bytes.
#[derive(Debug, PartialEq, Eq)]
pub struct ParsedDatagram<'a> {
    /// Raw preamble bytes, for diagnostics only.
    pub preamble: &'a [u8],
    pub header: NetvarHeader,
    /// Variable bytes following the header.
    pub payload: &'a [u8],
}

/// Parse the fixed 20-byte header.
///
/// Nothing past the header is consumed, so callers still own the payload bytes.
///
/// ```text
/// 0000000000000000   constant preamble
///                 0000   list id
///                     0000   packet index within the list
///                         0000   variables in packet
///                             0000   total datagram length
///                                 00000000   cycle counter
/// ```
pub fn parse_header(input: &[u8]) -> IResult<&[u8], NetvarHeader> {
    map(
        tuple((take(PREAMBLE_LEN), le_u16, le_u16, le_u16, le_u16, le_u32)),
        |(_preamble, list_id, packet_index, variables, total_len, cycle)| NetvarHeader {
            list_id,
            packet_index,
            variables,
            total_len,
            cycle,
        },
    )(input)
}

/// Whether the datagram starts with the expected CODESYS preamble.
pub fn has_known_preamble(preamble: &[u8]) -> bool {
    preamble.starts_with(KNOWN_PREAMBLE_PREFIX)
}

/// Parse a complete datagram into header and payload, validating the length field.
pub fn parse_datagram(input: &[u8]) -> Result<ParsedDatagram<'_>, NetvarError> {
    match parse_header(input) {
        Ok((_rest, header)) => {
            if usize::from(header.total_len) != input.len() {
                return Err(NetvarError::LengthMismatch {
                    declared: header.total_len,
                    actual: input.len(),
                });
            }
            Ok(ParsedDatagram {
                preamble: &input[..PREAMBLE_LEN],
                header,
                payload: &input[HEADER_LEN..],
            })
        }
        Err(e) => {
            let actual = input.len();
            if actual < HEADER_LEN {
                return Err(NetvarError::TooShort { actual });
            }
            Err(NetvarError::Nom(e.to_string()))
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// Build a full datagram from a payload, matching the wire format the parser expects.
    fn build_datagram(list_id: u16, cycle: u32, payload: &[u8]) -> Vec<u8> {
        let mut datagram = Vec::with_capacity(HEADER_LEN + payload.len());
        datagram.extend_from_slice(KNOWN_PREAMBLE_PREFIX);
        datagram.extend_from_slice(&[0u8; PREAMBLE_LEN - KNOWN_PREAMBLE_PREFIX.len()]);
        datagram.extend_from_slice(&list_id.to_le_bytes());
        datagram.extend_from_slice(&0u16.to_le_bytes());
        datagram.extend_from_slice(&(payload.len() as u16).to_le_bytes());
        datagram.extend_from_slice(&((HEADER_LEN + payload.len()) as u16).to_le_bytes());
        datagram.extend_from_slice(&cycle.to_le_bytes());
        datagram.extend_from_slice(payload);
        datagram
    }

    #[test]
    fn parse_header_reads_little_endian_fields() {
        let datagram = build_datagram(4, 0x0403_0201, &[0u8; 12]);
        let (rest, header) = parse_header(&datagram).expect("header should parse");
        assert_eq!(header.list_id, 4);
        assert_eq!(header.packet_index, 0);
        assert_eq!(header.variables, 12);
        assert_eq!(header.total_len, 32);
        assert_eq!(header.cycle, 0x0403_0201);
        assert_eq!(rest.len(), 12);
        assert!(has_known_preamble(&datagram[..PREAMBLE_LEN]));
    }

    #[test]
    fn parse_datagram_returns_header_and_payload_slice() {
        let payload = [1u8, 2, 3, 4];
        let datagram = build_datagram(2, 7, &payload);
        let parsed = parse_datagram(&datagram).expect("datagram should parse");
        assert_eq!(parsed.header.list_id, 2);
        assert_eq!(parsed.header.cycle, 7);
        assert_eq!(parsed.payload, &[1, 2, 3, 4]);
        assert!(parsed.preamble.starts_with(KNOWN_PREAMBLE_PREFIX));
    }

    #[test]
    fn parse_datagram_reads_the_bench_capture_header() {
        // First datagram of the bench capture, minus its (all zero) payload:
        // list 411, packet 0 of 4, 128 variables, 276 bytes, cycle 63.
        let mut datagram = vec![
            0x00, 0x2d, 0x53, 0x33, 0x00, 0x00, 0x00, 0x00, 0x9b, 0x01, 0x00, 0x00, 0x80, 0x00,
            0x14, 0x01, 0x3f, 0x00, 0x00, 0x00,
        ];
        datagram.resize(276, 0);
        let parsed = parse_datagram(&datagram).expect("capture header should parse");
        assert!(has_known_preamble(parsed.preamble));
        assert_eq!(
            parsed.header,
            NetvarHeader {
                list_id: 411,
                packet_index: 0,
                variables: 128,
                total_len: 276,
                cycle: 63,
            }
        );
        assert_eq!(parsed.payload.len(), 256);
    }

    #[test]
    fn parse_datagram_rejects_length_mismatch() {
        let datagram = build_datagram(2, 1, &[0u8; 8]);
        let truncated = &datagram[..datagram.len() - 1];
        assert_eq!(
            parse_datagram(truncated),
            Err(NetvarError::LengthMismatch {
                declared: 28,
                actual: 27
            })
        );
    }

    #[test]
    fn parse_datagram_rejects_short_datagrams() {
        assert_eq!(
            parse_datagram(&[0u8, 1, 2]),
            Err(NetvarError::TooShort { actual: 3 })
        );
    }
}
