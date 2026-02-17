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
    CHILE_USERNAME                = string,
    CHILE_PASSWORD                = string,
    CHILE_LOGIN_URL               = string,
    CHILE_HOME_URL                = string,
    CHILE_CREDIT_TRANSACTIONS_URL = string,
    FALABELLA_USERNAME            = string,
    FALABELLA_PASSWORD            = string,
    FALABELLA_LOGIN_URL           = string,
    FALABELLA_HOME_URL            = string,
  })
}

variable "service_image" {
  type = string
}
