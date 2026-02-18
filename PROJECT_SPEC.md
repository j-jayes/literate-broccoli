# Office Lunch Ordering Microservice - Technical Specification

## 1. Project Overview

**Project Name:** Office Lunch Ordering System  
**Code Name:** literate-broccoli  
**Version:** 1.0.0  
**Azure Subscription ID:** e9b64842-3c87-4665-ad56-86ae7c20fe4b

### Purpose
A microservice-based tool to streamline office lunch ordering by automating menu retrieval, collecting individual orders, and providing order summaries for managers and team members.

## 2. System Architecture

### 2.1 Microservices Architecture
The system consists of the following microservices:

1. **Menu Scraper Service**
   - Scrapes restaurant menus from various sources
   - Caches menu data for performance
   - API endpoint: `/api/menu/{restaurant_id}`

2. **Order Management Service**
   - Handles order creation and management
   - Stores order history in database
   - Manages default orders per user
   - API endpoints:
     - POST `/api/orders` - Create new order
     - GET `/api/orders/{order_id}` - Get order details
     - GET `/api/orders/history` - Get order history
     - PUT `/api/orders/{order_id}/items` - Update order items

3. **User Management Service**
   - Manages user profiles and default preferences
   - API endpoints:
     - GET `/api/users/{user_id}`
     - PUT `/api/users/{user_id}/defaults`

4. **Notification Service**
   - Sends notifications to manager
   - Sends confirmation to users
   - MS Teams integration
   - API endpoint: POST `/api/notifications`

5. **Web Frontend Service**
   - React-based web interface
   - Checkbox selection UI for menu items
   - Printable order summary view
   - Hosted as Azure Static Web App

### 2.2 Technology Stack

#### Backend
- **Language:** Python 3.9+
- **Framework:** FastAPI
- **Database:** Azure SQL Database / PostgreSQL
- **ORM:** SQLAlchemy
- **Web Scraping:** BeautifulSoup4, Selenium (for dynamic sites)
- **Caching:** Redis (Azure Cache for Redis)
- **API Documentation:** OpenAPI/Swagger

#### Frontend
- **Framework:** React 18
- **UI Components:** Material-UI / Fluent UI (for Teams integration)
- **State Management:** Redux or Context API
- **Build Tool:** Vite

#### Deployment
- **Platform:** Azure
- **Services:**
  - Azure App Service (for FastAPI microservices)
  - Azure Static Web Apps (for frontend)
  - Azure SQL Database (for data persistence)
  - Azure Cache for Redis (for menu caching)
  - Azure Container Registry (for Docker images)
  - Azure Key Vault (for secrets management)
  - Azure Application Insights (for monitoring)

#### MS Teams Integration
- **Method:** Teams App with Adaptive Cards
- **Bot Framework:** Azure Bot Service
- **Authentication:** Azure AD

## 3. Data Models

### 3.1 Database Schema

```sql
-- Users Table
CREATE TABLE users (
    user_id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    ms_teams_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Restaurants Table
CREATE TABLE restaurants (
    restaurant_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    menu_url VARCHAR(500),
    scraper_type VARCHAR(50),
    last_scraped TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Menu Items Table
CREATE TABLE menu_items (
    item_id SERIAL PRIMARY KEY,
    restaurant_id INTEGER REFERENCES restaurants(restaurant_id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2),
    category VARCHAR(100),
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders Table
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    order_date DATE NOT NULL,
    restaurant_id INTEGER REFERENCES restaurants(restaurant_id),
    manager_id VARCHAR(100) REFERENCES users(user_id),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finalized_at TIMESTAMP
);

-- Order Items Table
CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id),
    user_id VARCHAR(100) REFERENCES users(user_id),
    menu_item_id INTEGER REFERENCES menu_items(item_id),
    quantity INTEGER DEFAULT 1,
    is_default BOOLEAN DEFAULT FALSE,
    special_instructions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User Defaults Table
CREATE TABLE user_defaults (
    default_id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) REFERENCES users(user_id),
    restaurant_id INTEGER REFERENCES restaurants(restaurant_id),
    menu_item_id INTEGER REFERENCES menu_items(item_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, restaurant_id)
);
```

