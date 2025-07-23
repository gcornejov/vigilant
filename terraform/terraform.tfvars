project_id = "evocative-line-451302-f3"
location   = "us-central1"

apis = [
  "iam.googleapis.com",
  "cloudresourcemanager.googleapis.com",
  "sheets.googleapis.com",
  "storage-component.googleapis.com",
  "storage.googleapis.com",
  "artifactregistry.googleapis.com",
  "cloudbuild.googleapis.com",
  "run.googleapis.com",
]

env_secrets = {
  PORTAL_USERNAME         = "PORTAL_USERNAME"
  PORTAL_PASSWORD         = "PORTAL_PASSWORD"
  PORTAL_LOGIN_URL        = "PORTAL_LOGIN_URL"
  PORTAL_HOME_URL         = "PORTAL_HOME_URL"
  CREDIT_TRANSACTIONS_URL = "CREDIT_TRANSACTIONS_URL"
}
