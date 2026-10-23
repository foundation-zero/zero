{{/*
Expand the name of the chart.
*/}}
{{- define "zero-alert-forwarder.name" -}}
{{- default "alert-forwarder" .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "zero-alert-forwarder.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := include "zero-alert-forwarder.name" . }}
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
{{- define "zero-alert-forwarder.chart" -}}
{{- printf "%s-%s" (include "zero-alert-forwarder.name" .) .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "zero-alert-forwarder.labels" -}}
helm.sh/chart: {{ include "zero-alert-forwarder.chart" . }}
{{ include "zero-alert-forwarder.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "zero-alert-forwarder.selectorLabels" -}}
app.kubernetes.io/name: {{ include "zero-alert-forwarder.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Liveness probe: the file touched after every poll must be fresh.
*/}}
{{- define "zero-alert-forwarder.livenessProbe" -}}
exec:
  command:
  - /bin/bash
  - -c
  - "test \"$(( `date +%s` - `stat -L --format %Y {{ .Values.livenessPath }}` ))\" -lt {{ .Values.livenessMaxAgeSeconds }}"
initialDelaySeconds: 30
periodSeconds: 5
{{- end }}

{{/*
Readiness probe: polling is set up, so a rolling update may stop the old pod.
*/}}
{{- define "zero-alert-forwarder.readinessProbe" -}}
exec:
  command:
  - /bin/bash
  - -c
  - "test -e {{ .Values.readinessPath }}"
periodSeconds: 2
{{- end }}
