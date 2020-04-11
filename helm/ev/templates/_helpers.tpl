

{{- define "image_repository" -}}
{{- required "image.repository is required" .Values.image.repository -}}
{{- end -}}

{{- define "image_tag" -}}
{{- required "image.tag is required" .Values.image.tag -}}
{{- end -}}


{{ define "imagePullSecret" }}
{{ if .Values.image.private }}
imagePullSecrets:
- name: {{ .Values.image.imagePullSecret }}
{{ end }}
{{ end }}