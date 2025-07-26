variable "project_id" {
  type = string
}

variable "location" {
  type = string
}

variable "apis" {
  type = list(string)
}

variable "env_secrets" {
  type = map(string)
}

variable "service_image" {
  type = string
}
