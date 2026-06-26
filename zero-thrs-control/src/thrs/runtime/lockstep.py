from thrs.messaging.definition import MessageRouter
from thrs.runtime.messages import (
    MessageContext,
    SimulationPauseMessage,
    SimulationPlayMessage,
    SimulationStepMessage,
)

router = MessageRouter()


@router.handle("play", SimulationPlayMessage)
def simulation_play(message: SimulationPlayMessage, context: MessageContext):
    context.loop.play(message.playback_rate)


@router.handle("pause", SimulationPauseMessage)
def simulation_pause(message: SimulationPauseMessage, context: MessageContext):
    context.loop.pause()


@router.handle("step", SimulationStepMessage)
def simulation_step(message: SimulationStepMessage, context: MessageContext):
    context.loop.step(message.seconds)
