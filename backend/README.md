# FastAPI with MySQL and SQLAlchemy

This project sets up a simple **FastAPI** application with **MySQL** as the database and **SQLAlchemy** as the ORM to interact with the database.

## Features

- FastAPI for building the RESTful API
- SQLAlchemy for interacting with MySQL database
- Automatic API documentation generated with Swagger UI

## Prerequisites

Before starting, make sure you have the following installed:

- **Python 3.8+**
- **MySQL** or **MariaDB** database server running locally or remotely.

## Installation

Follow these steps to set up the project locally.

### 1. Clone the repository

Clone this repository to your local machine:

```bash
git clone https://github.com/<your-username>/fastapi-mysql-project.git
cd fastapi-mysql-project
```

### 2. Create a virtual environment

It's highly recommended to use a virtual environment to keep dependencies isolated:

Linux/macOS:

bash
Copiar código
python3 -m venv venv
source venv/bin/activate
Windows:

```bash
Copiar código
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

Once the virtual environment is activated, install the project dependencies:

```bash
Copiar código
pip install -r requirements.txt
```

### 4. sqlacodegen

parche para python 3.11

/venv/lib/python3.11/site-packages/sqlacodegen/codegen.py
remplazar

```bash
from inspect import ArgSpec
```

por

```bash
from inspect import getfullargspec as ArgSpec
```

si generar nuevos modelos

```bash
sqlacodegen mysql+pymysql://user:contraseña@localhost:3306/database --tables nombre_tabla > nombre_models.py
```
