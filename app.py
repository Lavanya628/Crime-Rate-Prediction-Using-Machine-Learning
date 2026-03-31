from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import joblib
import os
from werkzeug.utils import secure_filename
from flask import send_file
import os
from flask import send_file
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import os
import pandas as pd
import matplotlib.pyplot as plt

from flask import send_file, session
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4


# ================= APP CONFIG =================
app = Flask(__name__)
app.secret_key = "secret123"
DB = "database.db"

# ================= LOAD DATASET =================
DATASET_PATH = r"C:\Users\Lavanya m\OneDrive\Desktop\FINAL\crime_dataset_india.csv"
df = pd.read_csv(DATASET_PATH)

# ================= RAW DATA (FOR DROPDOWNS ONLY) =================
raw_df = pd.read_csv("crime_dataset_india.csv")

raw_df["City"] = (
    raw_df["City"]
    .astype(str)
    .str.strip()
    .str.lower()
)

city_aliases = {
    "bangalore": "bengaluru",
    "bombay": "mumbai",
    "madras": "chennai",
    "calcutta": "kolkata"
}

raw_df["City"] = raw_df["City"].replace(city_aliases)

raw_df["Crime Code"] = raw_df["Crime Code"].astype(int)
raw_df["Victim Age"] = raw_df["Victim Age"].astype(int)

# ================= LOAD MODEL =================
MODEL_PATH = "model/model.pkl"
ENCODER_PATH = "model/encoders.pkl"

if not os.path.exists(MODEL_PATH) or not os.path.exists(ENCODER_PATH):
    raise FileNotFoundError("Run train_model.py first to generate model & encoders")

model = joblib.load(MODEL_PATH)

encoders = joblib.load(ENCODER_PATH)
le_city = encoders["city"]
le_gender = encoders["gender"]
le_weapon = encoders["weapon"]
le_desc = encoders["desc"]
# ================= DATABASE =================
def get_db():
    return sqlite3.connect(DB)

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def landing():
    return render_template("landing.html")
#==========================HOME====================
@app.route("/home")
def home():
    if "user" not in session:
        return redirect("/")
    return render_template("home.html", user=session["user"])
# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT password, username FROM users WHERE email=?", (email,))
        user = cur.fetchone()
        conn.close()

        if user and check_password_hash(user[0], password):
            session["user"] = user[1]
            return redirect("/home")
        else:
            flash("Invalid email or password", "danger")

    return render_template("login.html")

# ================= REGISTER =================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users(username,email,password) VALUES(?,?,?)",
                (username, email, password)
            )
            conn.commit()
            conn.close()
            flash("Account created successfully!", "success")
            return redirect("/")
        except:
            flash("Email already registered", "danger")

    return render_template("register.html")

# ================= FORGOT PASSWORD =================
@app.route("/forgot", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]
        new_password = generate_password_hash(request.form["password"])

        conn = get_db()
        cur = conn.cursor()
        cur.execute("UPDATE users SET password=? WHERE email=?",
                    (new_password, email))
        conn.commit()
        conn.close()

        flash("Password updated successfully!", "success")
        return redirect("/")

    return render_template("forgot_password.html")
#=======================================================
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

CITY_COORDS = {
    "Agra": [27.1767, 78.0081],
    "Ahmedabad": [23.0225, 72.5714],
    "Bangalore": [12.9716, 77.5946],
    "Bhopal": [23.2599, 77.4126],
    "Chennai": [13.0827, 80.2707],
    "Delhi": [28.6139, 77.2090],
    "Faridabad": [28.4089, 77.3178],
    "Ghaziabad": [28.6692, 77.4538],
    "Hyderabad": [17.3850, 78.4867],
    "Indore": [22.7196, 75.8577],
    "Jaipur": [26.9124, 75.7873],
    "Kalyan": [19.2403, 73.1305],
    "Kanpur": [26.4499, 80.3319],
    "Kolkata": [22.5726, 88.3639],
    "Lucknow": [26.8467, 80.9462],
    "Ludhiana": [30.9010, 75.8573],
    "Meerut": [28.9845, 77.7064],
    "Mumbai": [19.0760, 72.8777],
    "Nagpur": [21.1458, 79.0882]
}

