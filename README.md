# Keycloak Labs

A comprehensive collection of hands-on security labs focused on web application vulnerabilities, authentication mechanisms, and secure development practices. This repository serves as an educational platform for learning about common security flaws and their remediation strategies.

## 🎯 Purpose

This repository is designed to help developers, security professionals, and students understand:

- **Common web vulnerabilities** and their exploitation techniques
- **Secure coding practices** and defensive programming
- **Authentication and authorization** security challenges
- **Real-world attack scenarios** and mitigation strategies

## 📚 Available Labs

### 🔐 Session Fixation Lab

**Location:** `session_fixation_lab/`

Demonstrates the session fixation vulnerability where attackers can force users to use specific session IDs, enabling session hijacking after authentication.

**Key Learning Points:**

- Session fixation attack vectors
- Secure session management practices
- Session ID regeneration techniques
- User-Agent binding and validation

**Files:**

- `vulnerable_app.py` - Intentionally vulnerable Flask application
- `patched_app.py` - Secure implementation with fixes
- `README.md` - Detailed lab instructions and explanations

## 🛠️ Getting Started

### Prerequisites

- **Python 3.8+** with pip
- **Basic understanding** of web development concepts
- **Familiarity** with HTTP, cookies, and session management

### Quick Start

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Guy-Ghis/keycloak-labs.git
   cd keycloak-labs
   ```

2. **Navigate to a specific lab:**

   ```bash
   cd session_fixation_lab
   ```

3. **Follow the lab-specific instructions** in each lab's README.md file

## 🏗️ Repository Structure

```plaintext
keycloak-labs/
├── README.md                    # This file - repository overview
├── session_fixation_lab/        # Session fixation vulnerability lab
│   ├── vulnerable_app.py       # Intentionally vulnerable application
│   ├── patched_app.py          # Secure implementation
│   ├── venv/                   # Python virtual environment
│   └── README.md               # Lab-specific instructions
└── [future_labs]/              # Additional labs will be added here
```

## 🎓 Learning Approach

Each lab follows a structured learning approach:

1. **Theory** - Understanding the vulnerability and attack vectors
2. **Exploitation** - Hands-on practice with vulnerable applications
3. **Analysis** - Examining the root causes and security implications
4. **Remediation** - Learning secure implementation practices
5. **Validation** - Testing the effectiveness of security fixes

## 🔒 Security Notice

⚠️ **Important:** All vulnerable applications in this repository are:

- **Intentionally insecure** for educational purposes
- **Designed for isolated testing** environments
- **Never intended** for production use
- **Should only be run** in controlled, isolated environments

## 🚀 Contributing

We welcome contributions to expand this educational platform:

- **New vulnerability labs** following the established pattern
- **Improvements** to existing labs and documentation
- **Bug fixes** and security enhancements
- **Additional learning resources** and references

### Lab Contribution Guidelines

When adding new labs, please include:

1. **Clear vulnerability description** and attack vectors
2. **Vulnerable implementation** demonstrating the flaw
3. **Secure implementation** with proper fixes
4. **Comprehensive README** with setup and testing instructions
5. **Learning objectives** and key takeaways
6. **Additional resources** for further study

## 📖 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [Flask Security Documentation](https://flask.palletsprojects.com/en/2.3.x/security/)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Support

For questions, issues, or contributions:

1. **Check existing issues** in the repository
2. **Create a new issue** for bugs or feature requests
3. **Submit pull requests** for improvements
4. **Follow security best practices** when reporting vulnerabilities
