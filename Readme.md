```markdown
# Inventory Management System

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Running Tests](#running-tests)
- [Contributing](#contributing)
- [License](#license)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)
- [Acknowledgments](#acknowledgments)
- [Contact Information](#contact-information)

## Introduction

The Inventory Management System is a web application built with Django that allows users to manage inventory items efficiently. It provides functionalities for user registration, login, and CRUD operations on inventory items. 

## Features

- User registration and authentication
- Create, retrieve, update, and delete inventory items
- Caching mechanism for improved performance using Redis
- Comprehensive testing suite

## Technologies Used

- Python 3.11
- Django
- PostgreSQL
- Redis (for caching)
- Django REST Framework
- SQLite (for testing)

## Installation

To set up the project locally, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/satyajitsjs/inventory_management.git
   cd inventory_management
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows use `env\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database:**
   - Make sure you have PostgreSQL installed and running.
   - Create a database for the project:
     ```sql
     CREATE DATABASE inventory_db;
     CREATE USER inventory_user WITH PASSWORD 'inventory';
     ALTER ROLE inventory_user SET client_encoding TO 'utf8';
     ALTER ROLE inventory_user SET default_transaction_isolation TO 'read committed';
     ALTER ROLE inventory_user SET timezone TO 'UTC';
     GRANT ALL PRIVILEGES ON DATABASE inventory_db TO inventory_user;
     ```

5. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Run the server:**
   ```bash
   python manage.py runserver
   ```

## Usage

- Access the application at `http://127.0.0.1:8000/`.
- Use the API endpoints to manage users and items.

## API Endpoints

### User Registration
- **Endpoint:** `POST /api/register/`
- **Request Body:**
  ```json
  {
      "username": "your_username",
      "password": "your_password",
      "email": "your_email@example.com"
  }
  ```
- **Response:**
  - **201 Created**
    ```json
    {
        "message": "User registered successfully."
    }
    ```
  - **400 Bad Request**
    ```json
    {
        "error": "User registration failed."
    }
    ```

### User Login
- **Endpoint:** `POST /api/login/`
- **Request Body:**
  ```json
  {
      "username": "your_username",
      "password": "your_password"
  }
  ```
- **Response:**
  - **200 OK**
    ```json
    {
        "token": "your_jwt_token"
    }
    ```
  - **401 Unauthorized**
    ```json
    {
        "error": "Invalid credentials provided."
    }
    ```

### Item Management
- **GET** `/api/items/` - Retrieve all items
  - **Headers:** 
    ```plaintext
    Authorization: Bearer your_jwt_token
    ```
  - **Response:**
    - **200 OK**
      ```json
      [
          {
              "id": 1,
              "name": "Item Name",
              "description": "Item Description",
              "quantity": 10
          },
          ...
      ]
      ```

- **POST** `/api/items/` - Create a new item
  - **Headers:** 
    ```plaintext
    Authorization: Bearer your_jwt_token
    ```
  - **Request Body:**
    ```json
    {
        "name": "New Item",
        "description": "Item Description",
        "quantity": 5
    }
    ```
  - **Response:**
    - **201 Created**
      ```json
      {
          "message": "Item created successfully.",
          "item": {
              "id": 2,
              "name": "New Item",
              "description": "Item Description",
              "quantity": 5
          }
      }
      ```
    - **400 Bad Request**
      ```json
      {
          "error": "Item creation failed."
      }
      ```

- **GET** `/api/items/{id}/` - Retrieve a specific item
  - **Headers:** 
    ```plaintext
    Authorization: Bearer your_jwt_token
    ```
  - **Response:**
    - **200 OK**
      ```json
      {
          "id": 1,
          "name": "Item Name",
          "description": "Item Description",
          "quantity": 10
      }
      ```
    - **404 Not Found**
      ```json
      {
          "error": "Item not found."
      }
      ```

- **PUT** `/api/items/{id}/` - Update a specific item
  - **Headers:** 
    ```plaintext
    Authorization: Bearer your_jwt_token
    ```
  - **Request Body:**
    ```json
    {
        "name": "Updated Item",
        "description": "Updated Description",
        "quantity": 15
    }
    ```
  - **Response:**
    - **200 OK**
      ```json
      {
          "message": "Item updated successfully.",
          "item": {
              "id": 1,
              "name": "Updated Item",
              "description": "Updated Description",
              "quantity": 15
          }
      }
      ```
    - **404 Not Found**
      ```json
      {
          "error": "Item not found."
      }
      ```

- **DELETE** `/api/items/{id}/` - Delete a specific item
  - **Headers:** 
    ```plaintext
    Authorization: Bearer your_jwt_token
    ```
  - **Response:**
    - **204 No Content** (if successfully deleted)
    - **404 Not Found**
      ```json
      {
          "error": "Item not found."
      }
      ```

## Running Tests

To run the test suite, execute the following command:

```bash
python manage.py test
```

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Environment Variables

Make sure to set the following environment variables before running the application:

- `REDIS_HOST`: The hostname of your Redis server (default: `localhost`)
- `REDIS_PORT`: The port number for your Redis server (default: `6379`)
- `REDIS_TTL`: The time-to-live for cache items in seconds (default: `300`)

You can set these variables in your terminal or create a `.env` file and use a package like `python-decouple` to load them.

## Troubleshooting

- **Database Connection Issues:** Ensure that PostgreSQL is running and that the credentials in the `settings.py` file are correct.
  
- **Redis Connection Errors:** Make sure that Redis is installed and running. You can check if it's running by executing `redis-cli ping` in your terminal. You should receive a response of `PONG`.

- **Test Failures:** If you encounter errors while running tests, ensure that your database is correctly set up and migrations have been applied. If you changed the models, remember to run migrations again.

## Acknowledgments

- [Django](https://www.djangoproject.com/) for the web framework
- [Django REST Framework](https://www.django-rest-framework.org/) for building APIs
- [PostgreSQL](https://www.postgresql.org/) for the database
- [Redis](https://redis.io/) for caching
- [OpenAI](https://openai.com/) for providing inspiration and resources

## Contact Information

If you have any questions, feel free to reach out to me:

- Name: Satyajit
- Email: [satyajitofficial4@gmail.com](mailto:satyajitofficial4@gmail.com)
- GitHub: [satyajitsjs](https://github.com/satyajitsjs)
```
