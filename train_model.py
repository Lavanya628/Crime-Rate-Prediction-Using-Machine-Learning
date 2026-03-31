import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

# ================= LOAD DATASET =================
df = pd.read_csv(
    r"C:\Users\Lavanya m\OneDrive\Desktop\FINAL\crime_dataset_india.csv"
)

# ================= CLEAN DATA =================
df["City"] = df["City"].astype(str).str.strip().str.lower()

city_aliases = {
    "bangalore": "bengaluru",
    "bombay": "mumbai",
    "madras": "chennai",
    "calcutta": "kolkata"
}
df["City"] = df["City"].replace(city_aliases)

df["Crime Code"] = df["Crime Code"].astype(int)
df["Victim Age"] = df["Victim Age"].astype(int)

# ================= ENCODERS =================
le_city = LabelEncoder()
le_gender = LabelEncoder()
le_weapon = LabelEncoder()
le_desc = LabelEncoder()

df["City_enc"] = le_city.fit_transform(df["City"])
df["Gender_enc"] = le_gender.fit_transform(df["Victim Gender"])
df["Weapon_enc"] = le_weapon.fit_transform(df["Weapon Used"])
df["Desc_enc"] = le_desc.fit_transform(df["Crime Description"])

# ================= FEATURES & TARGET =================
X = df[["City_enc", "Crime Code", "Victim Age"]]
y = df[["Gender_enc", "Weapon_enc", "Desc_enc"]]

# ================= TRAIN MODEL =================
model = RandomForestClassifier(
    n_estimators=30,
    max_depth=10,
    random_state=42
)
model.fit(X, y)

# ================= SAVE MODEL =================
os.makedirs("model", exist_ok=True)

joblib.dump(model, "model/model.pkl")
joblib.dump(
    {
        "city": le_city,
        "gender": le_gender,
        "weapon": le_weapon,
        "desc": le_desc
    },
    "model/encoders.pkl"
)

print("✅ Model trained and saved successfully")
