# Yaksha Lang Website & Docs Site

* Documentation directories are `yaksha_docs`, `yaksha_lib_docs`, `yaksha_proposals` and `yaksha_tutorials`

Require `css-minify` and `html-minifier` in path.

* STEP 01: Install node.js
* STEP 02:
```
npm install -g css-minify
npm install -g html-minifier
```

Uses Python to build the documentation.
* STEP 01: Create virtual environment
```
python -m venv .venv
```
* STEP 02: Activate virtual environment
* STEP 03: Install dependencies
```
pip install -r requirements.txt
```
* STEP 04: Run the build.py
```
python build.py
```
