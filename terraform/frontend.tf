resource "azurerm_container_registry" "acr" {
  name                = "crBikefitting"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Basic"
  admin_enabled       = true
}

resource "azurerm_app_service_plan" "asp" {
  name                = "asp-${var.name}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  kind                = "Linux"
  reserved            = true

  sku {
    tier = "Basic"
    size = "B1"
  }
}

resource "azurerm_app_service" "as" {
  name                = var.name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  app_service_plan_id = azurerm_app_service_plan.asp.id

  app_settings = {
    WEBSITES_ENABLE_APP_SERVICE_STORAGE = false
    DOCKER_ENABLE_CI                    = true
    DOCKER_REGISTRY_SERVER_URL          = "https://${azurerm_container_registry.acr.login_server}"
  }
  site_config {
    linux_fx_version                     = "DOCKER|${azurerm_container_registry.acr.login_server}/${var.frontend-image}:latest"
    acr_use_managed_identity_credentials = "true"
  }
  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_container_registry_webhook" "webhook" {
  name                = "webappbikefitting"
  resource_group_name = azurerm_resource_group.rg.name
  registry_name       = azurerm_container_registry.acr.name
  location            = azurerm_resource_group.rg.location

  service_uri = "https://${azurerm_container_registry.acr.login_server}/${var.frontend-image}" #NOT CORRECT: SET MANUALLY IN PORTAL
  status      = "enabled"
  scope       = "${var.frontend-image}:latest"
  actions     = ["push"]
  custom_headers = {
    "Content-Type" = "application/json"
  }

  lifecycle {
    ignore_changes = [
      service_uri
    ]
  }
}

resource "azurerm_role_assignment" "ra_acr" {
  scope                = azurerm_container_registry.acr.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_app_service.as.identity.0.principal_id
}