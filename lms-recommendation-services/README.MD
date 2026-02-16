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

![image alt](https://github.com/Ummadi21/LearningManagementSystem-lms-project/blob/b0c9bc1763f79d577da31e63175473293938574d/lms-recommendation-services/screenshots/home.png)

## API Endpoints

- /seed
![image alt](https://github.com/Ummadi21/LearningManagementSystem-lms-project/blob/b0c9bc1763f79d577da31e63175473293938574d/lms-recommendation-services/screenshots/home.png)
- /track
- /recommend/<user_id>
![image alt](https://github.com/Ummadi21/LearningManagementSystem-lms-project/blob/b0c9bc1763f79d577da31e63175473293938574d/lms-recommendation-services/screenshots/home.png)
- /activities/<user_id>

