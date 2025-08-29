#! /usr/bin/env python
#
#sensor_streaming.py
#
#Copyright (c) 2018 by Micron Optics, Inc.  All Rights Reserved
#

import hyperion
import asyncio
import numpy as np

instrument_ip = '10.0.10.42'

hyp_inst = hyperion.Hyperion(instrument_ip)
hyp_inst.remove_sensors()

test_sensors = [
    # edit this to define your own sensors
    #     Name        Model   chan. wl     cal
        ['sensor_1', 'os7520', 1, 1590.0, 2300.0],
        ['sensor_2', 'os7520', 1, 1610.0, 2300.0],
        ['sensor_3', 'os7510', 2, 1550.0, 66.0],
        ['sensor_4', 'os7510', 2, 1570.0, 66.0]
    ]


for sensor in test_sensors:
    hyp_inst.add_sensor(*sensor)

sensors = hyp_inst.get_sensor_names()
loop = asyncio.get_event_loop()
queue = asyncio.Queue(maxsize=5, loop=loop)
stream_active = True

serial_numbers = []
timestamps = []

sensor_streamer = hyperion.HCommTCPSensorStreamer(instrument_ip, loop, queue)


async def get_data():

    while True:

        sensor_data = await queue.get()
        queue.task_done()
        if sensor_data['data']:
            serial_numbers.append(sensor_data['data'].header.serial_number)
        else:
            break


loop.create_task(get_data())

streaming_time = 30  # seconds

loop.call_later(streaming_time, sensor_streamer.stop_streaming)

loop.run_until_complete(sensor_streamer.stream_data())

hyp_inst.remove_sensors()

assert (np.diff(np.array(serial_numbers)) == 1).all()