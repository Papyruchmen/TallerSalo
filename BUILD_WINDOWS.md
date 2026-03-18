# Instrucciones para generar ejecutable Windows

## Opción 1: En Windows (recomendado)

1. Instalar Python 3.12 para Windows desde: https://www.python.org/downloads/
2. Abrir cmd y ejecutar:

```cmd
cd carpeta_del_proyecto

pip install -r requirements.txt
pip install pyinstaller

pyinstaller taller.spec --clean
```

3. El ejecutable estará en `dist\TallerMecanico\`

## Opción 2: Usar GitHub Actions (automático)

Sube el proyecto a GitHub y crea un workflow en `.github/workflows/build.yml`:

```yaml
name: Build Windows EXE

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: pip install pyinstaller
      - run: pyinstaller taller.spec --clean
      - uses: actions/upload-artifact@v4
        with:
          name: TallerMecanico
          path: dist/TallerMecanico/
```

## Archivos necesarios para compilar

- main.py (código principal)
- database.py (manejo de base de datos)
- report.py (generación de PDFs)
- styles.qss (estilos visuales)
- taller.db (base de datos SQLite)
- taller.spec (configuración de PyInstaller)
- requirements.txt (dependencias)
