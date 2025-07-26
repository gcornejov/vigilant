provider "google" {
  project = var.project_id
  region  = var.location
}

resource "google_project_service" "google_api" {
  for_each = toset(var.apis)

  service            = each.key
  disable_on_destroy = false
}

resource "google_service_account" "vigilant_robot" {
  account_id   = "vigilant-robot"
  display_name = "Vigilant Robot"
}

resource "google_storage_bucket" "browser_screenshots" {
  name                     = "vigilant-295410116663"
  location                 = "US"
  force_destroy            = true
  public_access_prevention = "enforced"

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 3
    }
  }
}

resource "google_storage_bucket_iam_member" "robot_object_creator" {
  bucket = google_storage_bucket.browser_screenshots.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${google_service_account.vigilant_robot.email}"
}

resource "google_secret_manager_secret_iam_member" "secret_access" {
  for_each = var.env_secrets

  secret_id = each.value
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.vigilant_robot.email}"
}

resource "google_cloud_run_v2_service" "vigilant_robot" {
  name     = "vigilant"
  location = var.location

  template {
    execution_environment            = "EXECUTION_ENVIRONMENT_GEN2"
    service_account                  = google_service_account.vigilant_robot.email
    max_instance_request_concurrency = 1

    scaling {
      min_instance_count = 0
      max_instance_count = 1
    }

    containers {
      image = var.service_image

      resources {
        cpu_idle          = true
        startup_cpu_boost = true

        limits = {
          cpu    = "1"
          memory = "2Gi"
        }
      }

      ports {
        container_port = 8080
      }

      env {
        name  = "STORAGE_LOCATION"
        value = "gcs"
      }

      env {
        name  = "BUCKET_NAME"
        value = google_storage_bucket.browser_screenshots.name
      }

      dynamic "env" {
        for_each = var.env_secrets

        content {
          name = env.key

          value_source {
            secret_key_ref {
              secret  = env.value
              version = "latest"
            }
          }
        }
      }
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  deletion_protection = false
}

resource "google_cloud_run_v2_service_iam_member" "vigilant_robot" {
  name     = google_cloud_run_v2_service.vigilant_robot.name
  location = google_cloud_run_v2_service.vigilant_robot.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}
