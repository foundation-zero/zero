from thrs.messaging.definition import MessageRouter
from thrs.runtime.messages import MessageContext, SimulationInputMessage, SimulationStatusMessage


router = MessageRouter()


@router.handle("inputs", SimulationInputMessage)
def simulation_input(message: SimulationInputMessage, context: MessageContext):
    context.simulation.update_simulation_inputs(message.inputs)

simulation_status = router.define("status", SimulationStatusMessage, )
