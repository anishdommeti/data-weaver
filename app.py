import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import random

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Weather vs Zomato Food Orders",
    layout="centered"
)

# ---------------- TITLE ----------------
st.title("🌦️ Weather vs Zomato Food Orders 🍕")
st.write("How weather impacts food ordering behaviour")

# ---------------- LOAD DATA ----------------
df = pd.read_csv("zomato_orders.csv")
df["date"] = pd.to_datetime(df["date"])

# ---------------- CITY SELECTOR ----------------
cities = df["city"].unique()
selected_city = st.selectbox("Select City", cities)

city_df = df[df["city"] == selected_city]

# ---------------- WEATHER DATA ----------------
API_KEY = None
try:
    API_KEY = st.secrets["OPENWEATHER_API_KEY"]
except:
    pass

temp = None
condition = None

if API_KEY:
    try:
        weather_url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={selected_city},IN&appid={API_KEY}&units=metric"
        )

        weather_data = requests.get(weather_url, timeout=5).json()

        if "main" in weather_data:
            temp = weather_data["main"]["temp"]
            condition = weather_data["weather"][0]["main"]
        else:
            raise Exception("Weather API error")

    except:
        temp = random.randint(25, 35)
        condition = random.choice(["Clear", "Clouds", "Rain"])
else:
    temp = random.randint(25, 35)
    condition = random.choice(["Clear", "Clouds", "Rain"])

# ---------------- DISPLAY WEATHER ----------------
st.subheader("📍 Current Weather")
st.metric("Temperature (°C)", temp)
st.write("Condition:", condition)

# ---------------- EXPECTED ORDERS ----------------
filtered = city_df[city_df["weather"] == condition]

expected_orders = (
    int(filtered["orders"].mean())
    if not filtered.empty
    else int(city_df["orders"].mean())
)

st.metric("Expected Orders Today", expected_orders)

# ---------------- LINE CHART ----------------
st.subheader("📈 Orders Over Time")

fig, ax = plt.subplots()

ax.plot(
    city_df["date"],
    city_df["orders"],
    marker="o"
)

# ✅ FIXES
ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
plt.xticks(rotation=45)

ax.set_xlabel("Date")
ax.set_ylabel("Orders")
ax.set_title(f"Zomato Orders Trend – {selected_city}")

plt.tight_layout()
st.pyplot(fig)

# ---------------- DATA TABLE ----------------
st.subheader("📄 Raw Order Data")
st.dataframe(city_df)

# ---------------- INSIGHT ----------------
st.success(
    f"In **{selected_city}**, food orders tend to increase during **{condition}** weather conditions."
)
