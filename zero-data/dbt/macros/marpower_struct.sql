{% macro marpower_struct(type) -%}
  STRUCT<"Value" {{ type }}, TimeStamp TIMESTAMPTZ, IsValid BOOLEAN, HasValue BOOLEAN>
{%- endmacro %}
