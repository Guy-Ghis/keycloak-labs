# OAuth 2.0 Lab - Spring Boot + React + Keycloak

This lab demonstrates a complete **OAuth 2.0 Authorization Code Flow** implementation using Spring Boot, React, and Keycloak. It provides hands-on experience with modern authentication and authorization patterns used in enterprise applications.

## 🎯 Learning Objectives

- Understand OAuth 2.0 Authorization Code Flow
- Implement secure authentication with Keycloak
- Build a full-stack application with OAuth integration
- Learn JWT token handling and validation
- Practice secure session management with OAuth
- Understand the differences between local and OAuth authentication

## 📁 Lab Structure

```plaintext
oauth-lab/
├── oauth/                    # Spring Boot backend
│   ├── src/                 # Java source code
│   ├── build.gradle         # Gradle build configuration
│   ├── docker-compose.yml   # Keycloak and PostgreSQL setup
│   ├── OAuth_Flow_Guide.md  # Detailed OAuth flow explanation
│   └── TOKEN_VALIDATION_EXPLAINED.md # JWT token validation guide
├── oauth-client/            # React frontend
│   ├── src/                 # React source code
│   ├── package.json         # Node.js dependencies
│   └── vite.config.ts       # Vite configuration
└── README.md                # This file
```

## 🚨 The OAuth 2.0 Flow

### What is OAuth 2.0?

OAuth 2.0 is an authorization framework that allows third-party applications to access user resources without exposing user credentials. This lab demonstrates the **Authorization Code Flow**, which is the most secure OAuth flow for web applications.

### Flow Overview

1. **User initiates login** → Frontend redirects to Keycloak
2. **User authenticates** → Keycloak validates credentials
3. **Authorization code returned** → Keycloak redirects back with code
4. **Backend exchanges code** → Backend gets access token from Keycloak
5. **Token validation** → Backend validates JWT token
6. **User session created** → Application creates secure session

## 🛠️ Setup Instructions

### Prerequisites

- **Java 21** (or Java 17+)
- **Node.js 18+** and npm
- **Docker** and Docker Compose
- **Git** for cloning the repository

### Installation

1. **Clone and navigate to the lab:**

   ```bash
   git clone https://github.com/Guy-Ghis/keycloak-labs.git
   cd keycloak-labs/oauth-lab
   ```

2. **Start Keycloak and PostgreSQL:**

   ```bash
   cd oauth
   docker-compose up -d
   ```

3. **Verify services are running:**

   ```bash
   docker ps
   # Should show keycloak and postgres containers
   ```

## 🧪 Running the Lab

### Step 1: Configure Keycloak

1. **Access Keycloak Admin Console:**
   - Open: `http://localhost:7000/admin`
   - Login with: `ghis` / `password`

2. **Create Realm:**
   - Click "Create Realm"
   - Name: `test-realm`
   - Click "Create"

3. **Create OAuth Client:**
   - Go to "Clients" → "Create"
   - Client ID: `test-app`
   - Client Protocol: `openid-connect`
   - Click "Save"

4. **Configure Client Settings:**
   - **Valid Redirect URIs**: `http://localhost:5173/callback`
   - **Web Origins**: `http://localhost:5173`
   - **Access Type**: `confidential`
   - Click "Save"

5. **Get Client Secret:**
   - Go to "Credentials" tab
   - Copy the client secret (needed for backend configuration)

6. **Create Test User:**
   - Go to "Users" → "Add User"
   - Username: `testuser`
   - Email: `test@example.com`
   - First Name: `Test`
   - Last Name: `User`
   - Click "Save"
   - Go to "Credentials" tab
   - Set password: `password123`
   - Turn off "Temporary"
   - Click "Save"

### Step 2: Configure Backend

1. **Update application configuration:**

   ```bash
   # Edit oauth/src/main/resources/application.yml
   # Update these fields:
   # - spring.datasource.url: jdbc:postgresql://localhost:5432/oauth-demo
   # - keycloak.auth-server-url: http://localhost:7000/realms/test-realm
   # - keycloak.client-secret: [your-actual-client-secret]
   ```

2. **Start the Spring Boot backend:**

   ```bash
   cd oauth
   ./gradlew bootRun
   ```

3. **Verify backend is running:**

   ```bash
   curl http://localhost:8081/oauth/health
   # Should return: "OAuth Backend is running!"
   ```

### Step 3: Start Frontend

1. **Install dependencies:**

   ```bash
   cd oauth-client
   npm install
   ```

2. **Start the React application:**

   ```bash
   npm run dev
   ```

3. **Access the application:**
   - Open: `http://localhost:5173`

## 🧪 Testing the Application

### Test Local Authentication

1. **Register a new account:**
   - Click "Register" tab
   - Fill in: Name, Email, Password
   - Click "Create Account"

2. **Login with local account:**
   - Click "Login" tab
   - Enter email and password
   - Click "Sign In"