### 3.2 API Request/Response Models

```python
# Pydantic models for API

class MenuItem(BaseModel):
    item_id: int
    name: str
    description: Optional[str]
    price: Decimal
    category: str

class OrderItem(BaseModel):
    user_id: str
    user_name: str
    menu_item_id: int
    quantity: int = 1
    is_default: bool = False
    special_instructions: Optional[str]

class CreateOrderRequest(BaseModel):
    order_date: date
    restaurant_id: int
    manager_id: str

class OrderResponse(BaseModel):
    order_id: int
    order_date: date
    restaurant_name: str
    manager_name: str
    status: str
    items: List[OrderItem]
```

## 4. Feature Requirements

### 4.1 Core Features

1. **Menu Scraping**
   - Support for multiple restaurant websites
   - Configurable scraper templates
   - Fallback to manual menu entry if scraping fails
   - Cache menus for 24 hours

2. **Order Creation Flow**
   - Manager selects date and restaurant
   - System scrapes/retrieves menu
   - Link shared with team members
   - Team members select items via checkboxes
   - Option to use "default" order
   - Manager receives notification when all orders submitted

3. **Order Management**
   - View current orders
   - Edit orders before finalization
   - Historical order tracking
   - Export order summary (PDF/Print)

4. **Default Orders**
   - Users can set default order per restaurant
   - One-click "Use Default" option
   - Manager can see who used default

5. **MS Teams Integration**
   - Bot posts daily order link to Teams channel
   - Adaptive card for quick ordering
   - Notifications for order confirmations
   - @mentions for manager when order ready

6. **Printable Output**
   - Clean, formatted order summary
   - Grouped by user
   - Shows item names, quantities, special instructions
   - Total count per item for easy ordering

### 4.2 User Roles

1. **Manager**
   - Creates daily order
   - Receives order summary
   - Can finalize/close orders

2. **Team Member**
   - Selects meal from menu
   - Sets default preferences
   - Views order history

3. **Admin**
   - Manages restaurants
   - Configures scrapers
   - Views system analytics

## 5. User Interface Mockups

### 5.1 Order Selection Page
```
┌─────────────────────────────────────────┐
│  Lunch Order - [Restaurant Name]        │
│  Date: [DD/MM/YYYY]                     │
│  Manager: [Manager Name]                │
├─────────────────────────────────────────┤
│  Your Name: [Dropdown/Auto-filled]      │
│  □ Use my default order                 │
├─────────────────────────────────────────┤
│  Menu:                                  │
│  ┌───────────────────────────────────┐  │
│  │ Appetizers                        │  │
│  │ □ Caesar Salad - $8.00           │  │
│  │ □ Soup of the Day - $6.00        │  │
│  │                                   │  │
│  │ Main Courses                      │  │
│  │ □ Grilled Chicken - $15.00       │  │
│  │ □ Vegetarian Pasta - $12.00      │  │
│  │ □ Beef Burger - $14.00           │  │
│  │                                   │  │
│  │ Beverages                         │  │
│  │ □ Water - $0.00                  │  │
│  │ □ Soft Drink - $3.00             │  │
│  └───────────────────────────────────┘  │
│                                          │
│  Special Instructions:                  │
│  [Text Area]                            │
│                                          │
│  [Submit Order] [Save as Default]       │
└─────────────────────────────────────────┘
```

### 5.2 Manager Summary Page
```
┌─────────────────────────────────────────┐
│  Order Summary - [Restaurant Name]       │
│  Date: [DD/MM/YYYY]                     │
│  Status: [9/12 orders received]         │
├─────────────────────────────────────────┤
│  Individual Orders:                     │
│  ┌───────────────────────────────────┐  │
│  │ John Doe                          │  │
│  │   • Grilled Chicken               │  │
│  │   • Water                         │  │
│  │   Note: No onions                 │  │
│  │                                   │  │
│  │ Jane Smith (Default)              │  │
│  │   • Vegetarian Pasta              │  │
│  │   • Soft Drink                    │  │
│  └───────────────────────────────────┘  │
│                                          │
│  Order Totals:                          │
│  • Grilled Chicken: 3                   │
│  • Vegetarian Pasta: 5                  │
│  • Beef Burger: 4                       │
│  • Water: 8                             │
│  • Soft Drink: 4                        │
│                                          │
│  [Print] [Send to Restaurant] [Close]   │
└─────────────────────────────────────────┘
```

