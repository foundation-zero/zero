use anyhow::Result;
use futures::TryStream;
use tokio::io::AsyncReadExt;
use tokio::net::TcpSocket;
use tokio_stream::wrappers::ReceiverStream;

use crate::msg::{self, PeaksReply, ReplyHeader};

pub struct PeaksClient;

impl PeaksClient {
    pub async fn stream_peaks(
        addr: &str,
    ) -> Result<impl TryStream<Ok = msg::PeaksReply, Error = anyhow::Error>> {
        let a = TcpSocket::new_v4()?;
        let (mut rx, _tx) = a.connect(addr.parse()?).await?.into_split();
        let (tx_ch, rx_ch) = tokio::sync::mpsc::channel::<Result<PeaksReply, anyhow::Error>>(8);
        tokio::spawn(async move {
            let mut buffer = circular::Buffer::with_capacity(2 * 8 * 128); // Assuming max 128 peaks, each f64 is 8 bytes, double for safety
            loop {
                let read = rx.read(buffer.space()).await.unwrap();
                buffer.fill(read);
                if read != 0 {
                    match ReplyHeader::parse(buffer.data()) {
                        Ok((remaining, header)) => {
                            buffer.consume(buffer.available_data() - remaining.len());
                            loop {
                                let read = rx.read(buffer.space()).await.unwrap();
                                buffer.fill(read);
                                match header.parse_content::<msg::PeaksReply>(buffer.data()) {
                                    Ok((remaining, peaks_reply)) => {
                                        buffer.consume(buffer.available_data() - remaining.len());
                                        tx_ch.send(Ok(peaks_reply)).await.unwrap();
                                        break;
                                    }
                                    Err(nom::Err::Incomplete(_)) => {
                                        // Need more data
                                    }
                                    Err(e) => {
                                        log::error!("Error parsing PeaksReply: {:?}", e);
                                        break;
                                    }
                                }
                            }
                        }
                        Err(nom::Err::Incomplete(_)) => {
                            // Need more data
                        }
                        Err(e) => {
                            log::error!("Error parsing PeaksReply: {:?}", e);
                            break;
                        }
                    }
                }
            }
        });
        Ok(ReceiverStream::new(rx_ch))
    }
}
