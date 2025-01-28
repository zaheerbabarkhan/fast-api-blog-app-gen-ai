## Installation

### Prerequisites

- Python 3.10 or higher
- PostgreSQL (if using PostgreSQL or set the `DATABASE_TYPE` to `SQLITE` in the .env file)

### Steps

1. **Clone the repository:**

   ```sh
   git clone https://github.com/yourusername/fast-api-blog-app-gen-ai.git
   cd fast-api-blog-app-gen-ai
   ```

2. **Install `uv` using pip:**

   ```sh
   pip install uv
   ```

3. **Sync the dependencies using `uv`:**

   ```sh
   uv sync
   ```

4. **Add the .env file:**

   Create a .env file in the root directory and add the following environment variables:

   ```env
   # Environment
   ENV=development

   # Use SQLITE value to connect to SQLite database, otherwise will be connected to PostgreSQL
   DATABASE_TYPE=SQLITE

   # DATABASE
   POSTGRES_SERVER=localhost
   POSTGRES_PORT=5432
   POSTGRES_DB=gen-ai-fast-api
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=Password123,

   # Super admin details
   SUPER_ADMIN_EMAIL=super_admin@super.com
   SUPER_ADMIN_NAME=Super Admin
   SUPER_ADMIN_USER_NAME=super_admin
   SUPER_ADMIN_PASSWORD=Password123,
   ```

   If you want to run the application using SQLite, set `DATABASE_TYPE` to `SQLITE`.

5. **Initialize the database:**

   ```sh
   python app/init_db.py
   ```

6. **Run the application:**

   ```sh
   uv run uvicorn app.main:app --reload
   ```

   The application will be available at `http://127.0.0.1:8000`.

## Usage

### API Endpoints

- **User Registration:** `POST /api/v1/users/`
- **User Login:** `POST /api/v1/login/access-token`
- **Get Current User:** `GET /api/v1/users/me`
- **Update Current User:** `PATCH /api/v1/users/me`
- **CRUD Posts:** `GET /api/v1/posts/`
- **Admin Routes:** `GET /api/v1/backoffice/users`
- **Admin Activate User:** `PATCH /api/v1/backoffice/users/{user_id}/activate`

### Authentication

To access protected routes, you need to include the `Authorization` header with the Bearer token obtained from the login endpoint.

Example:

```sh
curl -X 'GET' \
  'http://localhost:8000/api/v1/users/me' \
  -H 'Authorization: Bearer your_access_token'
```