## 6. Azure Deployment Architecture

### 6.1 Azure Resources

```yaml
Resources:
  - Resource Group: rg-lunch-ordering-prod
  - App Service Plan: asp-lunch-ordering (B1)
  - App Services:
    - app-menu-scraper
    - app-order-management
    - app-user-management
    - app-notifications
  - Static Web App: swa-lunch-ordering-frontend
  - Azure SQL Database: sql-lunch-ordering
  - Azure Cache for Redis: redis-lunch-ordering
  - Azure Key Vault: kv-lunch-ordering
  - Application Insights: ai-lunch-ordering
  - Azure Bot Service: bot-lunch-ordering
```

### 6.2 Deployment Pipeline

```yaml
CI/CD Pipeline (GitHub Actions):
  1. Build:
     - Run tests
     - Build Docker images
     - Push to Azure Container Registry
  
  2. Deploy to Staging:
     - Deploy microservices to staging slots
     - Run integration tests
     - Deploy frontend to staging environment
  
  3. Deploy to Production:
     - Swap staging to production
     - Health check
     - Rollback on failure
```

## 7. Security Considerations

1. **Authentication**
   - Azure AD integration
   - JWT tokens for API authentication
   - MS Teams SSO

2. **Authorization**
   - Role-based access control (RBAC)
   - Manager-only endpoints protected

3. **Data Protection**
   - Secrets in Azure Key Vault
   - SSL/TLS for all communications
   - Database encryption at rest

4. **Input Validation**
   - Sanitize all web scraping inputs
   - Validate all API inputs with Pydantic
   - Prevent SQL injection with ORM

## 8. MS Teams Integration Details

### 8.1 Teams App Components

1. **Bot**
   - Posts daily order notifications
   - Responds to commands:
     - `/order` - Create new order
     - `/mydefault` - Set default order
     - `/history` - View order history

2. **Tab**
   - Embedded web app in Teams
   - Full order interface within Teams

3. **Adaptive Cards**
   - Quick order submission
   - Order status updates
   - Reminders for pending orders

### 8.2 Teams Integration Flow

```
1. Manager creates order via web app or Teams bot
2. Bot posts Adaptive Card to Teams channel
3. Team members click card to open order form
4. Submit orders (either via embedded tab or external link)
5. Bot sends confirmation to each user
6. Bot notifies manager when all orders received
7. Manager finalizes order
8. Bot posts summary to channel
```

## 9. Implementation Phases

### Phase 1: Core Infrastructure (Week 1-2)
- Set up Azure resources
- Initialize database schema
- Create basic API structure
- Implement authentication

### Phase 2: Menu Scraping (Week 2-3)
- Develop scraper framework
- Implement restaurant-specific scrapers
- Add caching layer
- Create admin UI for scraper configuration

### Phase 3: Order Management (Week 3-4)
- Implement order CRUD operations
- Build web frontend for order selection
- Add default order functionality
- Create printable summary view

### Phase 4: MS Teams Integration (Week 4-5)
- Develop Teams bot
- Create Adaptive Cards
- Implement Teams tab
- Set up notification workflows

### Phase 5: Testing & Deployment (Week 5-6)
- Integration testing
- User acceptance testing
- Performance optimization
- Production deployment

### Phase 6: Monitoring & Iteration (Ongoing)
- Monitor usage with Application Insights
- Gather user feedback
- Implement improvements
- Add new restaurant scrapers

## 10. Development Guidelines

### 10.1 Code Structure (Cookiecutter Data Science)

