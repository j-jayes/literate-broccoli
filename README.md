# Office Lunch Ordering System 🥦

A modern microservice-based tool for streamlining office lunch ordering with menu scraping, order management, and Microsoft Teams integration.

## 🎯 Project Overview

This system automates the lunch ordering process for offices by:
- Automatically scraping restaurant menus
- Providing an intuitive checkbox interface for meal selection
- Supporting default orders for quick ordering
- Integrating with Microsoft Teams for seamless communication
- Maintaining a complete order history
- Generating printable order summaries

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Development](#development)
- [Azure Deployment](#azure-deployment)
- [MS Teams Integration](#ms-teams-integration)
- [Documentation](#documentation)

## ✨ Features

### Core Features
- **Menu Scraping**: Automatically retrieve menus from restaurant websites
- **Order Management**: Create, manage, and track lunch orders
- **Default Orders**: Save favorite orders for one-click ordering
- **Teams Integration**: Native Microsoft Teams bot and adaptive cards
- **Order History**: Complete tracking of all historical orders
- **Printable Summaries**: Clean, formatted order summaries for managers
- **Multi-user Support**: Handle concurrent orders from multiple team members

### Technical Features
- **Microservices Architecture**: Scalable, independent services
- **Azure Cloud Hosting**: Fully deployed on Azure infrastructure
- **RESTful APIs**: Well-documented FastAPI endpoints
- **Database Persistence**: PostgreSQL for reliable data storage
- **Caching**: Redis for improved performance
- **Monitoring**: Application Insights for observability

## 🏗️ Architecture

The system consists of four main microservices:

```
┌─────────────────┐
│   MS Teams Bot  │
└────────┬────────┘
         │
┌────────▼────────────────────────────────────┐
│           Web Frontend (React)              │
└────────┬────────────────────────────────────┘
         │
    ┌────▼────┐
    │   API   │
    │ Gateway │
    └────┬────┘
         │
    ┌────┴────────────────────────────┐
    │                                  │
┌───▼──────┐  ┌──────────┐  ┌────────▼─────┐
│  Menu    │  │  Order   │  │     User     │
│ Scraper  │  │Management│  │  Management  │
└──────────┘  └──────────┘  └──────────────┘
    │              │              │
    └──────┬───────┴──────────────┘
           │
    ┌──────▼──────┐
    │  Database   │
    │ (PostgreSQL)│
    └─────────────┘
```

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- Node.js 16+ (for frontend)
- PostgreSQL (or use Azure SQL)
- Redis (or use Azure Cache for Redis)
- Azure CLI (for deployment)
- Azure subscription (ID: e9b64842-3c87-4665-ad56-86ae7c20fe4b)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/j-jayes/literate-broccoli.git
   cd literate-broccoli
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -e .
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize the database**
   ```bash
   python -c "from src.models.database import init_db; init_db('your_database_url')"
   ```

5. **Run the development server**
   ```bash
   # Start individual microservices (in separate terminals)
   uvicorn src.services.menu_scraper.main:app --reload --port 8001
   uvicorn src.services.order_management.main:app --reload --port 8002
   uvicorn src.services.user_management.main:app --reload --port 8003
   uvicorn src.services.notifications.main:app --reload --port 8004
   ```

## 📁 Project Structure

This project follows the **Cookiecutter Data Science** structure:

```
literate-broccoli/
├── .github/
│   └── workflows/          # GitHub Actions CI/CD pipelines
├── data/
│   ├── external/           # External data sources
│   ├── interim/            # Intermediate processed data
│   ├── processed/          # Final processed data
│   └── raw/                # Raw, immutable data
├── docs/                   # Documentation files
├── models/                 # Trained models (for ML features)
├── notebooks/              # Jupyter notebooks for analysis
├── references/             # Data dictionaries, manuals
├── reports/                # Generated reports
│   └── figures/            # Graphics and visualizations
├── src/                    # Source code
│   ├── services/           # Microservices
│   │   ├── menu_scraper/   # Menu scraping service
│   │   ├── order_management/ # Order management service
│   │   ├── user_management/  # User management service
│   │   └── notifications/    # Notification service
│   ├── data/               # Data processing scripts
│   ├── models/             # Database models
│   ├── utils/              # Utility functions
│   └── web/                # React frontend
├── tests/                  # Unit and integration tests
├── azure/                  # Azure deployment files
│   ├── bicep/             # Infrastructure as Code
│   ├── scripts/           # Deployment scripts
│   └── config/            # Configuration files
├── .env.example           # Example environment variables
├── .gitignore
├── requirements.txt       # Python dependencies
├── setup.py              # Package configuration
├── PROJECT_SPEC.md       # Detailed technical specification
└── README.md             # This file
```

## 💻 Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_orders.py
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## ☁️ Azure Deployment

### Prerequisites

1. **Install Azure CLI**
   ```bash
   # Follow instructions at https://docs.microsoft.com/cli/azure/install-azure-cli
   ```

2. **Login to Azure**
   ```bash
   az login
   az account set --subscription e9b64842-3c87-4665-ad56-86ae7c20fe4b
   ```

### Deploy Infrastructure

```bash
# Run the deployment script
./azure/scripts/deploy.sh
```

This script will:
1. Create the resource group
2. Deploy all Azure resources (App Services, SQL Database, Redis, etc.)
3. Configure networking and security
4. Set up Application Insights for monitoring

### Deploy Application Code

```bash
# Deploy microservices
az webapp up --runtime PYTHON:3.11 --sku B1 \
  --resource-group rg-lunch-ordering-prod \
  --name app-menu-scraper-prod

# Deploy static web app (frontend)
cd src/web
npm run build
az staticwebapp deploy --name swa-lunch-ordering-prod
```

### Configuration

After deployment, configure the following in Azure Key Vault:
- Database connection strings
- Redis connection string
- MS Teams bot credentials
- API secret keys

## 🤖 MS Teams Integration

### Setup Teams App

1. **Register Bot in Azure**
   ```bash
   az bot create --resource-group rg-lunch-ordering-prod \
     --name bot-lunch-ordering \
     --kind registration
   ```

2. **Configure Teams App Manifest**
   - Edit `teams-app/manifest.json`
   - Update bot ID and endpoints
   - Zip the manifest folder

3. **Upload to Teams**
   - In Teams, go to Apps > Manage your apps
   - Upload custom app
   - Select the manifest.zip file

### Using the Bot

Commands available:
- `/order` - Create a new lunch order
- `/mydefault` - Set your default order
- `/history` - View your order history
- `/help` - Show all available commands

## 📚 Documentation

Detailed documentation is available in the following files:

- **[PROJECT_SPEC.md](PROJECT_SPEC.md)** - Complete technical specification
- **[docs/API.md](docs/API.md)** - API documentation
- **[docs/SETUP.md](docs/SETUP.md)** - Detailed setup guide
- **[docs/TEAMS.md](docs/TEAMS.md)** - Teams integration guide

## 🔒 Security

- All secrets stored in Azure Key Vault
- HTTPS/TLS encryption for all communications
- Azure AD authentication
- Database encryption at rest
- Input validation and sanitization
- Regular security scans with CodeQL

## 📊 Monitoring

Access monitoring dashboards:
- **Application Insights**: Performance and error tracking
- **Log Analytics**: Centralized logging
- **Alerts**: Configured for critical issues

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Team

- **Project Lead**: [Your Name]
- **Development Team**: [Team Members]
- **Azure Subscription ID**: e9b64842-3c87-4665-ad56-86ae7c20fe4b

## 📞 Support

For issues and questions:
- Create an issue in GitHub
- Contact the development team
- Check the documentation in `/docs`

---

**Built with ❤️ for efficient office lunch ordering**