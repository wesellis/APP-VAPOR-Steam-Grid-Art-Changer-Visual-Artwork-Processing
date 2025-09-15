# Security Policy

## 🔒 **Supported Versions**

We actively support the following versions of VAPOR with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | ✅ Active support  |
| 1.x.x   | ❌ End of life     |

## 🛡️ **Security Considerations**

### **API Key Security**
- **Never commit API keys** to version control
- Store API keys securely in profile files
- Use environment variables for development
- Rotate API keys if compromised

### **Network Security**
- All API communications use HTTPS
- Certificate validation is enforced
- Request timeouts prevent hanging connections
- Rate limiting respects API guidelines

### **File System Security**
- Files are stored in appropriate user directories
- No system-wide file modifications
- Proper file permissions on created files
- Temporary files are cleaned up

## 🚨 **Reporting a Vulnerability**

If you discover a security vulnerability in VAPOR, please report it responsibly:

### **Private Reporting (Preferred)**
1. **Email**: Send details to [wes@wesellis.com](mailto:wes@wesellis.com)
2. **Subject**: `[SECURITY] VAPOR Vulnerability Report`
3. **Include**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact assessment
   - Suggested fix (if known)

### **What to Expect**
- **Initial Response**: Within 48 hours
- **Assessment**: 5-7 business days
- **Fix Timeline**: Varies by severity
  - Critical: 1-3 days
  - High: 1-2 weeks  
  - Medium: 2-4 weeks
  - Low: Next release cycle

### **Disclosure Policy**
- We follow **responsible disclosure**
- Security fixes are released before public disclosure
- Credit given to reporters (if desired)
- Coordinated disclosure timeline agreed upon

## 🔍 **Security Audit Areas**

### **High Priority**
- API key storage and transmission
- Network communication security
- File system access permissions
- Input validation and sanitization

### **Medium Priority**
- Error message information disclosure
- Logging sensitive information
- Dependency vulnerability scanning
- Build process security

## 🛠️ **Security Best Practices for Users**

### **API Key Management**
- Generate unique API keys for VAPOR
- Don't share API keys with others
- Revoke unused or old API keys
- Monitor API key usage in provider dashboards

### **Safe Installation**
- Download VAPOR only from official sources
- Verify checksums when available
- Run with standard user permissions
- Keep VAPOR updated to latest version

### **Network Security**
- Use trusted networks when possible
- Consider VPN for public Wi-Fi usage
- Monitor network traffic if concerned
- Report suspicious behavior

## 📋 **Known Security Considerations**

### **Current Limitations**
- Profile files store API keys in plain text locally
- No built-in encryption for cached data
- Network traffic is not encrypted beyond HTTPS
- No user authentication or access control

### **Mitigation Strategies**
- Store profiles in user-only accessible directories
- Clear cache regularly if using shared computers
- Use dedicated API keys for VAPOR only
- Consider file system encryption for sensitive environments

## 🔄 **Security Update Process**

### **For Critical Vulnerabilities**
1. Immediate patch development
2. Emergency release within 24-72 hours
3. Public advisory with minimal details
4. Full disclosure after user update period

### **For Non-Critical Issues**
1. Include in next scheduled release
2. Document in changelog
3. Update security documentation
4. Review related code areas

## 📞 **Contact Information**

### **Security Team**
- **Primary**: Wesley Ellis - [wes@wesellis.com](mailto:wes@wesellis.com)
- **GitHub**: [@wesellis](https://github.com/wesellis)

### **Response Languages**
- English (primary)

### **PGP/GPG**
*PGP key available upon request for sensitive communications*

## 🏆 **Security Hall of Fame**

*Recognition for security researchers who help improve VAPOR's security:*

*None yet - be the first to help secure VAPOR!*

## 📝 **Security Changelog**

### **Version 2.0.1**
- Enhanced input validation for API responses
- Improved error handling to prevent information disclosure
- Added request timeout limits
- Strengthened file path validation

### **Version 2.0.0**
- Initial security baseline established
- HTTPS enforcement for all API calls
- Secure API key storage implementation
- Professional directory structure for data storage

---

## 🙏 **Thank You**

We appreciate the security research community's efforts to keep VAPOR safe for all users. Your responsible disclosure helps protect the gaming community.

**Found a security issue? Please report it privately to [wes@wesellis.com](mailto:wes@wesellis.com)**

---

*Last updated: May 30, 2025*