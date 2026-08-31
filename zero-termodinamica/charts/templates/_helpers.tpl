{{/*
Expand the name of the chart.
*/}}
{{- define "zero-termodinamica.name" -}}
{{- default "zero-termodinamica" .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "zero-termodinamica.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := include "zero-termodinamica.name" . }}
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
{{- define "zero-termodinamica.chart" -}}
{{- printf "%s-%s" (include "zero-termodinamica.name" .) .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "zero-termodinamica.labels" -}}
helm.sh/chart: {{ include "zero-termodinamica.chart" . }}
{{ include "zero-termodinamica.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "zero-termodinamica.selectorLabels" -}}
app.kubernetes.io/name: {{ include "zero-termodinamica.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Stub deployment/service name.
*/}}
{{- define "zero-termodinamica.stub" -}}
    {{- printf "%s-stub" (include "zero-termodinamica.name" .) -}}
{{- end -}}

{{/*
Selector labels for the stub workload.
*/}}
{{- define "zero-termodinamica.stubSelectorLabels" -}}
{{ include "zero-termodinamica.selectorLabels" . }}
app.kubernetes.io/component: stub
{{- end }}
