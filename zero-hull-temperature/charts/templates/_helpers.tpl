{{/*
Expand the name of the chart.
*/}}
{{- define "zero-hull-temperature.name" -}}
{{- default "hull-temperature" .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "zero-hull-temperature.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := include "zero-hull-temperature.name" . }}
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
{{- define "zero-hull-temperature.chart" -}}
{{- printf "%s-%s" (include "zero-hull-temperature.name" .) .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "zero-hull-temperature.labels" -}}
helm.sh/chart: {{ include "zero-hull-temperature.chart" . }}
{{ include "zero-hull-temperature.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "zero-hull-temperature.selectorLabels" -}}
app.kubernetes.io/name: {{ include "zero-hull-temperature.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Stub deployment/service name.
*/}}
{{- define "zero-hull-temperature.stub" -}}
{{- printf "%s-stub" (include "zero-hull-temperature.name" .) -}}
{{- end -}}

{{/*
Selector labels for the stub workload.
*/}}
{{- define "zero-hull-temperature.stubSelectorLabels" -}}
{{ include "zero-hull-temperature.selectorLabels" . }}
app.kubernetes.io/component: stub
{{- end }}
