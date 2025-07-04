{{/*
Expand the name of the chart.
*/}}
{{- define "zero-data-gen.name" -}}
{{- default "data-gen" .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "zero-data-gen.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := include "zero-data-gen.name" . }}
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
{{- define "zero-data-gen.chart" -}}
{{- printf "%s-%s" (include "zero-data-gen.name" .) .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "zero-data-gen.envvars" -}}
  {{- printf "%s-envvars" (include "zero-data-gen.name" .) -}}
{{- end -}}

{{/*
Common labels
*/}}
{{- define "zero-data-gen.labels" -}}
helm.sh/chart: {{ include "zero-data-gen.chart" . }}
{{ include "zero-data-gen.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "zero-data-gen.selectorLabels" -}}
app.kubernetes.io/name: {{ include "zero-data-gen.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
