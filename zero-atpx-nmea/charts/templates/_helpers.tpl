{{/*
Expand the name of the chart.
*/}}
{{- define "zero-atpx-nmea.name" -}}
{{- default "zero-atpx-nmea" .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "zero-atpx-nmea.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := include "zero-atpx-nmea.name" . }}
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
{{- define "zero-atpx-nmea.chart" -}}
{{- printf "%s-%s" (include "zero-atpx-nmea.name" .) .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "zero-atpx-nmea.labels" -}}
helm.sh/chart: {{ include "zero-atpx-nmea.chart" . }}
{{ include "zero-atpx-nmea.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "zero-atpx-nmea.selectorLabels" -}}
app.kubernetes.io/name: {{ include "zero-atpx-nmea.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
