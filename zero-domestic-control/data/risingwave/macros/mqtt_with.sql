{% macro mqtt_with(topic) %}WITH (
  connector = 'mqtt',
  url       = 'tcp://{{ env_var('MQTT_HOST') }}:{{ env_var('MQTT_PORT') }}',
  topic     = '{{ topic }}',
  qos       = 'exactly_once',
) FORMAT PLAIN ENCODE JSON;
{% endmacro %}