### Test OAuth 2.0 Flow

1. **Logout first** (if logged in):
   - Click "Sign Out"

2. **Login with Keycloak:**
   - Click "Continue with Keycloak"
   - You'll be redirected to Keycloak login page
   - Login with: `testuser` / `password123`
   - You'll be redirected back with real user data

3. **Observe the OAuth flow:**
   - Check browser network tab for redirects
   - Verify JWT token in browser storage
   - Confirm user data is displayed correctly

## 🔒 Security Features Implemented

### 1. OAuth 2.0 Authorization Code Flow

```java
// Secure authorization code exchange
@GetMapping("/oauth/callback")
public ResponseEntity<String> handleOAuthCallback(@RequestParam String code) {
    // Exchange authorization code for access token
    // Validate JWT token
    // Create secure session
}
```

### 2. JWT Token Validation

```java
// Validate JWT tokens from Keycloak
public boolean validateToken(String token) {
    // Verify token signature
    // Check token expiration
    // Validate token claims
}
```

### 3. Secure Session Management

```java
// Create secure sessions after OAuth authentication
session.setAttribute("user", user);
session.setAttribute("oauth_token", accessToken);
```

### 4. CORS Configuration

```java
// Secure CORS configuration
@CrossOrigin(origins = "http://localhost:5173", allowCredentials = "true")
```

### 5. Password Security

```java
// BCrypt password hashing for local users
@Autowired
private PasswordEncoder passwordEncoder;
```

## 🎓 Key Learning Points

### OAuth 2.0 Concepts

- **Authorization Server** (Keycloak) - Manages user authentication
- **Resource Server** (Spring Boot) - Validates tokens and serves resources
- **Client Application** (React) - Initiates OAuth flow
- **Resource Owner** (User) - Grants access to their resources

### Security Best Practices

- ✅ **Authorization Code Flow** - Most secure OAuth flow
- ✅ **JWT Token Validation** - Verify token authenticity
- ✅ **HTTPS in Production** - Secure communication
- ✅ **State Parameter** - Prevent CSRF attacks
- ✅ **PKCE Extension** - Additional security for public clients

### Common Vulnerabilities to Avoid

- ❌ **Implicit Flow** - Less secure, deprecated
- ❌ **Storing tokens in localStorage** - Vulnerable to XSS
- ❌ **Not validating JWT signatures** - Token forgery
- ❌ **No token expiration checks** - Session hijacking
- ❌ **Insecure redirect URIs** - Authorization code interception

## 🔍 Additional Resources

### Lab Documentation

- `oauth/OAuth_Flow_Guide.md` - Detailed OAuth flow explanation
- `oauth/TOKEN_VALIDATION_EXPLAINED.md` - JWT token validation guide
- `oauth/oauth_flow_script.sh` - Automated OAuth flow testing

### External Resources

- [OAuth 2.0 RFC 6749](https://tools.ietf.org/html/rfc6749)
- [OpenID Connect Core](https://openid.net/specs/openid-connect-core-1_0.html)
- [Keycloak Documentation](https://www.keycloak.org/documentation)
- [Spring Security OAuth](https://docs.spring.io/spring-security/reference/servlet/oauth2/)

## 🔧 Troubleshooting

### Common Issues

#### 1. **401 Unauthorized Error**

**Cause**: Client ID or secret mismatch
**Solution**:

```bash
# Verify client configuration in Keycloak
# Check application.yml matches Keycloak settings
# Ensure client is 'confidential' type
```

#### 2. **Database Connection Error**

**Cause**: PostgreSQL not accessible
**Solution**:

```bash
# Check Docker containers
docker ps

# Restart services
docker-compose down && docker-compose up -d
```

#### 3. **CORS Errors**

**Cause**: Frontend can't access backend
**Solution**:

```bash
# Verify CORS configuration in Spring Boot
# Check Web Origins in Keycloak client settings
```

### Debug Commands

```bash
# Test Keycloak connectivity
curl -X GET "http://localhost:7000/realms/test-realm/.well-known/openid_configuration"

# Test backend health
curl -X GET "http://localhost:8081/oauth/health"

# Check database connection
telnet localhost 5432

# View application logs
docker logs oauth-demo
```

## 🚀 Advanced Features

### Custom Claims

- Add custom user attributes in Keycloak
- Include claims in JWT tokens
- Validate custom claims in backend

### Role-Based Access Control

- Define roles in Keycloak
- Include roles in JWT tokens
- Implement role-based authorization

### Token Refresh

- Implement refresh token flow
- Handle token expiration gracefully
- Maintain user sessions

## ⚠️ Security Notice

This lab is for educational purposes. In production environments:

- **Use HTTPS** for all communications
- **Implement proper error handling**
- **Add comprehensive logging**
- **Use secure session management**
- **Implement rate limiting**
- **Regular security audits**

---

### Happy OAuth Learning! 🔐🚀
