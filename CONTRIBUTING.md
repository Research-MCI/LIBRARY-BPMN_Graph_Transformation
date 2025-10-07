# Contributing to BPMN Graph Transformation Library

Thank you for considering contributing to this project! 🎉

---

## 🚀 How to Contribute

### 1. Fork the Project on GitHub
Visit the [GitHub repository](https://github.com/Research-MCI/LIBRARY-BPMN_Graph_Transformation/) and click **Fork**.

### 2. Clone Your Fork
```bash
git clone https://github.com/Research-MCI/LIBRARY-BPMN_Graph_Transformation.git
cd LIBRARY-BPMN_Graph_Transformation
```

### 3. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 4. Make Your Changes
- Follow PEP 8 coding standards
- Add tests for new features
- Update documentation if needed
- Ensure all tests pass:
  ```bash
  pytest tests/
  ```

### 5. Commit Your Changes
```bash
git add .
git commit -m "Add: Brief description of your changes"
```

Use conventional commit messages:
- `Add:` for new features
- `Fix:` for bug fixes
- `Docs:` for documentation
- `Test:` for testing
- `Refactor:` for code refactoring

### 6. Push to GitHub
```bash
git push origin feature/your-feature-name
```

### 7. Create a Pull Request
1. Go to your fork on GitHub
2. Click **Pull Request**
3. Select your branch
4. Fill in the description
5. Submit for review

**Note**: Changes merged to the main branch are automatically synchronized to our internal GitLab server for CI/CD pipelines (testing, PyPI publishing).

---

## 🐛 Reporting Bugs

Please report bugs via [GitHub Issues](https://github.com/Research-MCI/LIBRARY-BPMN_Graph_Transformation/issues).

**Include**:
- Python version
- Operating system
- Steps to reproduce
- Expected vs. actual behavior
- Sample BPMN file (if applicable)

---

## 💡 Suggesting Features

Feature requests are welcome! Please:
1. Check existing issues first on [GitHub Issues](https://github.com/Research-MCI/LIBRARY-BPMN_Graph_Transformation/issues)
2. Open a new issue with the "Feature Request" label
3. Describe the use case
4. Explain the expected behavior

---

## 📝 Code Style

This project follows:
- **PEP 8** for Python code
- **Black** for auto-formatting
- **flake8** for linting
- **mypy** for type checking

Run before committing:
```bash
black src/
flake8 src/
mypy src/
```

---

## 🧪 Testing

All contributions must include tests:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_validators.py

# Run with coverage
pytest --cov=bpmn_neo4j tests/
```

---

## 📚 Documentation

If you add new features:
1. Update docstrings in the code
2. Update README.md
3. Add examples if needed
4. Consider adding usage examples to the repository

---

## 🙏 Thank You!

Every contribution helps make this library better for the research community.

**Questions?** Contact us at 6025241065@student.its.ac.id or open an issue on GitHub.

---

**Made with ❤️ by IIM Lab, Institut Teknologi Sepuluh Nopember**