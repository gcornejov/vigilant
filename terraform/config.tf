terraform {
  required_version = ">= 1.12.2"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">=6.45.0, <7.0.0"
    }
  }

  backend "gcs" {
    bucket = "tf-state-295410116663"
    prefix = "terraform/state"
  }
}
