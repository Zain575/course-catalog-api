from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from models import Course
from data import get_all_courses, find_course

app = FastAPI(title="Course Catalog API")


@app.get("/")
def read_root():
    return {"message": "Course Catalog API is running"}


# Pagination dependency function
def pagination(page: int = 1, page_size: int = 20):
    offset = (page - 1) * page_size
    return {"offset": offset, "limit": page_size}


@app.get("/courses", response_model=list[Course])
def list_courses(
    is_elective: Optional[bool] = None,
    sort: str = "popular",
    p: dict = Depends(pagination),
):
    courses = get_all_courses()

    # 1. Filtering (must check 'is not None' so False isn't ignored)
    if is_elective is not None:
        courses = [c for c in courses if c.is_elective == is_elective]

    # 2. Sorting
    if sort == "title":
        courses = sorted(courses, key=lambda c: c.title)
    else:
        courses = sorted(courses, key=lambda c: c.likes, reverse=True)

    # 3. Pagination Slicing
    offset = p["offset"]
    limit = p["limit"]
    return courses[offset : offset + limit]


@app.get("/courses/{course_id}", response_model=Course)
def get_course(course_id: str):
    course = find_course(course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return course
