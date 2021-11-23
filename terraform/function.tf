resource "azurerm_resource_group" "rg-func" {
  name     = "rg-${var.name}-function-tf"
  location = "westeurope"
}

resource "azurerm_app_service_plan" "asp-func" {
  name                = "asp-${var.name}-function"
  location            = azurerm_resource_group.rg-func.location
  resource_group_name = azurerm_resource_group.rg-func.name
  kind                = "FunctionApp"
  reserved            = true

  sku {
    tier = "Dynamic"
    size = "Y1"
  }
}

resource "azurerm_function_app" "function" {
  name                       = "fa-${var.name}"
  location                   = azurerm_resource_group.rg-func.location
  resource_group_name        = azurerm_resource_group.rg-func.name
  app_service_plan_id        = azurerm_app_service_plan.asp-func.id
  storage_account_name       = azurerm_storage_account.sa.name
  storage_account_access_key = azurerm_storage_account.sa.primary_access_key

  os_type = "linux"
  version = "~3"

  app_settings = {
    "APPINSIGHTS_INSTRUMENTATIONKEY"  = azurerm_application_insights.insights.instrumentation_key
    "AzureWebJobsStorage"             = azurerm_storage_account.sa.primary_connection_string
    "WEBSITE_RUN_FROM_PACKAGE"        = ""
    "FUNCTIONS_WORKER_RUNTIME"        = "python"
    "WEBSITE_ENABLE_SYNC_UPDATE_SITE" = "true"
  }
  site_config {
    linux_fx_version          = "python|3.8"
    use_32_bit_worker_process = false
  }

  lifecycle {
    ignore_changes = [
      app_settings["WEBSITE_RUN_FROM_PACKAGE"],
      app_settings["AZURE_ML_MODEL_ENDPOINT"],
    ]
  }
}