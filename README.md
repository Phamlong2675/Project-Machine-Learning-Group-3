# 🌆 Project-Machine-Learning-Group-3-DSEB65B
## 🏙️ Hanoi Temperature Forecasting – Machine Learning I Project

---

## 📖 Overview

This project is part of the **Machine Learning I course**, aiming to **forecast Hanoi temperature** using historical weather data.  
The goal is to build a **complete pipeline**—from data collection to feature engineering, model training, hyperparameter tuning, and finally a **demo application** for end-users.

We leverage both **daily and hourly weather data** to explore how granularity affects temperature forecasting.

---

## 📁 Project Structure

```PROJECT-MACHINE-LEARNING/
│
├── data/ # Raw and processed data used for training and evaluation
│ ├── processed/ # Cleaned and transformed datasets
│ └── raw/ # Original, unprocessed data files
│
├── notebooks/ # Jupyter notebooks for exploration, processing, and modeling
│ ├── Daily data/ # Daily-level data analysis and modeling
│ │ ├── catboost_info/ # Logs or metadata from CatBoost training
│ │ ├── 01-data_understanding_daily.ipynb
│ │ ├── 02-data_processing_daily.ipynb
│ │ └── 03-fe_model_training_onnx_daily.ipynb
│ │
│ ├── Hourly data/ # Hourly-level data analysis and modeling
│ │ ├── 01-data_understanding_hourly.ipynb
│ │ ├── 02-data_processing_hourly.ipynb
│ │ └── 03-fe_model_training_onnx_hourly.ipynb
│ │
│ ├── data/ # Feature-engineered datasets used in notebooks
│ │ └── processed/
│ │ └── feature_engineered/
│ │ ├── X_test_original.csv
│ │ ├── X_train_original.csv
│ │ ├── X_val_original.csv
│ │ ├── y_test.csv
│ │ ├── y_train.csv
│ │ └── y_val.csv
│ │
│ ├── results/ # Output artifacts from model training and evaluation
│ │ ├── figures/ # Visualizations such as plots or charts
│ │ └── models/ # Saved models and metadata
│ │ ├── feature_names.txt
│ │ ├── model_metadata.json
│ │ └── temperature_prediction.onnx
│ │
│ └── Model_retraining.ipynb # Notebook for retraining the model with updated data
│
├── app.py # User Interface (UI) script — web/app front-end to interact with the model
└── README.md # Project overview and documentation


---

## 📊 Project Workflow

1. **Data Collection**
   - Download daily and hourly weather data for Hanoi from **Visual Crossing Weather**.
   - Collect at least **10 years of historical data** for robust forecasting.

2. **Data Understanding**
   - Analyze **33 weather features**, including numerical and categorical.
   - Visualize temperature trends, seasonal patterns, and correlations.

3. **Data Processing**
   - Handle missing values and outliers.
   - Normalize or scale numerical features.
   - Encode categorical/text features appropriately.

4. **Feature Engineering**
   - Transform raw data into **model-ready features**.
   - Create **lag features, rolling statistics, and temporal features**.
   - Predict the **next 5 days’ temperature (daily)** or **next few hours (hourly)**.

5. **Model Training & Hyperparameter Tuning**
   - Train multiple ML models: **CatBoost, Random Forest, XGBoost, LightGBM**.
   - Use **Optuna** for hyperparameter optimization.
   - Track experiments via **ClearML**.
   - Evaluate using **RMSE, MAPE, R²** metrics.

6. **Application UI**
   - Build an interactive demo using **Gradio**.
   - Allow users to input parameters or view predictions.

7. **Model Monitoring & Retraining**
   - Monitor model performance over time.
   - Define retraining schedules to prevent performance degradation.

8. **Hourly Data Forecasting**
   - Repeat the pipeline with **hourly data** for finer-grained predictions.

9. **Deployment with ONNX**
   - Convert the best model to **ONNX** for efficient deployment.
   - Reduce latency and enable cross-platform inference.```

---

## 🛠️ Tools & Technologies

- **Python** – data processing, feature engineering, modeling  
- **Pandas / NumPy / Matplotlib / Plotly** – analysis & visualization  
- **Scikit-learn / CatBoost / XGBoost / LightGBM** – ML modeling  
- **Optuna** – hyperparameter optimization  
- **ClearML** – experiment tracking  
- **Gradio** – demo application  
- **ONNX** – optimized deployment  

---

## 📚 References

- [Visual Crossing Weather](https://www.visualcrossing.com/weather) – Data source  
- [ClearML](https://clear.ml/) – Experiment tracking  
- [Optuna](https://optuna.org/) – Hyperparameter tuning  
- [ONNX](https://onnx.ai/) – Model deployment  

---

## 🚀 Future Development Directions

1. **Integrate Deep Learning**
   - Apply **LSTM** or **Transformer** architectures for sequence prediction.
   - Compare performance with tree-based models.

2. **API Deployment**
   - Serve the prediction pipeline as **FastAPI endpoints**.
   - Enable **real-time or batch predictions**.

3. **Real-Time Data Integration**
   - Stream weather data continuously.
   - Update predictions dynamically for **real-time monitoring**.

4. **Expand Forecasting Scope**
   - Predict additional metrics: **humidity, rainfall, UV index, extreme weather events**.

5. **CI/CD & Monitoring**
   - Implement automated testing, deployment, and performance monitoring for **production-ready systems**.
