# Getting started with FastAPI

FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints.

Install FastAPI with all optional dependencies, including [uvicorn](https://www.uvicorn.org/) that is the web server.

```sh
pip install "fastapi[all]"
```

### Use Python types for validation and autocompletition

[Python types tutorial](https://fastapi.tiangolo.com/python-types/)

### Basic tutorial

[FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/)

Run the code

```sh
uvicorn src.main:app --reload
```

Using `--reload` enable run the code automatically after each change.

### Generate automatic docs - Swagger UI

```
http://127.0.0.1:8000/docs
```