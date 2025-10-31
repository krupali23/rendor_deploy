# rendor_deploy

💬 Kiez Connect – Backend API

FastAPI backend for Kiez Connect, a Berlin-based assistant that provides data about tech jobs, events, and German courses.
Deployed live on Render:https://hackathon-kiez-chatbot.onrender.com/
👉 https://rendor-deploy.onrender.com

🚀 Overview

This API powers the Kiez Connect frontend (React or Streamlit).
It exposes clean JSON endpoints for querying available jobs, events, and courses with filtering options like:

Topic (job, event, course)

District (Mitte, Kreuzberg, etc.)

Search scope (all, only, or nearby)

Radius (for “nearby” search)

Optional keyword filtering

Data is loaded from local CSVs stored in the backend’s data folder.

🌐 Live API Endpoints
Method	Endpoint	Description
GET	/	Friendly root info
GET	/api/health	Health check ({"status":"ok"})
POST	/api/search	Main search endpoint
GET	/docs	Interactive Swagger documentation
GET	/api/debug/data	(optional) Check loaded dataset
GET	/api/areas	(optional) List all known districts
🔎 Example: Search API

Request

POST https://rendor-deploy.onrender.com/api/search

Body

{
  "query": "jobs in Mitte python",
  "topic": "job",
  "district": "Mitte",
  "scope": "all",
  "radius_km": 5.0,
  "use_my_location": false,
  "limit": 10
}


Response

{
  "total": 460,
  "count": 10,
  "items": [
    {
      "id": 0,
      "type": "job",
      "title": "Data & Business Systems Analyst",
      "company": "Wolt",
      "district": "Mitte",
      "latitude": 52.52,
      "longitude": 13.405,
      "job_url_direct": "https://grnh.se/3ica153t1us"
    },
    ...
  ]
}

🧠 Parameters Supported by /api/search
Field	Type	Description
query	string	Free text (auto-detects district/keywords)
topic	"job", "event", "course"	Filter by type
district	string	e.g. "Mitte"
scope	"all", "only", "nearby"	How to interpret district
radius_km	float	For nearby filtering
use_my_location	bool	Use user coordinates instead of district centroid
origin_lat, origin_lon	float	Coordinates for nearby search
keyword	string	Extra filter like "python"
limit	int	Max results
offset	int	Pagination offset
sort_by, sort_dir	string, `"asc"	"desc"`
🧩 Data Sources

CSV files should be placed under:

backend/data/
├─ berlin_tech_jobs.csv
├─ berlin_tech_events.csv
└─ german_courses_berlin.csv


Environment variable used by Render:

KC_DATA_DIR = /opt/render/project/src/backend/data

⚙️ Local Development

Requirements

fastapi
uvicorn[standard]
pandas
pydantic


Run locally

uvicorn api:app --reload


Then open: http://127.0.0.1:8000/docs

🧱 Repository Structure
rendor_deploy/
├─ api.py              # FastAPI app (main API)
├─ core.py             # Data loading, filtering, and logic
├─ requirements.txt    # Dependencies
├─ backend/
│  └─ data/            # CSVs for jobs, events, courses
└─ README.md           # This file

🔒 CORS

CORS is enabled for:

allow_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://your-react-domain.com"
]


Add your production domain here when your frontend is deployed.

💡 Example React Fetch Code
fetch("https://rendor-deploy.onrender.com/api/search", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    query: "python jobs in mitte",
    topic: "job",
    limit: 10
  }),
})
  .then(res => res.json())
  .then(data => console.log(data.items))
  .catch(console.error);

🧰 Debugging

GET /api/debug/data → confirms CSVs loaded correctly

GET /api/areas → shows known district names

Check logs in Render Dashboard if rows = 0 → means CSV path misconfigured

✅ Deployment Info

Platform: Render.com

Runtime: FastAPI (Python 3.11+)

Start Command:

uvicorn api:app --host 0.0.0.0 --port 10000


Environment Variable:

KC_DATA_DIR=/opt/render/project/src/backend/data

👩‍💻 Contact

Maintainer: Krupa
Repository: GitHub – rendor_deploy

Deployed API: https://rendor-deploy.onrender.comChatGPT said:

