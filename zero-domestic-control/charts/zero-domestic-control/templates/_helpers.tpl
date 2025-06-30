{{/*
Expand the name of the chart.
*/}}
{{- define "zero-domestic-control.name" -}}
{{- default "domestic-control" .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "zero-domestic-control.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := include "zero-domestic-control.name" . }}
{{- $releaseName := regexReplaceAll "(-?[^a-z\\d\\-])+-?" (lower .Release.Name) "-" -}}
{{- if contains $name $releaseName }}
{{- $releaseName | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" $releaseName $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{- define "zero-domestic-control.backend" -}}
  {{- printf "%s-backend" (include "zero-domestic-control.name" .) -}}
{{- end -}}

{{- define "zero-domestic-control.control" -}}
  {{- printf "%s-control" (include "zero-domestic-control.name" .) -}}
{{- end -}}

{{- define "zero-domestic-control.stub" -}}
  {{- printf "%s-stub" (include "zero-domestic-control.name" .) -}}
{{- end -}}

{{- define "zero-domestic-control.envvars" -}}
  {{- printf "%s-envvars" (include "zero-domestic-control.name" .) -}}
{{- end -}}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "zero-domestic-control.chart" -}}
{{- printf "%s-%s" (include "zero-domestic-control.name" .) .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "zero-domestic-control.labels" -}}
helm.sh/chart: {{ include "zero-domestic-control.chart" . }}
{{ include "zero-domestic-control.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "zero-domestic-control.selectorLabels" -}}
app.kubernetes.io/name: {{ include "zero-domestic-control.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Common envs from secrets
*/}}
{{- define "zero-domestic-control.postgresqlPasswordEnvFromSecret" -}}
{{- if .Values.postgresql.existingSecret -}}
- name: PG_PASSWORD
  valueFrom:
    secretKeyRef:
      name: {{ .Values.postgresql.existingSecret }}
      key: {{ .Values.postgresql.existingSecretPasswordKey }}
{{- end -}}
{{- end -}}

{{- define "zero-domestic-control.hasuraJwtEnvFromSecret" -}}
{{- if .Values.hasura.existingSecret }}
- name: JWT_SECRET
  valueFrom:
    secretKeyRef:
      name: {{ .Values.hasura.existingSecret }}
      key: {{ .Values.hasura.existingSecretJwtKey }}
{{- end }}
{{- end }}

{{- define "zero-domestic-control.homeAssistantTokenEnvFromSecret" -}}
{{- if .Values.homeAssistant.existingSecret }}
- name: HOME_ASSISTANT_TOKEN
  valueFrom:
    secretKeyRef:
      name: {{ .Values.homeAssistant.existingSecret }}
      key: {{ .Values.homeAssistant.existingSecretTokenKey }}
{{- end }}
{{- end }}
