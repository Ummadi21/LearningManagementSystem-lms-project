# LMS Recommendation System

Hybrid recommendation system using:

- Popularity-based ranking
- Item-based Collaborative Filtering
- Hybrid scoring (CF + Popularity)

## Tech Stack

- Flask
- SQLAlchemy
- SQLite
- NumPy
- Scikit-learn

## Setup Instructions

1. Clone the repository

git clone <your_repo_url>

2. Create virtual environment

python -m venv venv

3. Activate virtual environment

Windows:
venv\Scripts\activate

4. Install dependencies

pip install -r requirements.txt

5. Run application

python app.py

## API Endpoints

- /seed
- /track
- /recommend/<user_id>
- /activities/<user_id>

