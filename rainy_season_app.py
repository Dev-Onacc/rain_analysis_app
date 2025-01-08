import streamlit as st 
import pandas as pd
import plotly.express as px

# Ajouter un logo en en-tête
st.image("logo.png", width=80)  # Remplacez "logo.png" par le chemin de votre logo
st.title("Visualisation interactive de la saison des pluies (Seuil ≥ 1 mm/jour)")

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
    
    # Apply the precipitation threshold of ≥ 1 mm/day
    data["is_rainy"] = data["precipitation"] >= 1

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
st.subheader(f"Nombre de jours de pluie par an à {locality}")
fig_rainy_days = px.bar(
    locality_rainy_days,
    x="year",
    y="rainy_days",
    labels={"year": "Année", "rainy_days": "Jours de pluie"},
    title=f"Jours de pluie par an à {locality}",
    color="rainy_days",
    color_continuous_scale="Blues"
)
fig_rainy_days.update_layout(hovermode="x unified")
st.plotly_chart(fig_rainy_days)

# Visualization: Rainy season duration
st.subheader(f"Durée de la saison des pluies à {locality}")
fig_rainy_season = px.bar(
    locality_rainy_season,
    x="year",
    y="season_duration",
    labels={"year": "Année", "season_duration": "Durée (mois)"},
    title=f"Durée de la saison des pluies à {locality}",
    color="season_duration",
    color_continuous_scale="Greens"
)
fig_rainy_season.update_layout(hovermode="x unified")
st.plotly_chart(fig_rainy_season)

st.write("Cette application permet de visualiser interactivement le nombre de jours de pluie (seuil ≥ 1 mm/jour) et la durée de la saison des pluies par localité.")
