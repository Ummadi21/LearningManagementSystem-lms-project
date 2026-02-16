from flask import Flask,request
import random
from sqlalchemy import text,func
from db.database import engine, session
from db.models import Base, User, Course,UserActivity,Activity
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict


app = Flask(__name__)

# Create tables
Base.metadata.create_all(engine)

def build_user_item_matrix():
    db = session

    users = db.query(User.id).all()
    courses = db.query(Course.id).all()
    activities = db.query(UserActivity).all()

    user_ids = [u[0] for u in users]
    course_ids = [c[0] for c in courses]

    user_index = {user_id: i for i, user_id in enumerate(user_ids)}
    course_index = {course_id: i for i, course_id in enumerate(course_ids)}

    matrix = np.zeros((len(user_ids), len(course_ids)))

    for activity in activities:
        u = user_index[activity.user_id]
        c = course_index[activity.course_id]
        matrix[u][c] += 1

    return matrix, user_index, course_index, course_ids


@app.route("/")
def home():
    return "Recommendation Service Running"


@app.route("/seed")
def seed_data():
    db = session

    # Clear existing data
    db.execute(text("DELETE FROM user_activity"))
    db.execute(text("DELETE FROM users"))
    db.execute(text("DELETE FROM courses"))
    db.commit()

    # Create Users
    users = []
    for i in range(1, 11):   # 10 users
        users.append(
            User(
                id=i,
                branch="CSE",
                skill_level="beginner"
            )
        )

    db.add_all(users)

    # Categories
    categories = ["Programming", "AI", "Cloud", "Database", "DevOps"]

    # Create 50 courses
    courses = []
    for i in range(1, 51):
        courses.append(
            Course(
                id=i,
                title=f"Course {i}",
                category=random.choice(categories)
            )
        )

    db.add_all(courses)
    db.commit()

    # 🔥 Generate Random User Activities
    activities = []
    for _ in range(200):  # 200 random interactions
        activities.append(
            UserActivity(
                user_id=random.randint(1, 10),
                course_id=random.randint(1, 50)
            )
        )

    db.add_all(activities)
    db.commit()

    return {"message": "Database reset with random users, courses, and activity"}



@app.route("/track", methods=["GET", "POST"])
def track_activity():
    db = session

    user_id = request.args.get("user_id")
    course_id = request.args.get("course_id")

    if not user_id or not course_id:
        return {"error": "user_id and course_id required"}

    activity = UserActivity(
        user_id=int(user_id),
        course_id=int(course_id)
    )

    db.add(activity)
    db.commit()

    return {"message": "Activity tracked successfully"}



@app.route("/recommend/<int:user_id>")
def recommend(user_id):
    db = session

    # -----------------------
    # GET USER VIEWED COURSES
    # -----------------------
    viewed = db.query(UserActivity).filter_by(user_id=user_id).all()
    viewed_course_ids = [v.course_id for v in viewed]

    # Cold Start → return global popularity
    if not viewed_course_ids:
        popular = (
            db.query(
                Course,
                func.count(UserActivity.course_id).label("popularity")
            )
            .outerjoin(UserActivity, Course.id == UserActivity.course_id)
            .group_by(Course.id)
            .order_by(func.count(UserActivity.course_id).desc())
            .limit(5)
            .all()
        )

        return {
            "recommended": [
                {
                    "id": c.id,
                    "title": c.title,
                    "category": c.category,
                    "score": pop
                }
                for c, pop in popular
            ]
        }

    # -----------------------
    # BUILD MATRIX
    # -----------------------
    matrix, user_index, course_index, course_ids = build_user_item_matrix()

    # -----------------------
    # ITEM SIMILARITY
    # -----------------------
    item_similarity = cosine_similarity(matrix.T)

    # -----------------------
    # GET USER VECTOR
    # -----------------------
    if user_id not in user_index:
        return {"error": "User not found"}

    user_vector = matrix[user_index[user_id]]

    # -----------------------
    # COLLABORATIVE SCORE
    # -----------------------
    scores = defaultdict(float)

    for course_id in viewed_course_ids:
        idx = course_index[course_id]
        similarity_scores = item_similarity[idx]

        for i, sim_score in enumerate(similarity_scores):
            candidate_id = course_ids[i]

            if candidate_id not in viewed_course_ids:
                scores[candidate_id] += sim_score

    # -----------------------
    # POPULARITY SCORE
    # -----------------------
    popularity = dict(
        db.query(
            UserActivity.course_id,
            func.count(UserActivity.course_id)
        )
        .group_by(UserActivity.course_id)
        .all()
    )

    # -----------------------
    # NORMALIZATION
    # -----------------------
    max_cf = max(scores.values()) if scores else 1
    max_pop = max(popularity.values()) if popularity else 1

    final_scores = []

    for course_id in course_ids:
        if course_id in viewed_course_ids:
            continue

        cf_score = scores.get(course_id, 0) / max_cf
        pop_score = popularity.get(course_id, 0) / max_pop

        final_score = 0.6 * cf_score + 0.4 * pop_score

        course = db.query(Course).filter_by(id=course_id).first()

        final_scores.append({
            "id": course.id,
            "title": course.title,
            "category": course.category,
            "score": round(final_score, 4)
        })

    ranked = sorted(final_scores, key=lambda x: x["score"], reverse=True)

    return {"recommended": ranked[:10]}




@app.route("/activities/<int:user_id>")
def get_activities(user_id):
    db = session
    activities = db.query(UserActivity)\
    .filter(UserActivity.user_id == user_id).all()

    return [
        {
            "user_id": a.user_id,
            "course_id": a.course_id
        }
        for a in activities
    ]




if __name__ == "__main__":
    app.run(debug=True)
