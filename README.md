<div align="center">
  <a href="https://public.ksc.nasa.gov/partnerships/capabilities-and-testing/testing-and-labs/microgravity-simulation-support-facility/">
    <img src="images/NASA_logo.svg" alt="Logo" width="100" height="100">
  </a>
</div>

## Introduction

<div align="center">
  <img src="images/example.png" alt="example" style="max-width: 100%; height: auto;">
</div>

The Microgravity Simulation Support Facility (MSSF) at the National Aeronautics and Space Administration (NASA) John F. Kennedy Space Center (KSC) contains an array of devices that negate the directional influence of gravity to simulate microgravity. The MSSF has created a graphical user interface (GUI) with Python for computing and visualizing the accelerations felt by a biospecimen when rotating in these devices to better enable scientists to interpret data and validate that a microgravity environment is being achieved. The application has two modes: theoretical and experimental. The efficacy of a given operating condition in simulating microgravity is evaluated using a kinematics model for theoretical mode or data from an onboard accelerometer for experimental mode.

## Built With

[![Python][python-logo]](https://www.python.org/)

[python-logo]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white

## Getting Started

Ensure the following are installed:

- [Python](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)

Open a terminal, and run the following commands:

1. Clone the repository.

   ```bash
   git clone https://github.com/edwardromero25/Kinematics-Model.git
   ```

2. Navigate to the project directory.

   ```bash
   cd Kinematics-Model
   ```

3. Install dependencies.

   ```bash
   pip install -r requirements.txt
   ```

4. Launch the application.

   ```bash
   python gui.py
   ```

## References

1. Kim, Y. J., Jeong, A. J., Kim, M., Lee, C., Ye, S.-K., and Kim, S. (2017). Time-averaged simulated microgravity (taSMG) inhibits proliferation of lymphoma cells, L-540 and HDLM-2, using a 3D clinostat. _Biomed. Eng. OnLine_, 16, 48. [doi:10.1186/s12938-017-0337-8](https://doi.org/10.1186/s12938-017-0337-8)

2. Clary, J. L., France, C. S., Lind, K., Shi, R., Alexander, J. S., Richards, J. T., Scott, R. S., Wang, J., Lu, X.-H., and Harrison, L. (2022). Development of an inexpensive 3D clinostat and comparison with other microgravity simulators using _Mycobacterium marinum_. _Front. Space Technol._, 3, 1032610. [doi:10.3389/frspt.2022.1032610](https://doi.org/10.3389/frspt.2022.1032610)
