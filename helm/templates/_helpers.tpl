{{- define "s3app.name" }}
{{- .Values.k8s.identifier }}
{{- end }}

{{- define "s3app.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "s3app.container.listener.port" -}}
{{- if .Values.nginxproxy.enabled -}}
{{- .Values.listenerPort -}}
{{- else -}}
8080
{{- end -}}
{{- end -}}

