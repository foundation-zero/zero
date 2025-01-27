{% macro mqtt_with(topic) %}WITH (
  connector='mqtt',
  url='{{ env_var('MQTT_HOST') }}',
  topic= '{{ topic }}',
  qos = 'exactly_once',
{#  max_packet_size = 2000000,#}
) FORMAT PLAIN ENCODE JSON;
{% endmacro %}
