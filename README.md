# User Authentication App

Welcome to the User Authentication App, a secure and efficient way to manage user logins and registrations. Our application is designed to provide developers and businesses with a straightforward approach to implementing authentication mechanisms, ensuring that user data is handled securely and efficiently.

## Features

- **Secure Login and Registration**: Utilize robust encryption for passwords and sensitive data.
- **Session Management**: Manage user sessions to keep users logged in securely.
- **Multi-Factor Authentication (MFA)**: Enhance security by adding multi-factor authentication options.
- **Password Recovery**: Offer a secure process for users to recover forgotten passwords.
- **User Management Dashboard**: Admins can manage user accounts, including creation, updates, and deletion.

## Getting Started

### Prerequisites

- Python 3.10
- PostgreSql latest

### Installation

1. Clone the repository:
```bash
git clone https://github.com/dominic-source/User_Authentication.git
```

2. Navigate to the project directory:
```bash
cd user-authentication-app
```

3. Install dependencies:
```bash
    pip install -r requirements.txt
```

### Running the Application

1. Start the postgresql service on your machine.
2. Run the application:
```bash
    sudo service postgresql start
```
*Note: Ensure that postgresql is installed on your system*
*Note: Ensure you setup the username, password and other permissions for the user in the postgresql*

3. Run the app
```bash
python app.py
```
4. The application will be available at `http://localhost:5000`.

5. To run unittest
`python -m unittest tests.auth_spec`

## Usage

- **Register a New User**: Navigate to `/register` to create a new user account.
- **Login**: Go to `/login` and enter your credentials to access the application.
- **Admin Dashboard**: Accessible at `/admin` for managing user accounts (admin rights required).
