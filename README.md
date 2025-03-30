# 🏠 VivaEstate-Backend

**Empowering real estate connections effortlessly and intelligently.**

[![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)](https://www.python.org/)  
[![Django](https://img.shields.io/badge/Django-4.0+-green?logo=django)](https://www.djangoproject.com/)  
[![Docker](https://img.shields.io/badge/Docker-✔-2496ED?logo=docker)](https://www.docker.com/)  
[![Celery](https://img.shields.io/badge/Celery-✔-37814A?logo=celery)](https://docs.celeryq.dev/)  

---

## 🌟 Overview

VivaEstate-Backend is a **Django-powered API** designed to streamline real estate operations, providing scalable and efficient solutions. 

### ✨ Features
- ✅ **Robust Django Framework** – High-performance and scalable backend
- ✅ **Dockerized Environment** – Seamless deployment and development
- ✅ **Asynchronous Processing** – Celery for handling background tasks
- 📧 **Real-time Notifications** – Twilio-powered alerts for agents and clients
- 📚 **OpenAPI Documentation** – Swagger/Redoc for easy API integration

---

## 🛠️ Tech Stack

| Core Technologies  | Extensions & Tools | DevOps & Deployment |
|--------------------|-------------------|----------------------|
| Python 3.8+       | Redis             | Docker              |
| Django 4.0+       | Celery            | Poetry              |
| PostgreSQL        | NumPy             | Gunicorn            |
| DRF (Django REST) | aiohttp           | Twilio              |

---

## 🚀 Getting Started

### 📌 Prerequisites
- Python 3.8+
- Docker (optional)
- Poetry or Pip

### 🛠 Installation

1️⃣ **Clone the repository**:
```bash
 git clone https://github.com/Elite-Project-Dev/vivaestate-backend.git
 cd vivaestate-backend
```

2️⃣ **Install dependencies**:
- Using Poetry:
  ```bash
  poetry install
  ```
- Using Pip:
  ```bash
  pip install -r requirements.txt
  ```

3️⃣ **Run Database Migrations**:
```bash
python manage.py migrate
```

4️⃣ **Run the application**:
- With Poetry:
  ```bash
  poetry run python manage.py runserver
  ```
- With Docker:
  ```bash
  docker build -t qlaz26/vivaestate-backend .
  docker run -p 8000:8000 qlaz26/vivaestate-backend
  ```

---

## 📡 API Usage

- **OpenAPI Documentation**: Available at `/docs` (Swagger/Redoc)
- **Authentication**: JWT-based authentication
- **Sample API Request**:
  ```http
  GET /api/properties
  Authorization: Bearer <your_jwt_token>
  ```

---

## 🧪 Running Tests

Run the test suite to ensure everything is working correctly:
```bash
pytest  # Replace with your actual test command
```

---

## 🤝 Contributing

We welcome contributions! Follow these steps:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/your-feature`)
3. **Commit your changes** (`git commit -m 'Add some feature'`)
4. **Push to the branch** (`git push origin feature/your-feature`)
5. **Open a Pull Request**

---

## 📜 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

💡 *Built with ❤️ by [Elite-Project-Dev](https://github.com/Elite-Project-Dev).*
