from datetime import datetime, timedelta


from pytest import fixture
from orchestration.collector import PolarsCollector
from orchestration.executor import SimulationExecutor
from orchestration.interfacer import Interfacer


@fixture
def executor(io_mapping, simulation_inputs):
    return SimulationExecutor(io_mapping,
    simulation_inputs,
    datetime.now(),
    timedelta(seconds = 1))


collector = PolarsCollector()

async def test_interfacer(executor,io_mapping, simulation_inputs, control):
    interfacer = Interfacer(control, executor)
    result = await interfacer.run(20, collector)
    return collector


