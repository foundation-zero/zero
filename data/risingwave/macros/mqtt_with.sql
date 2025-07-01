{% macro mqtt_with(topic) %}WITH (
  connector = 'mqtt',
  url       = '{{ env_var('MQTT_PROTOCOL') }}://{{ env_var('MQTT_HOST') }}:{{ env_var('MQTT_PORT') }}',
  topic     = '{{ topic }}',
  qos       = 'exactly_once',
) FORMAT PLAIN ENCODE JSON;
{% endmacro %}
