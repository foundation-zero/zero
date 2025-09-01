use anyhow::Result;
use futures::TryStream;
use tokio::net::TcpSocket;
use tokio_util::{
    bytes::{Buf, BytesMut},
    codec::Decoder,
};

use crate::msg::{self, PeaksReply, ReplyHeader};

enum PeaksReplyDecoder {
    WaitingHeader,
    WaitingContent { header: ReplyHeader },
}
impl Decoder for PeaksReplyDecoder {
    type Item = PeaksReply;
    type Error = anyhow::Error;
    fn decode(&mut self, buf: &mut BytesMut) -> Result<Option<PeaksReply>, anyhow::Error> {
        match self {
            PeaksReplyDecoder::WaitingHeader => match ReplyHeader::parse(buf) {
                Ok((remaining, header)) => {
                    let header_len = buf.len() - remaining.len();
                    buf.advance(header_len);
                    *self = PeaksReplyDecoder::WaitingContent { header };
                    self.decode(buf)
                }
                Err(nom::Err::Incomplete(_)) => Ok(None),
                Err(e) => Err(anyhow::anyhow!("Error parsing header: {:?}", e)),
            },
            PeaksReplyDecoder::WaitingContent { header } => {
                match header.parse_content::<msg::PeaksReply>(buf) {
                    Ok((remaining, peaks_reply)) => {
                        let consumed = buf.len() - remaining.len();
                        buf.advance(consumed);
                        *self = PeaksReplyDecoder::WaitingHeader;
                        Ok(Some(peaks_reply))
                    }
                    Err(nom::Err::Incomplete(_)) => Ok(None),
                    Err(e) => Err(anyhow::anyhow!("Error parsing PeaksReply content: {:?}", e)),
                }
            }
        }
    }
}

pub struct PeaksClient;

impl PeaksClient {
    pub async fn stream_peaks(
        addr: &str,
    ) -> Result<impl TryStream<Ok = msg::PeaksReply, Error = anyhow::Error>> {
        let socket = TcpSocket::new_v4()?;
        let (rx, _tx) = socket.connect(addr.parse()?).await?.into_split();
        let framed = tokio_util::codec::FramedRead::new(rx, PeaksReplyDecoder::WaitingHeader);
        Ok(framed)
    }
}
