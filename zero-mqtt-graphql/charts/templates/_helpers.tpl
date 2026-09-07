{{/*
Expand the name of the chart.
*/}}
{{- define "zero-mqtt-graphql.name" -}}
{{- default "mqtt-graphql" .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "zero-mqtt-graphql.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := include "zero-mqtt-graphql.name" . }}
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
{{- define "zero-mqtt-graphql.chart" -}}
{{- printf "%s-%s" (include "zero-mqtt-graphql.name" .) .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "zero-mqtt-graphql.labels" -}}
helm.sh/chart: {{ include "zero-mqtt-graphql.chart" . }}
{{ include "zero-mqtt-graphql.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "zero-mqtt-graphql.selectorLabels" -}}
app.kubernetes.io/name: {{ include "zero-mqtt-graphql.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
