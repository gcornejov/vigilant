variable "project_id" {
  type = string
}

variable "project_number" {
  type = string
}

variable "location" {
  type = string
}

variable "gcs_location" {
  type = string
}

variable "apis" {
  type = list(string)
}

variable "secrets" {
  type = object({
    PORTAL_USERNAME         = string,
    PORTAL_PASSWORD         = string,
    PORTAL_LOGIN_URL        = string,
    PORTAL_HOME_URL         = string,
    CREDIT_TRANSACTIONS_URL = string,
  })
}

variable "service_image" {
  type = string
}
