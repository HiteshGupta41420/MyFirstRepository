
{{- define "invoice-platform.name" -}}
{{- .Chart.Name -}}
{{- end -}}

{{- define "invoice-platform.fullname" -}}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "invoice-platform.labels" -}}
app.kubernetes.io/name: {{ include "invoice-platform.name" . }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}
