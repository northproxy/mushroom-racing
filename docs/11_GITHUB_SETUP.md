# 11 — GitHub Setup

## 1. Unpack and open the repository

Example on Windows PowerShell:

```powershell
cd R:\_projects
```

Unpack `mushroom-racing-starter.zip` so the project folder is:

```text
R:\_projects\mushroom-racing
```

Then:

```powershell
cd R:\_projects\mushroom-racing
```

## 2. Create a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install:

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Run validation:

```powershell
pytest
```

Expected baseline:

```text
4 passed
```

Run the demo:

```powershell
python scripts\demo_score.py
```

## 3. Initialize Git

```powershell
git init
git branch -M main
git add .
git status
git commit -m "chore: initialize mushroom-racing project"
```

## 4. Create the GitHub repository

Recommended repository name:

```text
mushroom-racing
```

Recommended initial settings:

- Public: yes, when you are ready to show it as a portfolio project;
- Initialize with README: **no** — the repository already has one;
- Add .gitignore: **no**;
- Add license: leave empty for now; decide explicitly later.

## 5. Connect local repository

Replace `<YOUR_GITHUB_USERNAME>`:

```powershell
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/mushroom-racing.git
git push -u origin main
```

## 6. Check GitHub Actions

After the push, open:

```text
GitHub → mushroom-racing → Actions
```

The `tests` workflow should run automatically.

A green workflow is the first reproducible validation milestone.

## 7. Working convention

Use small commits that describe one change.

Examples:

```text
docs: add Austrian geodata source registry
feat: add rainfall rolling-window model
test: add legal exclusion scenarios
feat: calculate slope aspect from DEM
fix: clamp missing weather features safely
```

Avoid commits such as:

```text
update
changes
stuff
final
final2
```

## 8. Branching

For the beginning, keep it simple:

```text
main
```

When MR-1 starts, optional short-lived feature branches can be used:

```text
feature/species-profile
feature/weather-model
feature/geodata-poc
```

Do not introduce complex Git workflows before they solve a real problem.

## 9. First GitHub milestone

Create milestone:

```text
MR-1 — Domain model
```

Suggested issues:

1. Define `SpeciesProfile`
2. Define `ForestSpot`
3. Define `WeatherSnapshot`
4. Define `Observation`
5. Add JSON serialization
6. Add schema validation tests
7. Add sample Steinpilz profile

## 10. Definition of done for MR-1

MR-1 is complete when:

- domain entities are implemented;
- sample fixtures can be loaded;
- tests cover serialization and validation;
- README status is updated;
- roadmap marks MR-1 as complete;
- GitHub Actions is green.