```
literate-broccoli/
├── .github/
│   └── workflows/           # GitHub Actions CI/CD
├── data/
│   ├── external/           # External data sources
│   ├── interim/            # Intermediate data
│   ├── processed/          # Final data
│   └── raw/                # Raw, immutable data
├── docs/                   # Documentation
├── models/                 # Trained models (if ML used)
├── notebooks/              # Jupyter notebooks for analysis
├── references/             # Data dictionaries, manuals
├── reports/                # Generated analysis reports
│   └── figures/            # Graphics for reports
├── src/                    # Source code
│   ├── __init__.py
│   ├── services/           # Microservices
│   │   ├── menu_scraper/
│   │   ├── order_management/
│   │   ├── user_management/
│   │   └── notifications/
│   ├── data/               # Data processing scripts
│   ├── models/             # Database models
│   ├── utils/              # Utility functions
│   └── web/                # Frontend React app
├── tests/                  # Unit and integration tests
├── azure/                  # Azure deployment files
│   ├── bicep/             # Infrastructure as Code
│   ├── scripts/           # Deployment scripts
│   └── config/            # Configuration files
├── .env.example           # Example environment variables
├── .gitignore
├── requirements.txt       # Python dependencies
├── setup.py              # Package setup
├── README.md
└── PROJECT_SPEC.md       # This file
```

### 10.2 Best Practices

1. **Version Control**
   - Commit frequently with clear messages
   - Use feature branches
   - Code review before merging

2. **Testing**
   - Unit tests for all services
   - Integration tests for API endpoints
   - E2E tests for critical user flows
   - Minimum 80% code coverage

3. **Documentation**
   - Inline code comments
   - API documentation with Swagger
   - User guides in `/docs`
   - Architecture diagrams

4. **Code Quality**
   - Follow PEP 8 for Python
   - Use type hints
   - Linting with pylint/flake8
   - Format with black

## 11. Configuration Management

### 11.1 Environment Variables

```bash
# Azure
AZURE_SUBSCRIPTION_ID=e9b64842-3c87-4665-ad56-86ae7c20fe4b
AZURE_RESOURCE_GROUP=rg-lunch-ordering-prod

# Database
DATABASE_URL=postgresql://user:pass@host:5432/lunch_ordering
DATABASE_POOL_SIZE=10

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL=86400

# MS Teams
TEAMS_BOT_ID=<bot-id>
TEAMS_BOT_PASSWORD=<bot-password>
TEAMS_TENANT_ID=<tenant-id>

# API
API_BASE_URL=https://api.lunch-ordering.com
API_SECRET_KEY=<secret-key>

# Logging
LOG_LEVEL=INFO
APPLICATION_INSIGHTS_KEY=<key>
```

## 12. Monitoring & Analytics

### 12.1 Key Metrics

1. **System Health**
   - API response times
   - Error rates
   - Database connection pool usage
   - Cache hit rates

2. **Business Metrics**
   - Orders per day
   - Most popular restaurants
   - Most popular menu items
   - Default order usage rate
   - User engagement rates

3. **Alerts**
   - Scraper failures
   - API downtime
   - Database connection issues
   - Unusual spike in errors

## 13. Future Enhancements

1. **AI/ML Features**
   - Menu item recommendations based on history
   - Automatic restaurant rotation suggestions
   - Dietary restriction detection

2. **Additional Integrations**
   - Slack integration
   - Expense tracking integration
   - Calendar integration for automatic scheduling

3. **Advanced Features**
   - Budget management per team
   - Split payment handling
   - Delivery tracking
   - Rating system for restaurants

## 14. Success Criteria

1. **Technical**
   - 99.9% uptime
   - < 2 second page load times
   - < 500ms API response times
   - Zero data loss

2. **User Adoption**
   - 80%+ team adoption within first month
   - Average 3+ orders per user per week
   - Positive user satisfaction score (>4/5)

3. **Efficiency**
   - Reduce order coordination time by 80%
   - Zero order errors
   - 100% order history tracking

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-18  
**Author:** Development Team  
**Status:** Draft
