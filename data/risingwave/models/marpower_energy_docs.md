<!-- Electrical energy metrics -->
{% docs active_power_on_phase %}
The active power (W) measured on phase
{% enddocs %}
{% docs power_factor_on_phase %}
The power factor measured on phase
{% enddocs %}
{% docs rms_current_on_phase %}
The RMS current (A) measured on phase
{% enddocs %}
{% docs rms_voltage_on_phase %}
The RMS voltage (V) measured on phase
{% enddocs %}
{% docs total_active_power_cons %}
The electrical energy (W) currently being consumed.
{% enddocs %}
{% docs total_active_power_prod %}
The electrical energy (W) currently being produced.
{% enddocs %}
{% docs active_power %}
The electrical energy (W) currently being consumed or produced.
{% enddocs %}
{% docs power_factor %}
The power factor of the measured power.
{% enddocs %}
{% docs voltage_at_side %}
The measured voltage (V) at side
{% enddocs %}
{% docs current_at_side %}
The measured current (A) at side
{% enddocs %}
{% docs timestamp_voltage_at_side %}
Timestamp at which the voltage value was measured at side
{% enddocs %}
{% docs timestamp_current_at_side %}
Timestamp at which the current value was measured at side
{% enddocs %}
{% docs stored_energy %}
The electrical energy (kWh) stored in the battery.
{% enddocs %}

<!-- Metadata fields -->
{% docs electrical_system %}
The electrical system a data point belongs to.
{% enddocs %}
{% docs group_name %}
The name of the group. This can be an electrical energy consumer group or an electrical energy producer group.
{% enddocs %}
{% docs sub_group_name %}
The name of the sub-group within a specific group. 
{% enddocs %}
{% docs topic %}
The MQTT topic used to identify a data source.
{% enddocs %}

<!-- Time fields -->
{% docs time %}
The most recent time value the data is based on.
{% enddocs %}
{% docs timestamp %}
The timestamp of the related value.
{% enddocs %}
{% docs zero_timestamp %}
The timestamp determined by ZERO.
{% enddocs %}

<!-- Misc. -->
{% docs dc_converter_sides_explained %}
The values are measured on both sides of the converter (side A and B). The battery will be connected to side A.
{% enddocs %}
{% docs marpower_struct_explained %}
Values are delivered over MQTT in a structure created by Marpower. The structure is a JSON format containing a value and a timestamp.
{% enddocs %}
