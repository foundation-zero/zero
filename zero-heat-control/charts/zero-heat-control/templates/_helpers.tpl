{{/*
Expand the name of the chart.
*/}}
{{- define "zero-heat-control.name" -}}
{{- default "thrs-control" .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "zero-heat-control.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := include "zero-heat-control.name" . }}
{{- $releaseName := regexReplaceAll "(-?[^a-z\\d\\-])+-?" (lower .Release.Name) "-" -}}
{{- if contains $name $releaseName }}
{{- $releaseName | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" $releaseName $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}


{{- define "zero-heat-control.api" -}}
  {{- printf "%s-api" (include "zero-heat-control.name" .) -}}
{{- end -}}

{{- define "zero-heat-control.control" -}}
  {{- printf "%s-control" (include "zero-heat-control.name" .) -}}
{{- end -}}

{{- define "zero-heat-control.simulation" -}}
  {{- printf "%s-simulation" (include "zero-heat-control.name" .) -}}
{{- end -}}

{{- define "zero-heat-control.envvars" -}}
  {{- printf "%s-envvars" (include "zero-heat-control.name" .) -}}
{{- end -}}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "zero-heat-control.chart" -}}
{{- printf "%s-%s" (include "zero-heat-control.name" .) .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "zero-heat-control.labels" -}}
helm.sh/chart: {{ include "zero-heat-control.chart" . }}
{{ include "zero-heat-control.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "zero-heat-control.selectorLabels" -}}
app.kubernetes.io/name: {{ include "zero-heat-control.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}


{{- define "zero-heat-control.livenessProbe" -}}
exec:
  command:
  - /bin/bash
  - -c
  - "test \"$(( `date +%s` - `stat -L --format %Y {{ . }}` ))\" -lt 10"
initialDelaySeconds: 30
periodSeconds: 5
{{- end }}
