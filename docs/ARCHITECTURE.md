# Architecture Overview

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Microsoft Teams                           │
│                                                                  │
│  ┌──────────────┐    ┌─────────────┐    ┌──────────────┐      │
│  │   Bot        │    │  Adaptive   │    │   Teams      │      │
│  │ Integration  │◄───┤   Cards     │◄───┤     Tab      │      │
│  └──────┬───────┘    └─────────────┘    └──────┬───────┘      │
└─────────┼──────────────────────────────────────┼──────────────┘
          │                                       │
          ▼                                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Azure Static Web Apps                          │
│                     (React Frontend)                             │
│                                                                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐               │
│  │   Order    │  │    Menu    │  │  History   │               │
│  │   Page     │  │  Selection │  │   Page     │               │
│  └────────────┘  └────────────┘  └────────────┘               │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          │ HTTPS/REST API
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API Gateway / Load Balancer                   │
└─────────────────────────┬───────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┬──────────────────┐
          │               │               │                  │
          ▼               ▼               ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│    Menu      │  │    Order     │  │     User     │  │ Notification │
│   Scraper    │  │  Management  │  │  Management  │  │   Service    │
│   Service    │  │   Service    │  │   Service    │  │              │
│              │  │              │  │              │  │              │
│ Port: 8001   │  │ Port: 8002   │  │ Port: 8003   │  │ Port: 8004   │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │                 │
       │                 │                 │                 │
       └─────────────────┼─────────────────┴─────────────────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
  │  PostgreSQL  │  │    Redis     │  │   Azure      │
  │   Database   │  │    Cache     │  │  Key Vault   │
  │              │  │              │  │              │
  │  (Persistent │  │  (Menu &     │  │  (Secrets)   │
  │   Storage)   │  │   Sessions)  │  │              │
  └──────────────┘  └──────────────┘  └──────────────┘
```

## Data Flow

### Order Creation Flow

```
1. Manager initiates order
   └─> POST /api/orders
       └─> Order Management Service
           └─> Creates order record in DB
           └─> Triggers Menu Scraper Service
               └─> Scrapes restaurant menu
               └─> Caches menu in Redis
           └─> Notification Service sends Teams message

2. Team members view order
   └─> GET /api/orders/{order_id}
       └─> Order Management Service
           └─> Retrieves order from DB
           └─> GET /api/menu/{restaurant_id} (from cache)

3. Team member selects items
   └─> POST /api/orders/{order_id}/items
       └─> Order Management Service
           └─> Saves order items to DB
           └─> Notification Service confirms to user

4. Manager finalizes order
   └─> POST /api/orders/{order_id}/finalize
       └─> Order Management Service
           └─> Updates order status
           └─> Generates summary
           └─> Notification Service sends to manager
```

## Service Details

### Menu Scraper Service
**Responsibility**: Retrieve and cache restaurant menus

**Endpoints**:
- `POST /api/menu/scrape` - Trigger menu scrape
- `GET /api/menu/{restaurant_id}` - Get cached menu
- `GET /api/menu/restaurants` - List restaurants

**Technology**:
- BeautifulSoup4 for static sites
- Selenium for dynamic sites
- Redis for caching (24-hour TTL)

### Order Management Service
**Responsibility**: Handle order lifecycle

**Endpoints**:
- `POST /api/orders` - Create order
- `GET /api/orders/{order_id}` - Get order details
- `PUT /api/orders/{order_id}` - Update order
- `POST /api/orders/{order_id}/finalize` - Finalize order

**Business Logic**:
- Order validation
- Item aggregation
- Status management
- History tracking

### User Management Service
**Responsibility**: Manage users and defaults

**Endpoints**:
- `POST /api/users` - Create user
- `GET /api/users/{user_id}` - Get user
- `POST /api/users/{user_id}/defaults` - Set default order

**Features**:
- User profiles
- Default orders per restaurant
- Azure AD integration

### Notification Service
**Responsibility**: Send notifications

**Endpoints**:
- `POST /api/notifications/send` - Send notification

**Channels**:
- Microsoft Teams (via Bot Framework)
- Email (future)
- SMS (future)

## Technology Stack

### Backend
- **Language**: Python 3.11
- **Framework**: FastAPI
- **Database**: PostgreSQL (Azure SQL)
- **ORM**: SQLAlchemy
- **Cache**: Redis
- **API Docs**: OpenAPI/Swagger

### Frontend
- **Framework**: React 18
- **UI Library**: Material-UI / Fluent UI
- **State**: Redux or Context API
- **Build**: Vite

### Infrastructure
- **Cloud**: Microsoft Azure
- **Hosting**: 
  - App Services (backend)
  - Static Web Apps (frontend)
- **Database**: Azure SQL Database
- **Cache**: Azure Cache for Redis
- **Secrets**: Azure Key Vault
- **Monitoring**: Application Insights

### DevOps
- **CI/CD**: GitHub Actions
- **IaC**: Azure Bicep
- **Containers**: Docker (optional)

## Security Architecture

### Authentication Flow
```
1. User accesses app
   └─> Azure AD authentication
       └─> Returns JWT token
           └─> Token included in all API requests
               └─> API validates token
                   └─> Authorizes request based on role
```

### Security Layers
1. **Network**: Azure Virtual Network, NSG rules
2. **Application**: JWT tokens, CORS, rate limiting
3. **Data**: Encryption at rest, TLS in transit
4. **Secrets**: Azure Key Vault
5. **Monitoring**: Application Insights, alerts

## Scalability Considerations

### Horizontal Scaling
- All microservices are stateless
- Can scale independently based on load
- Load balancer distributes traffic

### Caching Strategy
- Menu data cached for 24 hours
- Session data in Redis
- Database query result caching

### Performance Optimization
- Database indexing on frequently queried fields
- Connection pooling
- Lazy loading for large datasets
- CDN for static assets

## Deployment Strategy

### Blue-Green Deployment
1. Deploy new version to "staging" slot
2. Run smoke tests
3. Swap staging to production
4. Monitor for errors
5. Rollback if needed (swap back)

### Monitoring
- Real-time error tracking
- Performance metrics
- User analytics
- Cost monitoring

---

**Document Version**: 1.0  
**Last Updated**: 2026-02-18
