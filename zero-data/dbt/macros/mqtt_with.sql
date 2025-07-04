{% macro mqtt_with(topic) %}WITH (
  connector = 'mqtt',
  url       = 'mqtt://{{ env_var('MQTT_HOST') }}:{{ env_var('MQTT_PORT') }}',
  topic     = '{{ topic }}',
  qos       = 'exactly_once',
{#  max_packet_size = 2000000,#}
) FORMAT PLAIN ENCODE JSON;
{% endmacro %}
