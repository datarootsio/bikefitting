variable "name" {
  type    = string
  default = "bikefitting"
}

variable "frontend-image" {
  type    = string
  default = "bikefitting-frontend-image"
}

locals {
  default_labels = { "image" = var.frontend-image, "name" = var.name }
}