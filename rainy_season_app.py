import streamlit as st 
import pandas as pd
import plotly.express as px

# Ajouter un logo en en-tête
st.image("logo.png", width=80)  # Remplacez "logo.png" par le chemin de votre logo
st.title("Visualisation interactive de la saison des pluies")

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

# Calculate the number of rainy days per year and locality based on threshold
@st.cache_data
def calculate_rainy_days(data, threshold):
    data["is_rainy"] = data["precipitation"] >= threshold
    return data.groupby(["locality", "year"])["is_rainy"].sum().reset_index(name="rainy_days")

# Calculate the average rainy season duration per locality based on threshold
@st.cache_data
def calculate_rainy_season(data, threshold):
    data["is_rainy"] = data["precipitation"] >= threshold
    monthly_rainy_days = data.groupby(["locality", "year", "month"])["is_rainy"].sum().reset_index(name="rainy_days")
    rainy_season = monthly_rainy_days[monthly_rainy_days["rainy_days"] > 15]
    rainy_season_duration = rainy_season.groupby(["locality", "year"]).size().reset_index(name="season_duration")
    return rainy_season_duration

# Main app

# Load and process the data
data = load_data()

# User input for precipitation threshold
threshold = st.number_input("Entrez le seuil de précipitation (mm/jour) :", min_value=1.0, value=1.0, step=0.1)

# Calculate rainy days and rainy season based on user-defined threshold
rainy_days = calculate_rainy_days(data, threshold)
rainy_season = calculate_rainy_season(data, threshold)

# Display dataset sample for verification
if st.checkbox("Afficher les données brutes"):
    st.write(data.head())

# Select locality
locality = st.selectbox("Sélectionnez une localité:", sorted(data["locality"].unique()))

# Filter data for selected locality
locality_rainy_days = rainy_days[rainy_days["locality"] == locality]
locality_rainy_season = rainy_season[rainy_season["locality"] == locality]

# Visualization: Number of rainy days per year
st.subheader(f"Nombre de jours de pluie par an à {locality} (Seuil ≥ {threshold} mm/jour)")
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
st.subheader(f"Durée de la saison des pluies à {locality} (Seuil ≥ {threshold} mm/jour)")
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

# Prepare data for download
export_data = pd.DataFrame({
    'Année': locality_rainy_days['year'],
    'Jours de pluie': locality_rainy_days['rainy_days'],
    'Durée de la saison (mois)': locality_rainy_season['season_duration'].reindex(locality_rainy_days.index, fill_value=0)  # Aligning indices for correct export
})

# Download button for exporting the data
st.download_button(
    label="Télécharger les données",
    data=export_data.to_csv(index=False).encode('utf-8'),
    file_name=f"{locality}_pluie_donnees.csv",
    mime='text/csv'
)

st.write("Cette application permet de visualiser interactivement le nombre de jours de pluie et la durée de la saison des pluies par localité.")
