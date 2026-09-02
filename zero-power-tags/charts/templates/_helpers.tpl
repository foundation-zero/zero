{{/*
Expand the name of the chart.
*/}}
{{- define "zero-power-tags.name" -}}
{{- default "zero-power-tags" .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "zero-power-tags.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := include "zero-power-tags.name" . }}
{{- $releaseName := regexReplaceAll "(-?[^a-z\\d\\-])+-?" (lower .Release.Name) "-" -}}
{{- if contains $name $releaseName }}
{{- $releaseName | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" $releaseName $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "zero-power-tags.chart" -}}
{{- printf "%s-%s" (include "zero-power-tags.name" .) .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "zero-power-tags.labels" -}}
helm.sh/chart: {{ include "zero-power-tags.chart" . }}
{{ include "zero-power-tags.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "zero-power-tags.selectorLabels" -}}
app.kubernetes.io/name: {{ include "zero-power-tags.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Name of the in-cluster stub workload/Service (the `run` deployment points its
panel hosts here when modbus.stub is enabled).
*/}}
{{- define "zero-power-tags.stubName" -}}
{{- printf "%s-stub" (include "zero-power-tags.name" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Deterministic port assigned to each panel in stub mode: the panels are ordered
by sanitized key and spread over consecutive ports from modbus.stub.basePort.
The `run` and `stub` deployments both derive ports this way, so they always
agree without either side depending on the ordering in modbus_bridges.json.
Takes a dict of `ctx` (the root context) and `key` (the panel key).
*/}}
{{- define "zero-power-tags.stubPort" -}}
{{- $key := .key -}}
{{- $base := int .ctx.Values.modbus.stub.basePort -}}
{{- range $i, $k := (keys .ctx.Values.modbus.panels | sortAlpha) -}}
{{- if eq $k $key }}{{ add $base $i }}{{- end -}}
{{- end -}}
{{- end }}

{{/*
Service/containerPort name for a panel's stub server (an IANA_SVC_NAME: <= 15
chars, lower-case). Takes a dict with `key` (the panel key).
*/}}
{{- define "zero-power-tags.stubPortName" -}}
{{- printf "modbus-%s" (.key | lower | replace "_" "-") | trunc 15 | trimSuffix "-" -}}
{{- end }}

{{/*
Panel env vars (MODBUS_PANELS__host_/port_) shared by the run and stub
deployments. In stub mode every panel is pointed at the stub Service on its
assigned port; otherwise the configured host (and optional port) is used. The
host var is what marks a panel "deployed", so the stub also relies on it to
decide which panels to serve (see StubCmd).
*/}}
{{- define "zero-power-tags.panelEnv" -}}
{{- $root := . -}}
{{- $stub := $root.Values.modbus.stub -}}
{{- if and $stub $stub.enabled -}}
{{- $stubName := include "zero-power-tags.stubName" $root -}}
{{- range $key, $panel := $root.Values.modbus.panels }}
- name: MODBUS_PANELS__host_{{ $key | lower }}
  value: {{ $stubName | quote }}
- name: MODBUS_PANELS__port_{{ $key | lower }}
  value: {{ include "zero-power-tags.stubPort" (dict "ctx" $root "key" $key) | quote }}
{{- end }}
{{- else -}}
{{- range $key, $panel := $root.Values.modbus.panels }}
- name: MODBUS_PANELS__host_{{ $key | lower }}
  value: {{ $panel.host | quote }}
{{- if $panel.port }}
- name: MODBUS_PANELS__port_{{ $key | lower }}
  value: {{ $panel.port | quote }}
{{- end }}
{{- end }}
{{- end -}}
{{- end }}