Perfect 🙌 Here’s a ready-to-use README.md for your backend repository (rendor_deploy).
Just copy this text into a file named README.md at the root of your repo — it’ll clearly explain everything to your web developer or anyone using your API.

💬 Kiez Connect – Backend API

FastAPI backend for Kiez Connect, a Berlin-based assistant that provides data about tech jobs, events, and German courses.
Deployed live on Render:
👉 https://rendor-deploy.onrender.com

🚀 Overview

This API powers the Kiez Connect frontend (React or Streamlit).
It exposes clean JSON endpoints for querying available jobs, events, and courses with filtering options like:

Topic (job, event, course)

District (Mitte, Kreuzberg, etc.)

Search scope (all, only, or nearby)

Radius (for “nearby” search)

Optional keyword filtering

Data is loaded from local CSVs stored in the backend’s data folder.

🌐 Live API Endpoints
Method	Endpoint	Description
GET	/	Friendly root info
GET	/api/health	Health check ({"status":"ok"})
POST	/api/search	Main search endpoint
GET	/docs	Interactive Swagger documentation
GET	/api/debug/data	(optional) Check loaded dataset
GET	/api/areas	(optional) List all known districts
🔎 Example: Search API

Request

POST https://rendor-deploy.onrender.com/api/search

Body

{
  "query": "jobs in Mitte python",
  "topic": "job",
  "district": "Mitte",
  "scope": "all",
  "radius_km": 5.0,
  "use_my_location": false,
  "limit": 10
}


Response

{
  "total": 460,
  "count": 10,
  "items": [
    {
      "id": 0,
      "type": "job",
      "title": "Data & Business Systems Analyst",
      "company": "Wolt",
      "district": "Mitte",
      "latitude": 52.52,
      "longitude": 13.405,
      "job_url_direct": "https://grnh.se/3ica153t1us"
    },
    ...
  ]
}

🧠 Parameters Supported by /api/search
Field	Type	Description
query	string	Free text (auto-detects district/keywords)
topic	"job", "event", "course"	Filter by type
district	string	e.g. "Mitte"
scope	"all", "only", "nearby"	How to interpret district
radius_km	float	For nearby filtering
use_my_location	bool	Use user coordinates instead of district centroid
origin_lat, origin_lon	float	Coordinates for nearby search
keyword	string	Extra filter like "python"
limit	int	Max results
offset	int	Pagination offset
sort_by, sort_dir	string, `"asc"	"desc"`
🧩 Data Sources

CSV files should be placed under:

backend/data/
├─ berlin_tech_jobs.csv
├─ berlin_tech_events.csv
└─ german_courses_berlin.csv


Environment variable used by Render:

KC_DATA_DIR = /opt/render/project/src/backend/data

⚙️ Local Development

Requirements

fastapi
uvicorn[standard]
pandas
pydantic


Run locally

uvicorn api:app --reload


Then open: http://127.0.0.1:8000/docs

🧱 Repository Structure
rendor_deploy/
├─ api.py              # FastAPI app (main API)
├─ core.py             # Data loading, filtering, and logic
├─ requirements.txt    # Dependencies
├─ backend/
│  └─ data/            # CSVs for jobs, events, courses
└─ README.md           # This file

🔒 CORS

CORS is enabled for:

allow_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://your-react-domain.com"
]


Add your production domain here when your frontend is deployed.

💡 Example React Fetch Code
fetch("https://rendor-deploy.onrender.com/api/search", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    query: "python jobs in mitte",
    topic: "job",
    limit: 10
  }),
})
  .then(res => res.json())
  .then(data => console.log(data.items))
  .catch(console.error);

🧰 Debugging

GET /api/debug/data → confirms CSVs loaded correctly

GET /api/areas → shows known district names

Check logs in Render Dashboard if rows = 0 → means CSV path misconfigured

✅ Deployment Info

Platform: Render.com

Runtime: FastAPI (Python 3.11+)

Start Command:

uvicorn api:app --host 0.0.0.0 --port 10000


Environment Variable:

KC_DATA_DIR=/opt/render/project/src/backend/data

👩‍💻 Contact

Maintainer: Krupa
Repository: GitHub – rendor_deploy

Deployed API: https://rendor-deploy.onrender.com
