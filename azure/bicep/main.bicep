// Azure Bicep template for deploying the lunch ordering system
// Deploy with: az deployment group create --resource-group rg-lunch-ordering-prod --template-file main.bicep

targetScope = 'resourceGroup'

@description('Location for all resources')
param location string = 'eastus'

@description('Environment name')
@allowed([
  'dev'
  'staging'
  'prod'
])
param environment string = 'prod'

@description('Unique suffix for resource names')
param uniqueSuffix string = uniqueString(resourceGroup().id)

// Variables
var appServicePlanName = 'asp-lunch-ordering-${environment}'
var webAppNames = [
  'app-menu-scraper-${environment}-${uniqueSuffix}'
  'app-order-management-${environment}-${uniqueSuffix}'
  'app-user-management-${environment}-${uniqueSuffix}'
  'app-notifications-${environment}-${uniqueSuffix}'
]
var staticWebAppName = 'swa-lunch-ordering-${environment}-${uniqueSuffix}'
var sqlServerName = 'sql-lunch-ordering-${environment}-${uniqueSuffix}'
var sqlDatabaseName = 'lunch-ordering-db'
var redisCacheName = 'redis-lunch-ordering-${environment}-${uniqueSuffix}'
var keyVaultName = 'kv-lunch-${environment}-${uniqueSuffix}'
var appInsightsName = 'ai-lunch-ordering-${environment}'
var logAnalyticsName = 'log-lunch-ordering-${environment}'

// Log Analytics Workspace
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: logAnalyticsName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// Application Insights
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
  }
}

// App Service Plan
resource appServicePlan 'Microsoft.Web/serverfarms@2022-03-01' = {
  name: appServicePlanName
  location: location
  sku: {
    name: 'B1'
    tier: 'Basic'
    capacity: 1
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
}

// Web Apps for Microservices
resource webApps 'Microsoft.Web/sites@2022-03-01' = [for webAppName in webAppNames: {
  name: webAppName
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      alwaysOn: true
      appSettings: [
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: appInsights.properties.ConnectionString
        }
        {
          name: 'WEBSITES_ENABLE_APP_SERVICE_STORAGE'
          value: 'false'
        }
      ]
    }
    httpsOnly: true
  }
}]

// Static Web App (for frontend)
resource staticWebApp 'Microsoft.Web/staticSites@2022-03-01' = {
  name: staticWebAppName
  location: location
  sku: {
    name: 'Free'
    tier: 'Free'
  }
  properties: {}
}

// SQL Server
resource sqlServer 'Microsoft.Sql/servers@2022-05-01-preview' = {
  name: sqlServerName
  location: location
  properties: {
    administratorLogin: 'sqladmin'
    administratorLoginPassword: 'ChangeMe123!' // Should be from Key Vault in production
    version: '12.0'
    minimalTlsVersion: '1.2'
  }
}

// SQL Database
resource sqlDatabase 'Microsoft.Sql/servers/databases@2022-05-01-preview' = {
  parent: sqlServer
  name: sqlDatabaseName
  location: location
  sku: {
    name: 'Basic'
    tier: 'Basic'
    capacity: 5
  }
  properties: {
    collation: 'SQL_Latin1_General_CP1_CI_AS'
    maxSizeBytes: 2147483648
  }
}

// SQL Firewall Rule (Allow Azure Services)
resource sqlFirewallRule 'Microsoft.Sql/servers/firewallRules@2022-05-01-preview' = {
  parent: sqlServer
  name: 'AllowAzureServices'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

// Redis Cache
resource redisCache 'Microsoft.Cache/redis@2022-06-01' = {
  name: redisCacheName
  location: location
  properties: {
    sku: {
      name: 'Basic'
      family: 'C'
      capacity: 0
    }
    enableNonSslPort: false
    minimumTlsVersion: '1.2'
  }
}

// Key Vault
resource keyVault 'Microsoft.KeyVault/vaults@2023-02-01' = {
  name: keyVaultName
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    accessPolicies: []
    enableRbacAuthorization: true
  }
}

// Outputs
output appServicePlanId string = appServicePlan.id
output webAppNames array = [for i in range(0, length(webAppNames)): webApps[i].name]
output staticWebAppUrl string = staticWebApp.properties.defaultHostname
output sqlServerFqdn string = sqlServer.properties.fullyQualifiedDomainName
output sqlDatabaseName string = sqlDatabase.name
output redisCacheHostName string = redisCache.properties.hostName
output keyVaultUri string = keyVault.properties.vaultUri
output appInsightsInstrumentationKey string = appInsights.properties.InstrumentationKey
output appInsightsConnectionString string = appInsights.properties.ConnectionString
