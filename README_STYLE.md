# Code Style, Import Sorting, and Type Checking

## Code Formatting: Black
- This project uses [Black](https://black.readthedocs.io/) for automatic code formatting.
- To format all code:
  ```sh
  black src/
  ```
- Black enforces a consistent, modern Python style. No configuration is needed.

## Import Sorting: isort
- [isort](https://pycqa.github.io/isort/) is used to automatically sort imports.
- To sort imports:
  ```sh
  isort src/
  ```
- isort works well with Black and keeps imports tidy and grouped.

## Type Checking: mypy
- [mypy](http://mypy-lang.org/) is used for static type checking.
- To check types:
  ```sh
  mypy src/
  ```
- If you see errors about missing stubs, install them (example):
  ```sh
  pip install types-requests types-colorama types-tqdm
  ```
- All public functions should have type annotations. mypy will warn if any are missing or incorrect.

## mypy configuration
- This project uses a `mypy.ini` file to ignore missing imports for local modules:
  ```ini
  [mypy]
  ignore_missing_imports = True
  ```
- If you encounter a false positive from mypy (e.g., for a third-party library or a known-safe call), you can suppress it with `# type: ignore` at the end of the line.

## Best Practices
- Run `black`, `isort`, and `mypy` before every commit or as a pre-commit hook.
- Keep type annotations up to date as you change code.
- Fix all warnings and errors from these tools for a robust, maintainable codebase.

## Example Workflow
```sh
black src/
isort src/
mypy src/
```

Add these steps to your CI for continuous enforcement.
