#! /usr/bin/env python
#
# peak_streaming.py
#
# Copyright (c) 2018 by Micron Optics, Inc.  All Rights Reserved
#

import logging
from re import X
import hyperion
import asyncio
import numpy as np

instrument_ip = '127.0.0.1'

logging.basicConfig()

async def main():
    loop = asyncio.get_event_loop()
    queue = asyncio.Queue(maxsize=5)
    stream_active = True

    serial_numbers = []

    # create the streamer object instance
    peaks_streamer = hyperion.HCommTCPPeaksStreamer(instrument_ip, loop, queue)

    # define a coroutine that pulls data out of the streaming queue and processes it.

    async def get_data():

        while True:

            peak_data = await queue.get()
            print(peak_data["data"].header.timestamp_int)
            print(peak_data['data'].data)
            queue.task_done()
            if peak_data['data']:
                serial_numbers.append(peak_data['data'].header.serial_number)
            else:
                # If the queue returns None, then the streamer has stopped.
                break

    loop.create_task(get_data())

    streaming_time = 5 # seconds

    # Call stop_streaming after the specified amount of time.

    loop.call_later(streaming_time, peaks_streamer.stop_streaming)

    stream_data = loop.create_task(peaks_streamer.stream_data())
    await stream_data

    assert (np.diff(np.array(serial_numbers)) == 1).all()

if __name__ == '__main__':
    asyncio.run(main())
