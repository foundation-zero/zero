#! /usr/bin/env python
#
#spectrum_streaming.py
#
#Copyright (c) 2018 by Micron Optics, Inc.  All Rights Reserved
#

import hyperion
import asyncio
import numpy as np

instrument_ip = '10.0.41.3'

loop = asyncio.get_event_loop()
queue = asyncio.Queue(maxsize=5, loop=loop)
stream_active = True

serial_numbers = []

# create the streamer object instance
spectrum_streamer = hyperion.HCommTCPSpectrumStreamer(instrument_ip, loop, queue, hyp_inst.power_cal)

# define a coroutine that pulls data out of the streaming queue and processes it
async def get_data():

    while True:

        spectrum_data = await queue.get()
        queue.task_done()
        if spectrum_data['data']:
            serial_numbers.append(spectrum_data['data'].header.serial_number)
        else:
            # If the queue returns None, then the streamer has stopped.
            break

loop.create_task(get_data())

streaming_time = 5  # seconds

loop.call_later(streaming_time, spectrum_streamer.stop_streaming)

loop.run_until_complete(spectrum_streamer.stream_data())