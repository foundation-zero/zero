from thrs.messaging.definition import MessageRouter
from thrs.runtime.messages import (
    ManualControlMessage,
    MessageContext,
    SetAutomationMessage,
    SetParametersMessage,
)


router = MessageRouter()


@router.handle(":module/controls/manual", ManualControlMessage)
def manual_control(message: ManualControlMessage, context: MessageContext, module: str):
    context.control.manual_controls(module, message.control_values)


@router.handle(":module/controls/set-automation", SetAutomationMessage)
def set_automation(message: SetAutomationMessage, context: MessageContext, module: str):
    context.control.set_automation_mode(module, message.enabled)


@router.handle(":module/controls/set-parameters", SetParametersMessage)
def set_parameters(message: SetParametersMessage, context: MessageContext, module: str):
    context.control.update_parameters_for(module, message.parameters)