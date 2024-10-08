# FrescomAPIs

FrescomAPIs is a FastAPI-based project that provides a RESTful API for managing customers and purchase orders.

## Table of Contents

- [Getting Started](#getting-started)
- [Installing Oracle Instant Client](#installing-oracle-instant-client)
- [Database Configuration](#database-configuration)
- [Running the application](#runing-the-application)
- [Dependencies](#dependencies)

## Getting Started

To run the application, follow these steps:

1. Clone the repository:

   ```
   git clone https://github.com/aiwoox/frescomAPIs.git
   cd frescomAPIs
   ```

2. Create a virtual environment:

   ```
   python3 -m venv venv
   ```

3. Activate the virtual environment:

   - For Windows:
     ```
     venv\Scripts\activate
     ```
   - For macOS and Linux:
     ```
     source venv/bin/activate
     ```

4. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

## Installing Oracle Instant Client

### For Windows:

1. Download Oracle Instant Client Basic Package (ZIP) for Windows from the [Oracle website](https://www.oracle.com/database/technologies/instant-client/winx64-64-downloads.html).
2. Extract the ZIP file.
3. Place the `instantclient_23_4` (version might change in the future) folder in the root of your project.
4. In `app/database.py` file, in line-9, update the version code of 'instance*client'. `(thick_mode = {"lib_dir": "./instantclient*[NEW_VERSION_CODE]"})`

### For macOS:

1. Download Oracle Instant Client Basic Package (DMG) for macOS from the [Oracle website](https://www.oracle.com/database/technologies/instant-client/macos-arm64-downloads.html).
2. Mount the DMG file and run the install script. [Follow the steps given in oracle website](https://www.oracle.com/database/technologies/instant-client/macos-arm64-downloads.html).
3. After installation, navigate to the installation directory (usually `/Users/username/Downloads/`).
4. Copy the `instantclient_23_3` (version might change in the future) folder to the root of your project.
5. In `app/database.py` file, in line-9, update the version code of 'instance*client'. `(thick_mode = {"lib_dir": "./instantclient*[NEW_VERSION_CODE]"})`

## Database Configuration

The application uses a database to store customer and purchase order data. You'll need to create a `.env` file with the following variables:

- `DATABASE_USERNAME`: Your database username
- `DATABASE_PASSWORD`: Your database password
- `DATABASE_HOST`: Your database host
- `DATABASE_PORT`: Your database port
- `DATABASE_SERVICE_NAME`: Your database service name
- `DATABASE_PROVIDER`: Your database provider (e.g., oracle)
- `DATABASE_DRIVER`: Your database driver (e.g., oracledb)

## Running the application:

```
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Dependencies

The project dependencies are listed in the `requirements.txt` file. You can install them using pip after activating your virtual environment:

```
pip install -r requirements.txt
```
