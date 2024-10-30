
## Set up

- Create virtual environment once: `python -m venv $env:HomeDrive$env:HomePath\venvs\jane-street`
- Activate virtual environment in PowerShell: `& "$env:HomeDrive$env:HomePath\venvs\jane-street\Scripts\Activate.ps1"`
- `streamlit run app.py`

## Thought process

- 2024 has prime factors 2x2x2x11x23. Say there is a 4-step path, two A=4, one B=11, one C=23, then we already have a solution < 50.
- All possible paths
- All possible series of operations
- Loop over all ABC over operations.
