# 🎓 UniRent - Campus Equipment Rental System

UniRent is a comprehensive, full-stack rental management platform designed for campus environments. It allows students to browse and securely check out equipment, while providing administrators with a robust set of tools to manage inventory, track rentals, and enforce role-based access.

---

## 🏆 Academic Requirements Met (Final PIT Rubric)

This project was built to satisfy all requirements for the Application Development and Emerging Technologies (IT323) Final PIT. 

### 1. Docker Containerization 🐳
The Django REST Framework backend is fully containerized. 
- **Files Included:** `Dockerfile` and `docker-compose.yml`
- **Purpose:** Ensures a consistent, isolated development environment and seamless deployment.

### 2. Security & Role-Based Access Control (RBAC) 🔐
Implemented two major layers of security:
- **JWT Authentication:** All API endpoints are secured using JSON Web Tokens (SimpleJWT). Users must be authenticated to interact with the system.
- **Role-Based Access Control:** Custom permissions (`IsAdminOrReadOnly`) enforce strict boundaries. 
  - *Students (Tenants)* can only view available items (GET) and manage their own specific rentals.
  - *Staff (Admins)* have exclusive rights to create, update, and delete inventory (POST, PUT, DELETE).

### 3. Full CRUD Operations 📦
The system demonstrates complete Create, Read, Update, and Delete lifecycles:
- **Create (POST):** Register users, create new inventory items (Admins), and check out equipment (Students).
- **Read (GET):** Fetch global inventory, view personal user profiles, and retrieve active/historical rental transactions.
- **Update (PUT/PATCH):** Update user profiles and change item statuses (e.g., from 'Available' to 'Occupied' upon checkout, or resetting locker labels upon return).
- **Delete (DELETE):** Permanently remove rental transaction records.

### 4. System Integration & Data Flow 🔄
The architecture follows a strict decoupled data flow:
- **Frontend (React Web / React Native Mobile) ➔ API (Django REST Framework) ➔ Database (SQLite).**

---

## 💻 Technology Stack
* **Backend:** Python, Django, Django REST Framework
* **Mobile Frontend:** React Native, Expo
* **Web Frontend:** React.js 
* **Database:** SQLite (Development)
* **Authentication:** SimpleJWT (JSON Web Tokens)
* **Infrastructure:** Docker, Docker Compose

---

## 🚀 Getting Started (Running the Backend via Docker)

To run the API server locally using Docker, ensure you have Docker Desktop installed and follow these steps:

1. **Clone the repository:**
   ```bash
   git clone <your-repository-url>
   cd <your-backend-folder>
