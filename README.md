# Language Access Data Explorer — Demo

A working demo of the internal data navigation tool, running on **randomly generated dummy data** so it can be shown to the team before the real dataset is ready. Filters, stat cards, charts, and CSV download all work end-to-end — swap in the real data later without changing anything else about how it looks or behaves.

## 1. Run it locally (fastest way to check it works)

```bash
pip install -r requirements.txt
streamlit run app.py
```

This opens the app in your browser at `http://localhost:8501`. Nothing else needed — no login required when running locally.

## 2. Put it online with restricted access (for Wednesday)

This is the path that gets you a real link + login screen with the least setup.

1. **Push this folder to a GitHub repo** (can be private).
   ```bash
   git init
   git add .
   git commit -m "Initial demo"
   git branch -M main
   git remote add origin <your-repo-url>
   git push -u origin main
   ```
2. Go to **[share.streamlit.io](https://share.streamlit.io)** and sign in with your UW email (or GitHub).
3. Click **New app**, point it at your repo, branch `main`, main file `app.py`. Deploy.
4. Once deployed, open the app's settings and set it to **Private**.
5. Under sharing settings, **add the emails** of everyone who should have access (Nicole, Hendrika, Camille, Suella, Charlotte, Shreya, etc.) — this is the "login with your UW email" behavior described in the proposal. No code needed for this part; it's a Streamlit Cloud setting.
6. Anyone not on that list who tries to open the link will be asked to request access, not shown the data.

This gets you a real, shareable, login-gated link by Wednesday without building custom authentication.

## 3. Swapping in real data later

Everything the app does — filtering, charts, stat cards, download — reads from a single `load_data()` function near the top of `app.py`. Once the real de-identified data and data dictionary are ready:

1. Publish the Google Sheet, or connect it via `gspread` / `st.connection("gsheets", type=GSheetsConnection)` (Streamlit has a built-in Google Sheets connector — `pip install st-gsheets-connection`).
2. Replace the body of `load_data()` with a read from that source instead of the random generator, keeping the same column names (`call_center`, `call_date`, `interpreter_used`, `language`, `zip_code`, `time_of_day`, `connect_time_sec`, plus whatever else the data dictionary specifies).
3. Everything downstream (filters, charts, table) keeps working as-is, since it's all driven off those column names.

## What's in this demo vs. what's still open

**Working now:** filtering by call center, date range, interpreter use, zip code, language, and time of day; live-updating stat cards; three chart types (grouped bar, weekly trend line, stacked zip breakdown); filtered data table; CSV export.

**Still needs real answers before this goes further:** the actual variable list (data dictionary), what de-identification looks like for the real dataset, and the final access list.
