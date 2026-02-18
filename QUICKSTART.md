# Quick Start Guide

## 🚀 Getting Started in 5 Minutes

This guide will help you get the lunch ordering system up and running quickly.

### Prerequisites Check

Before you begin, make sure you have:
- [ ] Python 3.9 or higher installed
- [ ] Azure CLI installed
- [ ] Access to Azure subscription (e9b64842-3c87-4665-ad56-86ae7c20fe4b)
- [ ] Git installed

### Step 1: Clone and Setup (2 minutes)

```bash
# Clone the repository
git clone https://github.com/j-jayes/literate-broccoli.git
cd literate-broccoli

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

### Step 2: Configure Environment (1 minute)

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
# At minimum, set:
# - DATABASE_URL (or use SQLite for local: sqlite:///./lunch_ordering.db)
# - API_SECRET_KEY (generate one with: openssl rand -hex 32)
```

### Step 3: Initialize Database (1 minute)

```bash
# Create database tables
python -c "from src.models.database import init_db; init_db('sqlite:///./lunch_ordering.db')"
```

### Step 4: Run the Application (1 minute)

```bash
# Start the development server (when services are implemented)
# For now, verify installation:
python -c "import src; print(f'✓ Installation successful! Version: {src.__version__}')"

# Run tests to verify setup
pytest tests/
```

## 🔧 What's Next?

Now that you have the foundation set up, you can:

1. **Implement Services**: Start with Phase 3 of the IMPLEMENTATION_CHECKLIST.md
2. **Deploy to Azure**: Follow the Azure Deployment section in README.md
3. **Customize**: Adapt the system to your specific restaurant needs

## 📋 Current Status

✅ **Completed:**
- Project structure (Cookiecutter Data Science)
- Database models
- API schemas
- Azure deployment templates
- Configuration system
- Documentation

⏳ **Next Steps:**
- Implement Menu Scraper Service
- Implement Order Management Service
- Implement User Management Service
- Build Web Frontend
- Integrate with MS Teams

## 🆘 Need Help?

- Check the full [README.md](README.md)
- Review [PROJECT_SPEC.md](PROJECT_SPEC.md) for technical details
- Follow [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md) for step-by-step guide

## 💡 Quick Tips

1. **Use SQLite for local development** - No need for PostgreSQL initially
2. **Mock scrapers first** - Use static data before implementing web scraping
3. **Test incrementally** - Don't wait to test until everything is built
4. **Follow the checklist** - It's designed to minimize dependencies

---

**Ready to build?** Check out the implementation checklist and start with Phase 3!
