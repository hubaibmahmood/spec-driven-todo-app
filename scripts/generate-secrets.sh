#!/usr/bin/env bash
# =============================================================================
# Momentum - Secret Generation & Environment Setup Script
# =============================================================================
# Automatically generates secure random secrets and creates .env file
#
# Usage:
#   ./scripts/generate-secrets.sh
#
# What this script does:
#   1. Generates 3 unique cryptographic secrets (BETTER_AUTH_SECRET, JWT_SECRET, SERVICE_AUTH_TOKEN)
#   2. Generates Fernet encryption key for API key storage
#   3. Creates .env file from .env.example template
#   4. Validates that all secrets are unique
#   5. Prompts for required API keys (Resend, Gemini)
#
# =============================================================================

set -e  # Exit on error
set -u  # Exit on undefined variable

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root (parent of scripts/)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_EXAMPLE="${PROJECT_ROOT}/.env.example"
ENV_FILE="${PROJECT_ROOT}/.env"

# =============================================================================
# Helper Functions
# =============================================================================

print_header() {
    echo -e "${BLUE}=============================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}=============================================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# =============================================================================
# Validation Functions
# =============================================================================

check_prerequisites() {
    print_info "Checking prerequisites..."

    # Check if openssl is installed
    if ! command -v openssl &> /dev/null; then
        print_error "OpenSSL is not installed. Please install it first."
        exit 1
    fi

    # Check if python3 is installed (for Fernet key generation)
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install it first."
        exit 1
    fi

    # Check if .env.example exists
    if [[ ! -f "$ENV_EXAMPLE" ]]; then
        print_error ".env.example not found at $ENV_EXAMPLE"
        exit 1
    fi

    print_success "Prerequisites validated"
}

check_existing_env() {
    if [[ -f "$ENV_FILE" ]]; then
        print_warning ".env file already exists at $ENV_FILE"
        echo -n "Do you want to overwrite it? (y/N): "
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            print_info "Exiting without changes"
            exit 0
        fi
        # Backup existing .env
        cp "$ENV_FILE" "${ENV_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
        print_success "Backed up existing .env file"
    fi
}

# =============================================================================
# Secret Generation Functions
# =============================================================================

generate_openssl_secret() {
    # Generate 32 random bytes, encode as base64
    # Produces ~44 character string with 256 bits of entropy
    openssl rand -base64 32 | tr -d '\n'
}

generate_fernet_key() {
    # Generate Fernet encryption key using Python cryptography library
    python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" | tr -d '\n'
}

validate_secrets_unique() {
    local secret1="$1"
    local secret2="$2"
    local secret3="$3"

    if [[ "$secret1" == "$secret2" ]] || [[ "$secret1" == "$secret3" ]] || [[ "$secret2" == "$secret3" ]]; then
        print_error "Generated secrets are not unique! This should never happen."
        print_error "Please run the script again or report this issue."
        exit 1
    fi
}

# =============================================================================
# Main Script
# =============================================================================

main() {
    print_header "Momentum Secret Generation & Environment Setup"

    # Step 1: Validate prerequisites
    check_prerequisites

    # Step 2: Check for existing .env file
    check_existing_env

    # Step 3: Generate secrets
    print_info "Generating cryptographic secrets..."

    BETTER_AUTH_SECRET=$(generate_openssl_secret)
    JWT_SECRET=$(generate_openssl_secret)
    SERVICE_AUTH_TOKEN=$(generate_openssl_secret)
    ENCRYPTION_KEY=$(generate_fernet_key)

    # Validate uniqueness
    validate_secrets_unique "$BETTER_AUTH_SECRET" "$JWT_SECRET" "$SERVICE_AUTH_TOKEN"

    print_success "Generated 3 unique OpenSSL secrets (256-bit base64)"
    print_success "Generated Fernet encryption key"

    # Step 4: Prompt for API keys
    echo ""
    print_info "API keys required (press Enter to skip and add later):"
    echo ""

    echo -n "Resend API Key (https://resend.com/api-keys): "
    read -r RESEND_API_KEY
    RESEND_API_KEY=${RESEND_API_KEY:-"re_your_resend_api_key_here"}

    echo -n "Gemini API Key (https://aistudio.google.com/app/apikey): "
    read -r GEMINI_API_KEY
    GEMINI_API_KEY=${GEMINI_API_KEY:-"your_gemini_api_key_here"}

    # Step 5: Create .env file from template
    print_info "Creating .env file from template..."

    cp "$ENV_EXAMPLE" "$ENV_FILE"

    # Step 6: Replace placeholders with generated values
    # macOS-compatible sed (use -i '' for in-place editing)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s|BETTER_AUTH_SECRET=.*|BETTER_AUTH_SECRET=$BETTER_AUTH_SECRET|g" "$ENV_FILE"
        sed -i '' "s|JWT_SECRET=.*|JWT_SECRET=$JWT_SECRET|g" "$ENV_FILE"
        sed -i '' "s|SERVICE_AUTH_TOKEN=.*|SERVICE_AUTH_TOKEN=$SERVICE_AUTH_TOKEN|g" "$ENV_FILE"
        sed -i '' "s|ENCRYPTION_KEY=.*|ENCRYPTION_KEY=$ENCRYPTION_KEY|g" "$ENV_FILE"
        sed -i '' "s|RESEND_API_KEY=.*|RESEND_API_KEY=$RESEND_API_KEY|g" "$ENV_FILE"
        sed -i '' "s|AGENT_GEMINI_API_KEY=.*|AGENT_GEMINI_API_KEY=$GEMINI_API_KEY|g" "$ENV_FILE"
    else
        # Linux
        sed -i "s|BETTER_AUTH_SECRET=.*|BETTER_AUTH_SECRET=$BETTER_AUTH_SECRET|g" "$ENV_FILE"
        sed -i "s|JWT_SECRET=.*|JWT_SECRET=$JWT_SECRET|g" "$ENV_FILE"
        sed -i "s|SERVICE_AUTH_TOKEN=.*|SERVICE_AUTH_TOKEN=$SERVICE_AUTH_TOKEN|g" "$ENV_FILE"
        sed -i "s|ENCRYPTION_KEY=.*|ENCRYPTION_KEY=$ENCRYPTION_KEY|g" "$ENV_FILE"
        sed -i "s|RESEND_API_KEY=.*|RESEND_API_KEY=$RESEND_API_KEY|g" "$ENV_FILE"
        sed -i "s|AGENT_GEMINI_API_KEY=.*|AGENT_GEMINI_API_KEY=$GEMINI_API_KEY|g" "$ENV_FILE"
    fi

    print_success ".env file created successfully"

    # Step 7: Display summary
    echo ""
    print_header "Setup Complete!"
    echo ""
    print_success "Generated secrets:"
    echo "  • BETTER_AUTH_SECRET: ${BETTER_AUTH_SECRET:0:20}... (44 chars)"
    echo "  • JWT_SECRET: ${JWT_SECRET:0:20}... (44 chars)"
    echo "  • SERVICE_AUTH_TOKEN: ${SERVICE_AUTH_TOKEN:0:20}... (44 chars)"
    echo "  • ENCRYPTION_KEY: ${ENCRYPTION_KEY:0:20}... (Fernet key)"
    echo ""

    if [[ "$RESEND_API_KEY" == "re_your_resend_api_key_here" ]]; then
        print_warning "Resend API key not set - email verification will not work"
        print_info "Get one at: https://resend.com/api-keys (free tier: 100 emails/day)"
    else
        print_success "Resend API key configured"
    fi

    if [[ "$GEMINI_API_KEY" == "your_gemini_api_key_here" ]]; then
        print_warning "Gemini API key not set - AI agent will not work"
        print_info "Get one at: https://aistudio.google.com/app/apikey (free tier available)"
    else
        print_success "Gemini API key configured"
    fi

    echo ""
    print_info "Next steps:"
    echo "  1. Review and customize .env file if needed"
    echo "  2. Start services: docker-compose up --build"
    echo "  3. Access application: http://localhost:3000"
    echo ""
    print_info "For production deployment:"
    echo "  • Set NODE_ENV=production and ENV=production"
    echo "  • Replace DATABASE_URL with production Neon URL"
    echo "  • Update CORS_ORIGINS and FRONTEND_URL to production domains"
    echo "  • Use HTTPS URLs for all NEXT_PUBLIC_ variables"
    echo ""
}

# Run main function
main