#==========================DASH BOARD====================
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    DEFAULT_DATASET = "crime_dataset_india.csv"
    UPLOAD_FOLDER = "uploads"
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

    uploaded = False
    selected_city = "All"
    selected_year = "All"

    # ---------------- DATASET PATH ----------------
    dataset_path = DEFAULT_DATASET

    # ---------------- HANDLE UPLOAD ----------------
    if request.method == "POST":
        file = request.files.get("dataset")
        if file and file.filename.endswith(".csv"):
            upload_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(upload_path)
            session["dataset_path"] = upload_path
            dataset_path = upload_path
            uploaded = True

    if "dataset_path" in session:
        dataset_path = session["dataset_path"]
        uploaded = True

    # ---------------- LOAD DATA ----------------
    df = pd.read_csv(dataset_path)

    # ---------------- DATE PROCESS ----------------
    if "Date of Occurrence" in df.columns:
        df["Date of Occurrence"] = pd.to_datetime(
            df["Date of Occurrence"],
            errors="coerce",
            dayfirst=True
        )
        df["Year"] = df["Date of Occurrence"].dt.year
        df["Month"] = df["Date of Occurrence"].dt.month
    else:
        df["Year"] = None
        df["Month"] = None

    # ---------------- CLEAN GENDER ----------------
    if "Victim Gender" in df.columns:
        df["Victim Gender"] = (
            df["Victim Gender"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        df["Victim Gender"] = df["Victim Gender"].replace({
            "m": "male",
            "f": "female",
            "others": "other",
            "unknown": "other",
            "nan": "other",
            "": "other"
        })

    # ---------------- FILTER OPTIONS ----------------
    cities = sorted(df["City"].dropna().unique().tolist())
    years = sorted(df["Year"].dropna().astype(int).unique().tolist())

    # ================= APPLY FILTERS (KPIs + CHARTS) =================
    if uploaded:
        selected_city = request.form.get("city", "All")
        selected_year = request.form.get("year", "All")

        if selected_city != "All":
            df = df[df["City"] == selected_city]

        if selected_year != "All":
            df = df[df["Year"] == int(selected_year)]

    # ================= KPIs (FILTERED DATA) =================
    total = len(df)
    male = (df["Victim Gender"] == "male").sum()
    female = (df["Victim Gender"] == "female").sum()
    other = len(df) - male - female

    kpis = {
        "total": int(total),
        "male": int(male),
        "female": int(female),
        "other": int(other)
    }

    # ================= CHART DATA =================
    charts = {}

    # -------- City-wise --------
    city_counts = df["City"].value_counts()
    charts["city_labels"] = city_counts.index.tolist()[:5]
    charts["city_values"] = city_counts.values.tolist()[:5]
    charts["all_city_labels"] = city_counts.index.tolist()
    charts["all_city_values"] = city_counts.values.tolist()

    # -------- Gender --------
    charts["gender_labels"] = ["Male", "Female", "Other"]
    charts["gender_values"] = [int(male), int(female), int(other)]
    # -------- Crime Description --------
    crime_counts = df["Crime Description"].value_counts()
    charts["crime_labels"] = crime_counts.index.tolist()
    charts["crime_values"] = crime_counts.values.tolist()

    # -------- Year --------
    year_counts = df["Year"].value_counts().sort_index()
    charts["year_labels"] = year_counts.index.dropna().astype(int).tolist()
    charts["year_values"] = year_counts.values.tolist()

    # -------- Month --------
    charts["month_labels"] = ["Jan","Feb","Mar","Apr","May","Jun",
                              "Jul","Aug","Sep","Oct","Nov","Dec"]
    charts["month_values"] = (
        df.groupby("Month")
        .size()
        .reindex(range(1,13), fill_value=0)
        .tolist()
    )

    # -------- Map --------
    map_data = []
    for city, count in city_counts.items():
        if city in CITY_COORDS:
            map_data.append({
                "city": city,
                "lat": CITY_COORDS[city][0],
                "lon": CITY_COORDS[city][1],
                "count": int(count)
            })
    charts["map_data"] = map_data

    # ---------------- RENDER ----------------
    return render_template(
        "dashboard.html",
        kpis=kpis,
        charts=charts,
        cities=cities,
        years=years,
        uploaded=uploaded,
        selected_city=selected_city,
        selected_year=selected_year
    )
#========================download==================
@app.route("/download")
def download_page():
    return render_template("download_report.html")

@app.route("/download_report", methods=["POST"])
def download_report():

    # ---------- Load dataset ----------
    dataset_path = session.get("dataset_path", "crime_dataset_india.csv")
    df = pd.read_csv(dataset_path)

    os.makedirs("reports", exist_ok=True)
    os.makedirs("reports/charts", exist_ok=True)

    pdf_path = "reports/crime_dashboard_report.pdf"

    # ---------- KPIs ----------
    total_crimes = len(df)
    top_city = df["City"].value_counts().idxmax()
    top_city_count = df["City"].value_counts().max()
    gender_counts = df["Victim Gender"].value_counts()

    # ---------- Generate Charts ----------
    # Bar Chart – City-wise crimes
    plt.figure()
    df["City"].value_counts().head(5).plot(kind="bar")
    plt.title("Top 5 Cities by Crime Rate")
    bar_path = "reports/charts/city_bar.png"
    plt.savefig(bar_path)
    plt.close()

    # Pie Chart – Gender distribution
    plt.figure()
    gender_counts.plot(kind="pie", autopct="%1.1f%%")
    plt.title("Victim Gender Distribution")
    pie_path = "reports/charts/gender_pie.png"
    plt.savefig(pie_path)
    plt.close()

    # ---------- Build PDF ----------
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    content = []

    content.append(Paragraph("Crime Dashboard Report", styles["Title"]))
    content.append(Spacer(1, 12))

    content.append(Paragraph(f"<b>Total Crimes:</b> {total_crimes}", styles["Normal"]))
    content.append(Paragraph(
        f"<b>Highest Crime City:</b> {top_city} ({top_city_count})",
        styles["Normal"]
    ))

    content.append(Spacer(1, 12))
    content.append(Paragraph("<b>City-wise Crime Chart</b>", styles["Heading2"]))
    content.append(Image(bar_path, width=400, height=250))

    content.append(Spacer(1, 12))
    content.append(Paragraph("<b>Gender Distribution Chart</b>", styles["Heading2"]))
    content.append(Image(pie_path, width=350, height=250))

    doc.build(content)

    return send_file(pdf_path, as_attachment=True)
@app.route("/download_excel", methods=["POST"])
def download_excel():

    dataset_path = session.get("dataset_path", "crime_dataset_india.csv")
    df = pd.read_csv(dataset_path)

    os.makedirs("reports", exist_ok=True)
    excel_path = "reports/crime_dashboard_report.xlsx"

    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Crime Data", index=False)

        summary = pd.DataFrame({
            "Metric": ["Total Crimes", "Top City"],
            "Value": [len(df), df["City"].value_counts().idxmax()]
        })
        summary.to_excel(writer, sheet_name="Summary", index=False)

    return send_file(excel_path, as_attachment=True)

# ================= PREDICTION =================
@app.route("/predict", methods=["GET", "POST"])
def predict():

    if "user" not in session:
        return redirect("/")

    gender = weapon = description = None

    cities = sorted(df["City"].unique())

    if request.method == "POST":
        city = request.form["city"].strip().lower()
        city = city_aliases.get(city, city)

        crime_code = int(request.form["crime_code"])
        age = int(request.form["age"])

        city_enc = le_city.transform([city])[0]

        pred = model.predict([[city_enc, crime_code, age]])[0]

        gender = le_gender.inverse_transform([pred[0]])[0]
        weapon = le_weapon.inverse_transform([pred[1]])[0]
        description = le_desc.inverse_transform([pred[2]])[0]

    return render_template(
        "predict.html",
        cities=cities,
        gender=gender,
        weapon=weapon,
        description=description
    )

# ================= CASCADING DROPDOWNS =================
@app.route("/get_crime_codes/<city>")
def get_crime_codes(city):
    city = city.strip().lower()

    city_aliases = {
        "bangalore": "bengaluru",
        "bombay": "mumbai",
        "madras": "chennai",
        "calcutta": "kolkata"
    }
    city = city_aliases.get(city, city)

    codes = (
        raw_df[raw_df["City"] == city]["Crime Code"]
        .value_counts()
        .head(15)   # 🔥 TOP 15 ONLY
        .index
        .tolist()
    )

    return jsonify(codes)


@app.route("/get_ages/<city>/<crime_code>")
def get_ages(city, crime_code):
    city = city.strip().lower()
    city = city_aliases.get(city, city)
    crime_code = int(crime_code)

    ages = (
        raw_df[
            (raw_df["City"] == city) &
            (raw_df["Crime Code"] == crime_code)
        ]["Victim Age"]
        .dropna()
        .unique()
        .tolist()
    )

    return jsonify(sorted(ages))


# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
