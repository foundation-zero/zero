{{/*
Expand the name of the chart.
*/}}
{{- define "zero-thrs-control.name" -}}
{{- default "thrs-control" .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "zero-thrs-control.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := include "zero-thrs-control.name" . }}
{{- $releaseName := regexReplaceAll "(-?[^a-z\\d\\-])+-?" (lower .Release.Name) "-" -}}
{{- if contains $name $releaseName }}
{{- $releaseName | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" $releaseName $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}


{{- define "zero-thrs-control.control" -}}
  {{- printf "%s-control" (include "zero-thrs-control.name" .) -}}
{{- end -}}

{{- define "zero-thrs-control.simulation" -}}
  {{- printf "%s-simulation" (include "zero-thrs-control.name" .) -}}
{{- end -}}

{{- define "zero-thrs-control.envvars" -}}
  {{- printf "%s-envvars" (include "zero-thrs-control.name" .) -}}
{{- end -}}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "zero-thrs-control.chart" -}}
{{- printf "%s-%s" (include "zero-thrs-control.name" .) .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "zero-thrs-control.labels" -}}
helm.sh/chart: {{ include "zero-thrs-control.chart" . }}
{{ include "zero-thrs-control.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "zero-thrs-control.selectorLabels" -}}
app.kubernetes.io/name: {{ include "zero-thrs-control.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
