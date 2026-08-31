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
Stub deployment/service name.
*/}}
{{- define "zero-power-tags.stub" -}}
    {{- printf "%s-stub" (include "zero-power-tags.name" .) -}}
{{- end -}}

{{/*
Selector labels for the stub workload.
*/}}
{{- define "zero-power-tags.stubSelectorLabels" -}}
{{ include "zero-power-tags.selectorLabels" . }}
app.kubernetes.io/component: stub
{{- end }}
