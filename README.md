<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://public.ksc.nasa.gov/partnerships/capabilities-and-testing/testing-and-labs/microgravity-simulation-support-facility/">
    <img src="images/NASA_logo.svg" alt="Logo" width="100" height="100">
  </a>
</div>

## Overview

<div align="center">
  <img src="images/example.png" alt="example" style="max-width: 100%; height: auto;">
</div>

This is a computer model that evaluates the efficacy of microgravity simulation devices.

## Built With

[![Python][python-logo]](https://www.python.org/)

[python-logo]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white

## Usage

1. Install the necessary dependencies by running:

   ```bash
   pip install -r requirements.txt
   ```

2. Open the graphical user interface (GUI) by running:

   ```bash
   python gui.py
   ```

   or, if you prefer to create an executable file, you can do so by running:

   ```bash
   python -m PyInstaller executable.spec
   ```

   After creating the executable file, you can run it directly from the output directory (usually `dist/`).

## Acknowledgments

This project was inspired by:

Clary JL, France CS, Lind K, Shi R, Alexander JS, Richards JT, Scott RS, Wang J, Lu X-H, and Harrison L (2022), Development of an inexpensive 3D clinostat and comparison with other microgravity simulators using Mycobacterium marinum. _Front. Space Technol._ 3:1032610. [doi: 10.3389/frspt.2022.1032610](https://doi.org/10.3389/frspt.2022.1032610)
