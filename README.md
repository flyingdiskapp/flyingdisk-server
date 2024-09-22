# FdServer

## Information

FdServer is a simple [Flying Disk](https://github.com/flyingdiskapp/fdcli) server written in Python. 

## Usage

### Start server

```bash
python3 run.py
```

## Configuration

Configuration options can be changed in the `config.py` file located in the root of the project.

**Available Configuration Options:**

* **ALLOW_INSTALLATION (boolean):**
    * Controls whether package installation is enabled for users.
    * **Default:** `True` (Installation is enabled)
    * Set to `False` to disable package installation functionality.

* **ALLOW_LOGIN (boolean):**
    * Controls whether user login is enabled.
    * **Default:** `True` (Login is enabled)
    * Set to `False` to disable user login functionality.

* **ALLOW_REGISTRATION (boolean):**
    * Controls whether user registration is enabled.
    * **Default:** `False` (Registration is disabled)
    * Set to `True` to allow users to register new accounts.

* **ALLOW_PUBLISHING_NEW_PACKAGES (boolean):**
    * Controls whether publishing entirely new packages is allowed.
    * **Default:** `True` (Publishing new packages is allowed)
    * Set to `False` to restrict users from publishing new packages.

* **ALLOW_PUBLISHING_NEW_RELEASES (boolean):**
    * Controls whether publishing new versions of existing packages is allowed.
    * **Default:** `True` (Publishing new releases is allowed)
    * Set to `False` to restrict users from publishing new versions of existing packages.

* **REQUIRE_ADMIN_TO_INSTALL (boolean):**
    * Controls whether only admins can install packages.
    * **Default:** `False` (Anyone can install packages)
    * Set to `True` to require admin privileges for package installation.

* **REQUIRE_ADMIN_TO_PUBLISH (boolean):**
    * Controls whether only admins can publish packages.
    * **Default:** `True` (Only admins can publish packages)
    * Set to `False` to allow non-admin users to publish packages.

* **REQUIRE_LOGIN_TO_INSTALL (boolean):**
    * Controls whether users need to be logged in to install packages.
    * **Default:** `False` (Users do not need to be logged in to install packages)
    * Set to `True` to require users to be logged in before installing packages.

* **SECRET_KEY (string):**
    * A secret key used for cryptographic functions in Flask applications.
    * **Important:** This key should be a random and unguessable string.
    * **Default:** `'changeme'` (Placeholder value, you must replace this with a strong secret key)
    * **Never expose the secret key in your code or configuration files.**

* **SQLALCHEMY_DATABASE_URI (string):**
    * Defines the connection string for the SQLAlchemy database used by the application.
    * The exact format of the connection string depends on the database type you are using (e.g., SQLite, PostgreSQL, MySQL).
    * **Default:** `'sqlite:///flyingdiskrepo.db'` (Connection string for a SQLite database named `flyingdiskrepo.db`)
    * You may need to modify this value to connect to a different database or database type.

## Routes

**User Authentication**

* **/register (POST)**
    * Requires server to allow registration (`ALLOW_REGISTRATION = True`)
    * Request body format: JSON
        * `username`: Username (string, 8-20 characters, alphanumeric only)
        * `mail`: Email address (string, valid email format)
        * `password`: Password (string, 8-20 characters)
    * Response:
        * 201 Created: User created successfully
        * 400 Bad Request:
            * Username does not meet requirements
            * Email address is invalid
            * Password does not meet requirements
        * 403 Forbidden: Registration is disabled on the server

* **/login (POST)**
    * Requires server to allow login (`ALLOW_LOGIN = True`)
    * Request body format: JSON
        * `username`: Username (string)
        * `password`: Password (string)
    * Response:
        * 200 OK: Login successful
        * 401 Unauthorized: Invalid credentials
        * 403 Forbidden: Login is disabled on the server

* **/logout (GET)**
    * Requires user to be logged in
    * Response:
        * 200 OK: Successfully logged out

* **/userinfo (GET)**
    * Requires user to be logged in
    * Returns information about the current user
    * Response: JSON object containing user data (id, username, email)

* **/userinfo/<id> (GET)**
    * Returns information about a user by ID
    * Response:
        * 200 OK: JSON object containing user data (id, username, email)
        * 404 Not Found: User with specified ID not found

**Package Management**

* **/packages/<package>/<package_version>/<filename> (GET)**
    * Requires server to allow installation (`ALLOW_INSTALLATION = True`)
    * Requires user to be logged in, or admin if `REQUIRE_LOGIN_TO_INSTALL = True` or `REQUIRE_ADMIN_TO_INSTALL = True` is set
    * Downloads a specific file from a published package
    * Response:
        * File data if successful
        * 403 Forbidden: Installation is disabled or user does not have permission
    
* **/packages/<package>/<package_version>.json (GET)**
    * Returns information about a specific package version
    * Response:
        * 200 OK: JSON object containing package data (id, name, description, version, dependencies, files)
        * 404 Not Found: Package or version not found

* **/packages/<package>/latest.json (GET)**
    * Returns information about the latest version of a package
    * Response:
        * 200 OK: JSON object containing package data (id, name, description, version, dependencies, files)
        * 404 Not Found: Package not found

* **/publish (POST)**
    * Requires user to be logged in
    * Uploads a new package or updates an existing one
    * Request body format: multipart/form-data
        * `json`: Package information in JSON format (package, name, shortDescription, description, version) - optional if updating
        * `file`: Package file(s)
    * Response:
        * 200 OK: Package published successfully
        * 400 Bad Request:
            * Invalid package name or version format
            * Version already exists for the package
        * 401 Unauthorized: User is not the owner of the package or not an admin
        * 403 Forbidden:
            * Publishing new packages or new releases is disabled
            * User is not an admin and `REQUIRE_ADMIN_TO_PUBLISH` is set
