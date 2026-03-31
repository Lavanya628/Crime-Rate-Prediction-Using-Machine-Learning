Crime Rate Analysis & Prediction Dashboard

A web-based interactive dashboard to analyze, visualize, and understand crime patterns across different cities in India. This project helps in identifying trends, detecting hotspots, and supporting data-driven decision-making using charts and maps.

📸 Screenshots
![alt text](image.png)
![alt text](image-1.png)
![alt text](image-2.png)

📌 Features
📊 Interactive Dashboard
City-wise crime analysis
Year-wise crime trends
Month-wise crime patterns
Crime category distribution
Gender-based analysis

🗺️ Crime Hotspot Map
Displays crime density using map markers
Helps identify high-crime areas visually

📁 CSV Upload
Upload custom datasets
Dashboard updates dynamically

🔍 Filters
Filter by City
Filter by Year

KPIs and charts update instantly
📈 Key Metrics (KPIs)
Total crimes
Male victims
Female victims
Other

📉 Charts Used
Bar Chart (City-wise, Year-wise)
Line Chart (Monthly trend)
Pie Chart (Gender distribution)
Doughnut Chart (Crime type)

🛠️ Tech Stack
Category	                Technology
Frontend	                HTML, CSS, JavaScript
Charts	                    Chart.js
Maps	                    Leaflet.js
Backend	                    Flask (Python)
Data Processing	            Pandas

📂 Project Structure
project/
│
├── app.py
├── templates/
│   ├── dashboard.html
│   ├── login.html
│   └── register.html
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── uploads/
├── crime_dataset_india.csv
└── README.md

⚙️ How It Works
User uploads a CSV dataset
Data is processed using Pandas
Filters (City & Year) are applied
KPIs and charts are updated dynamically
Map displays crime hotspots using coordinates

▶️ How to Run the Project
1. Install dependencies
pip install flask pandas
2. Run the application
python app.py
3. Open in browser
http://127.0.0.1:5000
📊 Dataset Requirements

Your CSV file should contain columns like:

City
Date of Occurrence
Victim Gender
Crime Description

🎯 Objectives
Analyze historical crime data
Identify crime trends and patterns
Visualize crime distribution
Support better decision-making

👩‍💻 Author
Lavanya M

⭐ Support
If you like this project, give it a ⭐ on GitHub!
