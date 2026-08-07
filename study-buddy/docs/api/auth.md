# Authentication API

Base URL: `http://localhost:8000`

---

## POST /auth/register

Register a new student account.

**Request Body**
```json
{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "password": "securepassword123"
}
```

**Response** `201 Created`
```json
{
  "id": 1,
  "name": "Jane Smith",
  "email": "jane@example.com",
  "is_active": true,
  "study_streak": 0,
  "document_count": 0,
  "created_at": "2026-08-07T12:00:00Z"
}
```

**Errors**
- `400` — Email already registered

---

## POST /auth/login

Login and receive a JWT access token.

**Request Body** (form-encoded)
```
username=jane@example.com&password=securepassword123
```

**Response** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errors**
- `401` — Invalid email or password

---

## GET /auth/me

Get the current authenticated user's profile.

**Headers**
```
Authorization: Bearer <access_token>
```

**Response** `200 OK`
```json
{
  "id": 1,
  "name": "Jane Smith",
  "email": "jane@example.com",
  "is_active": true,
  "study_streak": 5,
  "document_count": 3,
  "created_at": "2026-08-07T12:00:00Z"
}
```

**Errors**
- `401` — Missing or invalid token
