use std::io::Cursor;
use std::str::FromStr;

use crate::stub::Sweep;
use crate::SignalFrequency;
use anyhow::anyhow;
use anyhow::Result;
use binrw::io::SeekFrom;
use binrw::meta::ReadEndian;
use binrw::{binrw, BinRead, BinWrite};
use nom::error::ErrorKind;
use nom::{
    bytes::streaming::take,
    error::Error,
    number::streaming::{le_u16, le_u32, le_u8},
    IResult, Parser,
};
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use strum::Display;
use tokio::io::{AsyncWrite, AsyncWriteExt};

#[binrw]
#[brw(little)]
#[derive(PartialEq, Eq, Clone, Debug, Copy)]
pub struct RequestOption {
    val: u8,
}
impl RequestOption {
    pub fn parse(val: u8) -> RequestOption {
        RequestOption { val: val & 0x07 } // Take only 3 last bits
    }

    pub fn new(suppress_msg: bool, suppress_content: bool, compress: bool) -> Self {
        let val = [
            (suppress_msg, SUPPRESS_MESSAGE_MASK),
            (suppress_content, SUPPRESS_CONTENT_MASK),
            (compress, COMPRESS_MASK),
        ]
        .iter()
        .fold(0u8, |acc, (val, mask)| if *val { acc + *mask } else { acc });
        RequestOption { val }
    }

    #[allow(dead_code)]
    pub fn suppress_msg(&self) -> bool {
        (self.val & SUPPRESS_MESSAGE_MASK) != 0
    }

    #[allow(dead_code)]
    pub fn suppress_content(&self) -> bool {
        (self.val & SUPPRESS_CONTENT_MASK) != 0
    }

    #[allow(dead_code)]
    pub fn compress(&self) -> bool {
        (self.val & COMPRESS_MASK) != 0
    }
}

