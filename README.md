# Photovoltaic J-V Curve Analyzer ☀️

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)] (https://pv-jv-analyzer.streamlit.app/)

**Main Dashboard - Batch Processing & Visualization**
<img width="1841" height="930" alt="image" src="https://github.com/user-attachments/assets/eeeb7d85-ee7b-4736-b790-242d07f6d40c" />
**Statistical Analysis & Parameter Extraction**
<img width="1863" height="845" alt="image" src="https://github.com/user-attachments/assets/627acead-2bba-4992-a47b-fe8be75001c0" />


## 📌 Overview
This Streamlit-based web application is designed to automate and standardize the processing of experimental Current-Voltage (J-V) curves for Photovoltaic devices (e.g., DSSCs, Perovskites). It eliminates manual plotting bottlenecks by providing researchers with a rapid, interactive interface to visualize raw `.txt` data, instantly extract key optoelectronic parameters, and generate comprehensive statistical reports.

## 🔬 Scientific Features
*   **Automated Parameter Extraction:** Uses mathematical zero-crossing interpolation to accurately calculate Open-Circuit Voltage ($V_{oc}$), Short-Circuit Current Density ($J_{sc}$), Fill Factor (FF), and Power Conversion Efficiency ($\eta$).
*   **Dark Measurement Integration:** Includes a dedicated mode for dark curve analysis, allowing dynamic threshold configuration to extract Turn-on Voltages.
*   **Smart Grouping & Statistics:** Automatically identifies cell groups via regex parsing of file names and calculates aggregate statistics (Mean, Max Efficiency, Standard Deviation).
*   **Interactive Visualization:** Real-time data filtering and rendering using Plotly.
*   **Advanced Data Export:** Generates `.xlsx` reports complete with raw data, parameter tables, and **natively editable Excel scatter charts** (injected via `xlsxwriter`), streamlining the transition from data acquisition to publication formatting.

## 🛠️ Tech Stack
*   **Language:** Python 3.x
*   **Framework:** Streamlit
*   **Data Processing:** Pandas, NumPy, Regex
*   **Visualization:** Plotly (Interactive Web), XlsxWriter (Native Excel Charts)

## 🚀 Usage
Upload raw measurement files `.txt` directly into the web interface. Configure the active area ($cm^2$) and incident power ($W/cm^2$) in the sidebar to dynamically update the optoelectronic parameters.
