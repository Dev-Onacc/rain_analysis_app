import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset (assume the data has already been preprocessed)
@st.cache_data
def load_data():
    # Load the dataset from Excel
    file_path = "mnocc_data-1980-2023.xlsx"
    data = pd.ExcelFile(file_path).parse("mnocc_data")
    
    # Ensure the time column is in datetime format
    data["time"] = pd.to_datetime(data["time"])
    data["year"] = data["time"].dt.year
    data["month"] = data["time"].dt.month
    data["is_rainy"] = data["precipitation"] > 0

    # Map location_id to locality names
    locality_mapping = {
        0: "Yaounde",
        1: "Douala",
        2: "Bafoussam",
        3: "Buea",
        4: "Bamenda",
        5: "Ebolowa",
        6: "Bertoua",
        7: "Ngaoundere",
        8: "Garoua",
        9: "Maroua",
    }
    data["locality"] = data["location_id"].map(locality_mapping)

    return data

# Calculate the number of rainy days per year and locality
@st.cache_data
def calculate_rainy_days(data):
    return data.groupby(["locality", "year"])["is_rainy"].sum().reset_index(name="rainy_days")

# Calculate the average rainy season duration per locality
@st.cache_data
def calculate_rainy_season(data):
    monthly_rainy_days = data.groupby(["locality", "year", "month"])["is_rainy"].sum().reset_index(name="rainy_days")
    rainy_season = monthly_rainy_days[monthly_rainy_days["rainy_days"] > 15]
    rainy_season_duration = rainy_season.groupby(["locality", "year"]).size().reset_index(name="season_duration")
    return rainy_season_duration

# Main app
st.title("Visualisation de la saison des pluies")

# Load and process the data
data = load_data()
rainy_days = calculate_rainy_days(data)
rainy_season = calculate_rainy_season(data)

# Display dataset sample for verification
if st.checkbox("Afficher les données brutes"):
    st.write(data.head())

# Select locality
locality = st.selectbox("Sélectionnez une localité:", sorted(data["locality"].unique()))

# Filter data for selected locality
locality_rainy_days = rainy_days[rainy_days["locality"] == locality]
locality_rainy_season = rainy_season[rainy_season["locality"] == locality]

# Visualization: Number of rainy days per year
st.subheader(f"Nombre de jours de pluie par an en {locality}")
fig, ax = plt.subplots()
ax.bar(locality_rainy_days["year"], locality_rainy_days["rainy_days"], color="blue")
ax.set_xlabel("Année")
ax.set_ylabel("Jours de pluie")
ax.set_title("Jours de pluie par an")
st.pyplot(fig)

# Visualization: Rainy season duration
st.subheader(f"Durée de la saison des pluies en {locality}")
fig, ax = plt.subplots()
ax.bar(locality_rainy_season["year"], locality_rainy_season["season_duration"], color="green")
ax.set_xlabel("Année")
ax.set_ylabel("Durée (mois)")
ax.set_title("Durée de la saison des pluies")
st.pyplot(fig)

st.write("Cette application permet de visualiser le nombre de jours de pluie et la durée de la saison des pluies par localité.")



