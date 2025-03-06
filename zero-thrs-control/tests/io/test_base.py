from input_output.sensor import FlowSensor


def test_flow_sensor():
    message = """{
        "flow": {
            "value": 12.12,
            "has-value": true,
            "is-valid": true,
            "timestamp": "2025-01-21T08:49:03.6735253Z"
        },
        "temperature": {
            "value": 17.12,
            "has-value": true,
            "is-valid": true,
            "timestamp": "2025-01-21T08:49:03.6735253Z"
        }
    }"""
    parsed_message = FlowSensor.model_validate_json(message)
    assert parsed_message.temperature.value == 17.12
