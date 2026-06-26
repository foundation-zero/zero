from thrs.messaging.definition import MessageRouter
from thrs.orchestration.config import Config
from thrs.runtime.runtime import MqttTopicConfig, construct_definition
import thrs.runtime.simulation as simulation

settings = Config()  # type: ignore

definition = construct_definition(MqttTopicConfig.from_settings(settings))

router = MessageRouter()

# TODO: figure out exactly what we want here
# I think it is best to have runtime define the messages it expects and sends out
# So then ideally here we would consume the definitions from there with
# handlers for incoming messages and using `construct` to send out the correct messages
@router.handle(simulation.simulation_status)
def handle_simulation_status():
    pass

