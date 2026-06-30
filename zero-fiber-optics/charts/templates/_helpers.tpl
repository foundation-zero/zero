{{/*
Expand the name of the chart.
*/}}
{{- define "zero-fiber-optics.name" -}}
{{- default "fiber-optics" .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "zero-fiber-optics.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := include "zero-fiber-optics.name" . }}
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
{{- define "zero-fiber-optics.chart" -}}
{{- printf "%s-%s" (include "zero-fiber-optics.name" .) .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "zero-fiber-optics.labels" -}}
helm.sh/chart: {{ include "zero-fiber-optics.chart" . }}
{{ include "zero-fiber-optics.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "zero-fiber-optics.selectorLabels" -}}
app.kubernetes.io/name: {{ include "zero-fiber-optics.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
