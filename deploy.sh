#!/bin/bash

# MyHealthCare Azure Deployment Script
# Usage: ./deploy.sh [resource-group] [app-name]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Get parameters
RESOURCE_GROUP=${1:-"myhealthcare-rg"}
APP_NAME=${2:-"myhealthcare-api"}

echo ""
print_info "MyHealthCare Azure Deployment"
echo "=================================="
echo ""
print_info "Resource Group: $RESOURCE_GROUP"
print_info "App Name: $APP_NAME"
echo ""

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    print_error "Azure CLI is not installed!"
    print_info "Install: https://docs.microsoft.com/cli/azure/install-azure-cli"
    exit 1
fi

print_success "Azure CLI found"

# Check if logged in
print_info "Checking Azure login status..."
if ! az account show &> /dev/null; then
    print_warning "Not logged in to Azure"
    print_info "Running az login..."
    az login
fi

print_success "Logged in to Azure"

# Create resource group if doesn't exist
print_info "Checking resource group..."
if ! az group show --name "$RESOURCE_GROUP" &> /dev/null; then
    print_warning "Resource group doesn't exist. Creating..."
    az group create --name "$RESOURCE_GROUP" --location "Southeast Asia"
    print_success "Resource group created"
else
    print_success "Resource group exists"
fi

# Check if app exists
print_info "Checking if app exists..."
if az webapp show --resource-group "$RESOURCE_GROUP" --name "$APP_NAME" &> /dev/null; then
    print_warning "App already exists. Updating..."
    DEPLOY_MODE="update"
else
    print_info "Creating new app..."
    DEPLOY_MODE="create"
fi

# Deploy or update
if [ "$DEPLOY_MODE" = "create" ]; then
    print_info "Creating Azure Web App..."
    az webapp up \
        --runtime PYTHON:3.11 \
        --sku B1 \
        --location "Southeast Asia" \
        --resource-group "$RESOURCE_GROUP" \
        --name "$APP_NAME"
    print_success "App created successfully!"
else
    print_info "Deploying to existing app..."
    az webapp up \
        --resource-group "$RESOURCE_GROUP" \
        --name "$APP_NAME"
    print_success "App updated successfully!"
fi

# Configure startup command
print_info "Configuring startup command..."
az webapp config set \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME" \
    --startup-file "backend/startup.sh"
print_success "Startup command configured"

# Generate secret key
print_info "Generating Django SECRET_KEY..."
SECRET_KEY=$(openssl rand -base64 32)

# Set app settings
print_info "Setting environment variables..."
az webapp config appsettings set \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME" \
    --settings \
        DJANGO_SECRET_KEY="$SECRET_KEY" \
        DJANGO_DEBUG=False \
        DJANGO_ALLOWED_HOSTS="$APP_NAME.azurewebsites.net"

print_success "Environment variables set"

# Show deployment info
echo ""
echo "=================================="
print_success "Deployment completed!"
echo "=================================="
echo ""
print_info "App URL: https://$APP_NAME.azurewebsites.net"
print_info "Admin URL: https://$APP_NAME.azurewebsites.net/api/v1/admin/"
echo ""
print_warning "IMPORTANT: You still need to:"
echo "  1. Set DATABASE_URL in Azure Portal"
echo "  2. Configure your database"
echo "  3. Run migrations (they'll run automatically on restart)"
echo ""
print_info "Set DATABASE_URL with:"
echo "  az webapp config appsettings set \\"
echo "    --resource-group $RESOURCE_GROUP \\"
echo "    --name $APP_NAME \\"
echo "    --settings DATABASE_URL='postgresql://user:pass@host:5432/db'"
echo ""
print_info "View logs with:"
echo "  az webapp log tail --resource-group $RESOURCE_GROUP --name $APP_NAME"
echo ""
print_info "Restart app with:"
echo "  az webapp restart --resource-group $RESOURCE_GROUP --name $APP_NAME"
echo ""

