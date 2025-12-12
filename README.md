# Time-Series-Modeling-of-Moroccan-Unemployment-Rates



# Morocco Unemployment Forecasting

*A Time Series Analysis & Predictive Modeling Project (2006–2025)*

This project analyzes and forecasts unemployment trends in **Morocco** using official quarterly data published by the **High Commission for Planning (HCP)**.
It explores socio-economic disparities, evaluates multiple forecasting models, and provides an interactive web application for visualization and prediction.

---

## Project Objectives

* Analyze historical unemployment trends in Morocco (2006–2025).
* Identify differences across population groups:

  * **Urban vs Rural**
  * **Education levels** (No diploma, Medium, Higher)
  * **Gender**
  * **Age groups**
* Build and compare traditional statistical and deep learning forecasting models.
* Develop an interactive web app enabling users to explore data and generate forecasts up to 2050.

---

##  Dataset Overview

* **Source:** Quarterly employment surveys (HCP – Haut Commissariat au Plan)
* **Period:** 2006 Q1 → 2025 Q4 (79 observations)
* **Coverage:**

  * Areas: *Urban, Rural, National*
  * Education levels: *No diploma, Medium, Higher*
  * Gender: *Male, Female*
  * Age groups: *15–24, 25–34, 35–44, 45+*
* **Quality:** No missing values; minimal preprocessing required.

---

##  Methodology

### 1. **Exploratory Data Analysis (EDA)**

* Visualization of unemployment trends by category
* 4-quarter moving averages
* Trend and seasonality detection
* Stationarity testing (ADF Test)

### 2. **Forecasting Models Tested**

| Model            | Type                  | Strengths                                     |
| ---------------- | --------------------- | --------------------------------------------- |
| **ARIMA**        | Statistical           | Effective for stationary differenced series   |
| **SARIMA**       | Statistical           | Captures quarterly seasonality                |
| **Holt-Winters** | Exponential Smoothing | Models trend + seasonality                    |
| **RNN**          | Deep Learning         | Learns non-linear temporal dependencies       |
| **LSTM**         | Deep Learning         | Handles long-term memory and complex patterns |

---

##  Results & Model Performance

**SARIMA outperformed all other models**, effectively capturing both long-term trends and seasonal patterns.

### Test Set Performance

| Model        | MSE       | RMSE      | MAE       |
| ------------ | --------- | --------- | --------- |
| **SARIMA**   | **0.193** | **0.440** | **0.388** |
| Holt-Winters | 0.309     | 0.556     | 0.444     |
| ARIMA        | 0.902     | 0.950     | 0.870     |
| RNN          | 1.315     | 1.147     | 1.064     |

---

##  Web Application

The project includes an interactive forecasting platform that allows users to:

* Explore historical unemployment data
* Filter by gender, age, education level, and area
* Compare model forecasts
* Generate predictions up to **2050**
* Visualize results with dynamic charts

---

##  Tech Stack

### **Backend**

* Python
* Flask 3.0

### **Data Processing**

* Pandas
* NumPy

### **Modeling**

* statsmodels
* pmdarima
* TensorFlow / Keras

### **Frontend**

* HTML, CSS, JavaScript
* Bootstrap

### **Visualization**

* Matplotlib
* Plotly



##  Future Improvements

* Integrating Prophet for additional comparison
* Deploying the web app on a cloud platform
* Adding real-time updates when new HCP data is released
* Enhancing LSTM and RNN architectures




