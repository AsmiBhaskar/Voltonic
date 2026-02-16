# Virtual Environment Setup

## ✅ Virtual Environment Created

Your Python virtual environment `.venv` has been successfully created!

## 🚀 How to Use

### Activate the Virtual Environment

**macOS/Linux:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.venv\Scripts\activate
```

You'll see `(.venv)` in your terminal prompt when activated.

### Install Project Dependencies

After activating the virtual environment:

```bash
pip install -r requirements.txt
```

### Deactivate

When you're done working:

```bash
deactivate
```

## 📦 What's Installed

The virtual environment includes:
- Python 3.12 (isolated from system Python)
- pip (package manager)
- setuptools (package building tools)

## ⚙️ Quick Commands

```bash
# Activate venv
source .venv/bin/activate

# Install all dependencies
pip install -r requirements.txt

# Run the application
python run.py

# Run tests
python test_api_endpoints.py

# Deactivate when done
deactivate
```

## 🎯 Benefits

- ✅ Isolated Python environment
- ✅ Prevents dependency conflicts
- ✅ Easy to recreate on other machines
- ✅ Keeps system Python clean
- ✅ Already added to `.gitignore`

## 🔄 Dashboard Setup

For the React dashboard:

```bash
# Install dashboard dependencies
cd dashboard
npm install

# Run dashboard (with backend running)
npm start
```

## 📝 Notes

- The `.venv` folder is excluded from git (already in `.gitignore`)
- Always activate the venv before running Python commands
- Each terminal session needs activation
- The venv is project-specific

## 🆘 Troubleshooting

**Virtual environment not activating?**
```bash
# Recreate it
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
```

**Missing dependencies?**
```bash
pip install -r requirements.txt
```

**Wrong Python version?**
```bash
python --version  # Check version
which python      # Check location (should show .venv/bin/python)
```

---

Happy coding! 🚀
