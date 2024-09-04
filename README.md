# polymarket_copy_trader
An automated bot for tailing the trades of the top ranked wallets on Polymarket monthly

- Simple Usage: enter your Polymarket Proxy Wallet Address, run main.py
    - Note: You will need to have previously created API Keys and set allowances for your proxy wallet address

# Project Setup

This guide will help you set up the project environment using the provided `requirements.txt` file.

## Prerequisites

- Python installed on your machine.
- A virtual environment (recommended) to keep dependencies isolated.

## Setting Up Your Environment

### 1. Clone the Repository

Clone the repository to your local machine using:

```bash
git clone https://github.com/Joshbazz/polymarket_copy_trader.git
cd polymarket_copy_trader
```

### 2. Create a Virtual Environment

Create a virtual environment to keep your dependencies isolated:

```bash
python -m venv venv
### This will create a directory named venv in your project folder.
```
### 3. Activate the Virtual Environment

Activate the virtual environment using the following command:

On Windows:
```bash
venv\Scripts\activate
```
On macOS/Linux:
```bash
source venv/bin/activate
```

### 4. Install the Required Dependencies

Once your virtual environment is activated, install the required dependencies listed in requirements.txt:

``` bash
pip install -r requirements.txt
## This command will install all the packages and their respective versions specified in the requirements.txt file.
```

### 5. Deactivate the Virtual Environment

When you're done working on the project, you can deactivate the virtual environment using:

``` bash
deactivate
```

### Updating Dependencies

If you add new packages or update existing ones, make sure to update the requirements.txt file with:
```bash
pip freeze > requirements.txt
## This will overwrite the old requirements.txt with the current environment's dependencies.
Troubleshooting
```

Virtual Environment Not Activating: Ensure you are using the correct activation command for your operating system.

Permission Errors: If you encounter permission errors while installing packages, ensure your terminal or command prompt has the necessary permissions or try running it as an administrator (Windows) or with sudo (macOS/Linux).

Dependency Conflicts: If dependencies conflict during installation, consider updating your virtual environment or reviewing the required package versions.