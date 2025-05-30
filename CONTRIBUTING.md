# Contributing to VAPOR 🎮

Thank you for your interest in contributing to VAPOR! This document provides guidelines and information for contributors.

## 🚀 **Quick Start for Contributors**

### **Prerequisites**
- Python 3.8+ installed
- Git for version control
- Basic familiarity with Python and Tkinter
- Steam account for testing

### **Development Setup**
```bash
# Clone the repository
git clone https://github.com/wesellis/VAPOR.git
cd VAPOR

# Install dependencies
pip install -r requirements.txt

# Run VAPOR in development mode
cd src
python main.py
```

## 🎯 **Ways to Contribute**

### **🐛 Bug Reports**
Found a bug? Help us fix it!

**Before reporting:**
- Search existing issues to avoid duplicates
- Test with the latest release
- Gather system information

**Include in your report:**
- Operating system and version
- Python version (if running from source)
- Steam installation details
- Clear steps to reproduce
- Expected vs actual behavior
- Screenshots or error logs

### **💡 Feature Requests**
Have an idea for VAPOR? We'd love to hear it!

**Good feature requests include:**
- Clear description of the problem it solves
- Proposed solution or approach
- Use cases and benefits
- Mockups or examples (if applicable)

### **📖 Documentation Improvements**
Help make VAPOR more accessible:
- Fix typos or unclear instructions
- Add examples and tutorials
- Translate documentation
- Improve API documentation

### **🧪 Testing**
Help ensure VAPOR works everywhere:
- Test on different operating systems
- Test with various Steam configurations
- Verify new features work as expected
- Performance testing with large libraries

### **💻 Code Contributions**
Ready to code? Here's what we need:

**High Priority Areas:**
- Performance optimizations
- Steam Deck UI improvements
- Cross-platform compatibility
- Error handling enhancements
- Caching improvements

**Medium Priority:**
- New artwork sources
- UI/UX improvements
- Additional image formats
- Logging enhancements

## 🔧 **Development Guidelines**

### **Code Style**
- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings for functions and classes
- Keep functions focused and under 50 lines when possible
- Use type hints where appropriate

### **Project Structure**
```
VAPOR/
├── src/                    # Main application code
│   ├── main.py            # Application entry point
│   ├── models/            # Data models
│   ├── ui/                # User interface modules
│   └── utilities/         # Helper functions
├── assets/                # Images and resources
├── docs/                  # Documentation
└── tests/                 # Test files (coming soon)
```

### **Coding Best Practices**
- Write self-documenting code with clear variable names
- Handle errors gracefully with user-friendly messages
- Use logging instead of print statements for debugging
- Follow the existing code patterns and architecture
- Add comments for complex logic

### **Testing Guidelines**
- Test on Windows, Linux, and Steam Deck when possible
- Verify API key validation works correctly
- Test with different Steam library sizes
- Check memory usage during long operations
- Validate cross-platform file path handling

## 📝 **Pull Request Process**

### **Before Submitting**
1. **Fork** the repository and create a feature branch
2. **Test** your changes thoroughly
3. **Document** new features or API changes
4. **Follow** the code style guidelines
5. **Update** relevant documentation

### **Pull Request Checklist**
- [ ] Code follows project style guidelines
- [ ] Changes are tested on at least one platform
- [ ] Documentation is updated if needed
- [ ] Commit messages are clear and descriptive
- [ ] No sensitive information (API keys) in code
- [ ] Screenshots included for UI changes

### **PR Title Format**
Use descriptive titles with prefixes:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `perf:` for performance improvements
- `refactor:` for code refactoring

**Examples:**
- `feat: Add batch artwork processing for faster auto-enhancement`
- `fix: Resolve Steam Deck touch input issues in artwork selection`
- `docs: Update installation guide for Linux users`

## 🎮 **Platform-Specific Considerations**

### **Windows Development**
- Test with both Steam and portable Steam installations
- Verify Windows Defender compatibility
- Check AppData directory handling
- Test with different Windows versions (10, 11)

### **Linux Development**
- Test on major distributions (Ubuntu, Fedora, Arch)
- Verify XDG Base Directory compliance
- Check desktop integration features
- Test with different Steam installation methods

### **Steam Deck Development**
- Test in both Desktop and Gaming modes
- Verify touch input responsiveness
- Check screen scaling and layout
- Test with on-screen keyboard

## 🚦 **Issue Labels**

We use labels to organize and prioritize issues:

**Priority:**
- `priority-high` - Critical bugs or important features
- `priority-medium` - Standard improvements
- `priority-low` - Nice-to-have enhancements

**Type:**
- `bug` - Something isn't working
- `feature` - New functionality request
- `enhancement` - Improvement to existing feature
- `documentation` - Documentation needs improvement

**Platform:**
- `windows` - Windows-specific issue
- `linux` - Linux-specific issue
- `steam-deck` - Steam Deck-specific issue
- `cross-platform` - Affects multiple platforms

**Difficulty:**
- `good-first-issue` - Good for newcomers
- `help-wanted` - Extra attention needed
- `advanced` - Requires deep knowledge

## 💬 **Communication**

### **Getting Help**
- **GitHub Discussions** - General questions and ideas
- **GitHub Issues** - Bug reports and feature requests
- **Email** - Direct contact: wes@wesellis.com

### **Code of Conduct**
- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers learn and contribute
- Follow GitHub's community guidelines

## 🎉 **Recognition**

Contributors are recognized in several ways:
- Listed in repository contributors
- Mentioned in release notes for significant contributions
- Added to acknowledgments in documentation
- Potential collaboration on future projects

## 📚 **Resources**

### **Learning Resources**
- [Python Official Documentation](https://docs.python.org/3/)
- [Tkinter Tutorial](https://docs.python.org/3/library/tkinter.html)
- [Steam Web API Documentation](https://steamcommunity.com/dev)
- [SteamGridDB API Documentation](https://www.steamgriddb.com/api/v2)

### **VAPOR-Specific Resources**
- [Project Architecture Overview](docs/ARCHITECTURE.md) (coming soon)
- [API Integration Guide](docs/API_INTEGRATION.md) (coming soon)
- [Performance Optimization Guide](docs/PERFORMANCE.md) (coming soon)

---

## 🙏 **Thank You!**

Every contribution, no matter how small, helps make VAPOR better for the entire gaming community. Whether you're fixing a typo, reporting a bug, or implementing a major feature, your help is appreciated!

**Ready to contribute? [Fork the repository](../../fork) and start coding!** 🚀

---

*For questions about contributing, reach out via [GitHub Discussions](../../discussions) or email [wes@wesellis.com](mailto:wes@wesellis.com)*