#[derive(Debug, Clone, Display, PartialEq, Eq)]
pub enum Command {
    #[strum(serialize = "#EnablePeakDataStreaming")]
    EnablePeakDataStreaming,
    #[strum(serialize = "#DisablePeakDataStreaming")]
    DisablePeakDataStreaming,
    #[strum(serialize = "#EnableFullSpectrumDataStreaming")]
    EnableFullSpectrumDataStreaming,
    #[strum(serialize = "#DisableFullSpectrumDataStreaming")]
    DisableFullSpectrumDataStreaming,
    #[strum(serialize = "#GetLaserScanSpeed")]
    GetLaserScanSpeed,
    #[strum(serialize = "#SetLaserScanSpeed")]
    SetLaserScanSpeed(SignalFrequency),
    #[strum(disabled)]
    #[allow(dead_code)]
    Stop,
}
impl Command {
    pub fn from_str(command: &str, arguments: &str) -> Result<Self> {
        match command {
            "#EnablePeakDataStreaming" => Ok(Command::EnablePeakDataStreaming),
            "#DisablePeakDataStreaming" => Ok(Command::DisablePeakDataStreaming),
            "#EnableFullSpectrumDataStreaming" => Ok(Command::EnableFullSpectrumDataStreaming),
            "#DisableFullSpectrumDataStreaming" => Ok(Command::DisableFullSpectrumDataStreaming),
            "#GetLaserScanSpeed" => Ok(Command::GetLaserScanSpeed),
            "#SetLaserScanSpeed" => {
                let freq = SignalFrequency::from_str(arguments)
                    .map_err(|_| anyhow!("Invalid argument for SetLaserScanSpeed"))?;
                Ok(Command::SetLaserScanSpeed(freq))
            }
            _ => Err(anyhow!("Unknown command")),
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CommandMsg {
    pub request_option: RequestOption,
    pub reserved: u8,
    pub command_size: u16,
    pub argument_size: u32,
    pub command: Command,
    pub arguments: String,
}

const SUPPRESS_MESSAGE_MASK: u8 = 0x01;
const SUPPRESS_CONTENT_MASK: u8 = 0x02;
const COMPRESS_MASK: u8 = 0x04;

impl CommandMsg {
    pub fn parse(input: &[u8]) -> IResult<&[u8], CommandMsg> {
        let (input, (request_option, reserved, command_size, argument_size)) =
            (le_u8, le_u8, le_u16, le_u32).parse(input)?;

        let (input, command_bytes) = take::<_, _, Error<&[u8]>>(command_size)(input)?;
        let (input, argument_bytes) = take::<_, _, Error<&[u8]>>(argument_size)(input)?;

        let command = String::from_utf8_lossy(command_bytes);

        let arguments = String::from_utf8_lossy(argument_bytes);

        Ok((
            input,
            CommandMsg {
                request_option: RequestOption::parse(request_option),
                reserved,
                command_size,
                argument_size,
                command: Command::from_str(&command, &arguments)
                    .map_err(|_| nom::Err::Failure(Error::new(input, ErrorKind::MapRes)))?,
                arguments: arguments.to_string(),
            },
        ))
    }

    #[allow(dead_code)]
    pub fn to_bytes(&self) -> Vec<u8> {
        let mut bytes =
            Vec::with_capacity(self.command_size as usize + self.argument_size as usize + 6);

        bytes.push(self.request_option.val);
        bytes.push(self.reserved);
        bytes.extend_from_slice(&self.command_size.to_le_bytes());
        bytes.extend_from_slice(&self.argument_size.to_le_bytes());
        bytes.extend_from_slice(self.command.to_string().as_bytes());
        bytes.extend_from_slice(self.arguments.as_bytes());
        bytes
    }
}

#[binrw]
#[brw(little)]
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Reply {
    pub header: ReplyHeader,
    #[br(count = header.message_length)]
    pub message: Vec<u8>,
    #[br(count = header.content_length)]
    pub content: Vec<u8>,
}

impl Reply {
    fn build(status: Status, option: RequestOption, msg: Vec<u8>, content: Vec<u8>) -> Self {
        Reply {
            header: ReplyHeader {
                status: status.value(),
                option,
                message_length: msg.len() as u16,
                content_length: content.len() as u32,
            },
            message: msg,
            content,
        }
    }

    pub async fn write_async(&self, writer: &mut (impl AsyncWrite + Unpin)) -> Result<()> {
        self.header.write_async(writer).await?;
        writer.write_all(&self.message).await?;
        writer.write_all(&self.content).await?;
        Ok(())
    }
}

impl From<&PeaksReply> for Reply {
    fn from(value: &PeaksReply) -> Self {
        let mut writer = Cursor::new(Vec::new());
        value.write(&mut writer).unwrap();
        Reply::build(
            Status::Ok,
            RequestOption::new(false, false, false),
            Vec::new(),
            writer.into_inner(),
        )
    }
}
pub enum Status {
    Ok,
    #[allow(dead_code)]
    Fail,
}
impl Status {
    pub fn value(&self) -> u8 {
        match self {
            Status::Ok => 0,
            Status::Fail => 1,
        }
    }
}

#[binrw]
#[brw(little)]
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ReplyHeader {
    status: u8,
    option: RequestOption,
    message_length: u16,
    content_length: u32,
}
impl ReplyHeader {
    pub fn size() -> usize {
        8
    }
    pub fn parse(input: &[u8]) -> IResult<&[u8], ReplyHeader> {
        if input.len() < ReplyHeader::size() {
            Err(nom::Err::Incomplete(nom::Needed::new(
                ReplyHeader::size() - input.len(),
            )))
        } else {
            let mut cursor = Cursor::new(input);
            let header = ReplyHeader::read(&mut cursor)
                .map_err(|_| nom::Err::Failure(Error::new(input, ErrorKind::MapRes)))?;

            Ok((&input[(cursor.position() as usize)..], header))
        }
    }
    pub fn parse_content<'i, T: BinRead + ReadEndian + Clone + Sized>(
        &self,
        input: &'i [u8],
    ) -> IResult<&'i [u8], T>
    where
        for<'a> T::Args<'a>: Default,
    {
        let message_len = self.message_length as usize;
        let content_len = self.content_length as usize;
        let total = message_len + content_len;

        if input.len() < total {
            Err(nom::Err::Incomplete(nom::Needed::new(total - input.len())))
        } else {
            // Limit the read window to the declared content length
            let mut cursor = Cursor::new(&input[message_len..message_len + content_len]);
            let parsed = T::read(&mut cursor)
                .map_err(|_| nom::Err::Failure(Error::new(input, ErrorKind::MapRes)))?;

            let consumed_from_original = message_len + cursor.position() as usize;
            Ok((&input[consumed_from_original..], parsed))
        }
    }
    pub async fn write_async(&self, writer: &mut (impl AsyncWrite + Unpin)) -> Result<()> {
        let mut cursor = Cursor::new(Vec::new());
        self.write(&mut cursor)?;
        Ok(writer.write_all(&cursor.into_inner()).await?)
    }
}

#[binrw]
#[brw(little)]
#[derive(Debug, Clone, PartialEq)]
pub struct PeaksReply {
    pub header_length: u16,
    pub header_version: u16,
    pub reserved: u32,
    pub serial_number: u64,
    pub timestamp_seconds: u32,
    pub timestamp_nanoseconds: u32,
    pub num_peaks: [u16; 16],
    #[br(count = num_peaks.iter().sum::<u16>() as usize, seek_before = SeekFrom::Start(header_length as u64))]
    pub peaks: Vec<f64>,
}
impl PeaksReply {
    #[allow(dead_code)]
    pub fn timestamp(&self) -> SystemTime {
        UNIX_EPOCH
            + Duration::from_secs(self.timestamp_seconds as u64)
            + Duration::from_nanos(self.timestamp_nanoseconds as u64)
    }
}
impl From<&Sweep> for PeaksReply {
    fn from(value: &Sweep) -> Self {
        let mut num_peaks = [0u16; 16];
        let peaks = value.peaks.iter().map(|p| p.wavelength).collect();

        for peak in &value.peaks {
            num_peaks[(peak.channel - 1) as usize] += 1;
        }
        log::info!("num_peaks: {:?}", num_peaks);
        let since_epoch = value.timestamp.duration_since(UNIX_EPOCH).unwrap();

        PeaksReply {
            header_length: (24 + size_of_val(&num_peaks)) as u16, // Size of header + size of num_peaks array
            header_version: 1,
            reserved: 0,
            serial_number: value.serial_number,
            timestamp_seconds: since_epoch.as_secs() as u32,
            timestamp_nanoseconds: since_epoch.subsec_nanos(),
            num_peaks,
            peaks,
        }
    }
}

#[cfg(test)]
mod tests {
    use crate::stub::Peak;

    use super::*;

    #[test]
    fn test_parse_message_valid() {
        const COMMAND_TEXT: &[u8] = b"#DisablePeakDataStreaming";
        const ARGUMENTS_TEXT: &[u8] = b"test";

        let mut input = Vec::new();
        input.extend_from_slice(&1u8.to_le_bytes());
        input.extend_from_slice(&0u8.to_le_bytes());
        input.extend_from_slice(&(COMMAND_TEXT.len() as u16).to_le_bytes());
        input.extend_from_slice(&4u32.to_le_bytes());
        input.extend_from_slice(COMMAND_TEXT);
        input.extend_from_slice(ARGUMENTS_TEXT);

        let result = CommandMsg::parse(&input);
        assert!(result.is_ok());

        let (remaining, message) = result.unwrap();
        assert_eq!(remaining.len(), 0);
        assert_eq!(message.request_option.suppress_msg(), true);
        assert_eq!(message.request_option.suppress_content(), false);
        assert_eq!(message.request_option.compress(), false);
        assert_eq!(message.reserved, 0);
        assert_eq!(message.command_size, COMMAND_TEXT.len() as u16);
        assert_eq!(message.argument_size, 4);
        assert_eq!(
            message.command,
            Command::from_str(
                &String::from_utf8_lossy(COMMAND_TEXT),
                &String::from_utf8_lossy(ARGUMENTS_TEXT)
            )
            .unwrap()
        );
        assert_eq!(message.arguments, String::from_utf8_lossy(ARGUMENTS_TEXT));
    }

    #[test]
    fn test_parse_message_empty_command_and_args() {
        let mut input = Vec::new();
        input.push(7);
        input.push(128);
        input.extend_from_slice(&0u16.to_le_bytes());
        input.extend_from_slice(&0u32.to_le_bytes());

        let result = CommandMsg::parse(&input);
        assert!(result.is_err());
    }

    #[test]
    fn test_parse_message_insufficient_data() {
        const INSUFFICIENT_INPUT: &[u8] = &[1u8, 0u8, 0u8];
        let result = CommandMsg::parse(INSUFFICIENT_INPUT);
        assert!(result.is_err());
    }

    #[test]
    fn test_parse_message_insufficient_command_data() {
        const SHORT_COMMAND: &[u8] = b"short";

        let mut input = Vec::new();
        input.push(1);
        input.push(0);
        input.extend_from_slice(&10u16.to_le_bytes());
        input.extend_from_slice(&0u32.to_le_bytes());
        input.extend_from_slice(SHORT_COMMAND);

        let result = CommandMsg::parse(&input);
        assert!(result.is_err());
    }

    #[test]
    fn test_roundtrip_message() {
        let cmd = Command::EnablePeakDataStreaming;
        let original_message = CommandMsg {
            request_option: RequestOption::new(true, false, false),
            reserved: 17,
            command_size: cmd.to_string().len() as u16,
            argument_size: 11,
            command: cmd,
            arguments: String::from("hello world"),
        };

        let bytes = original_message.to_bytes();
        let (remaining, parsed_message) = CommandMsg::parse(&bytes).unwrap();

        assert_eq!(remaining.len(), 0);
        assert_eq!(original_message, parsed_message);
    }

    #[test]
    fn test_roundtrip_empty_message() {
        let cmd = Command::EnablePeakDataStreaming;
        let original_message = CommandMsg {
            request_option: RequestOption::new(true, false, false),
            reserved: 128,
            command_size: cmd.to_string().len() as u16,
            argument_size: 0,
            command: cmd,
            arguments: String::new(),
        };

        let bytes = original_message.to_bytes();
        let (remaining, parsed_message) = CommandMsg::parse(&bytes).unwrap();

        assert_eq!(remaining.len(), 0);
        assert_eq!(original_message, parsed_message);
    }

    #[test]
    fn test_reply_header_roundtrip() {
        let original_header = ReplyHeader {
            status: 1,
            option: RequestOption::new(true, false, true),
            message_length: 42,
            content_length: 1000,
        };

        let mut writer = Cursor::new(Vec::new());
        original_header.write(&mut writer).unwrap();

        let (remaining, parsed_header) = ReplyHeader::parse(writer.get_ref()).unwrap();
        assert_eq!(remaining.len(), 0);
        assert_eq!(original_header, parsed_header);
    }

    #[test]
    fn test_reply_header_format() {
        let header = ReplyHeader {
            status: 1,
            option: RequestOption::new(true, false, true),
            message_length: 42,
            content_length: 127,
        };

        let mut writer = Cursor::new(Vec::new());
        header.write(&mut writer).unwrap();
        let bytes = writer.into_inner();

        let expected_bytes = vec![
            1,          // status
            0b00000101, // options
            42, 0, // message_length (u16 little-endian)
            127, 0, 0, 0, // content_length (u32 little-endian)
        ];

        assert_eq!(bytes, expected_bytes);
    }

    #[test]
    fn test_peaks_reply_from_sweep() {
        let seconds = 1625079600; // Example timestamp in seconds
        let nanoseconds = 500_000_000; // Example timestamp in nanoseconds
        let sweep = Sweep {
            serial_number: 12345,
            timestamp: UNIX_EPOCH + Duration::new(seconds, nanoseconds),
            peaks: vec![
                Peak {
                    channel: 1,
                    wavelength: 1550.0,
                },
                Peak {
                    channel: 1,
                    wavelength: 1551.0,
                },
                Peak {
                    channel: 2,
                    wavelength: 1552.0,
                },
            ],
        };

        let peaks_reply = PeaksReply::from(&sweep);
        assert_eq!(peaks_reply.serial_number, 12345);
        assert_eq!(peaks_reply.timestamp_seconds, seconds as u32);
        assert_eq!(peaks_reply.timestamp_nanoseconds, nanoseconds);
        assert_eq!(peaks_reply.num_peaks[0], 2); // Channel 1 has 2 peaks
        assert_eq!(peaks_reply.num_peaks[1], 1); // Channel 2 has 1 peak
        assert_eq!(peaks_reply.num_peaks[2], 0); // Channel 3 has 0 peaks
        assert_eq!(peaks_reply.peaks, vec![1550.0, 1551.0, 1552.0]);
    }

    #[test]
    fn test_reply_from_peak_reply() {
        let peaks_reply = PeaksReply {
            header_length: 24 + 16 * 2, // header + num_peaks array
            header_version: 1,
            reserved: 0,
            serial_number: 12345,
            timestamp_seconds: 1625079600,
            timestamp_nanoseconds: 500_000_000,
            num_peaks: [2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            peaks: vec![1550.0, 1551.0, 1552.0],
        };

        let reply: Reply = Reply::from(&peaks_reply);
        assert_eq!(reply.header.status, Status::Ok.value());
        assert_eq!(reply.header.option, RequestOption::new(false, false, false));
        assert_eq!(reply.header.message_length, 0);
        assert_eq!(reply.header.content_length, 24 + 16 * 2 + 3 * 8); // header + num_peaks + peaks
        assert_eq!(reply.message.len(), 0);
        assert_eq!(reply.content.len(), 24 + 16 * 2 + 3 * 8);
        let parsed_peaks_reply = PeaksReply::read(&mut Cursor::new(&reply.content)).unwrap();
        assert_eq!(parsed_peaks_reply, peaks_reply);
    }

    #[test]
    fn test_peak_reply_roundtrip() {
        let peaks_reply = PeaksReply {
            header_length: 24 + 16 * 2, // header + num_peaks array
            header_version: 1,
            reserved: 0,
            serial_number: 12345,
            timestamp_seconds: 1625079600,
            timestamp_nanoseconds: 500_000_000,
            num_peaks: [2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            peaks: vec![1550.0, 1551.0, 1552.0],
        };
        let mut writer = Cursor::new(Vec::<u8>::new());
        peaks_reply.write(&mut writer).unwrap();
        let parsed = PeaksReply::read(&mut Cursor::new(writer.get_ref())).unwrap();
        assert_eq!(parsed, peaks_reply);
    }
}
