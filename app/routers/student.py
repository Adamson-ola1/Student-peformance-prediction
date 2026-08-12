from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.model import (
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    PaginatedStudents
)

router = APIRouter(
    prefix="/students",
    tags=["Students"]
)


# ─────────────────────────────────────────────
# GET /students → Paginated List
# ─────────────────────────────────────────────
@router.get("/", response_model=PaginatedStudents)
def get_students(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=200),
    db: Session = Depends(get_db),
):
    offset = (page - 1) * page_size

    total_query = text("""
        SELECT COUNT(*)
        FROM StudentPerformance
    """)

    total = db.execute(total_query).scalar()

    query = text("""
        SELECT *
        FROM StudentPerformance
        ORDER BY student_id
        OFFSET :offset ROWS
        FETCH NEXT :page_size ROWS ONLY
    """)

    rows = db.execute(
        query,
        {
            "offset": offset,
            "page_size": page_size
        }
    ).mappings().all()

    students = [dict(row) for row in rows]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "students": students
    }


# ─────────────────────────────────────────────
# GET /students/{student_id}
# ─────────────────────────────────────────────
@router.get("/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: int,
    db: Session = Depends(get_db)
):
    query = text("""
        SELECT *
        FROM StudentPerformance
        WHERE student_id = :student_id
    """)

    row = db.execute(
        query,
        {"student_id": student_id}
    ).mappings().first()

    if not row:
        raise HTTPException(
            status_code=404,
            detail=f"Student {student_id} not found."
        )

    return dict(row)


# ─────────────────────────────────────────────
# POST /students
# ─────────────────────────────────────────────
@router.post(
    "/",
    response_model=StudentResponse,
    status_code=201
)
def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db)
):
    insert_query = text("""
        SET NOCOUNT ON;
        INSERT INTO StudentPerformance (
            age,
            gender,
            attendance_rate,
            study_hours_per_week,
            previous_gpa,
            extracurricular_score,
            family_income
        )
        VALUES (
            :age,
            :gender,
            :attendance_rate,
            :study_hours_per_week,
            :previous_gpa,
            :extracurricular_score,
            :family_income
        );
        SELECT CAST(SCOPE_IDENTITY() AS INT) AS new_id;
    """)

    result = db.execute(insert_query, student.model_dump())
    new_id = result.scalar()

    db.commit()

    if new_id is None:
        raise HTTPException(
            status_code=500,
            detail="Insert succeeded but no identity value was returned."
        )

    select_query = text("""
        SELECT *
        FROM StudentPerformance
        WHERE student_id = :student_id
    """)

    row = db.execute(
        select_query,
        {"student_id": new_id}
    ).mappings().first()

    if not row:
        raise HTTPException(
            status_code=500,
            detail="Insert succeeded but the new row could not be retrieved."
        )

    return dict(row)


# ─────────────────────────────────────────────
# PUT /students/{student_id}
# ─────────────────────────────────────────────
@router.put(
    "/{student_id}",
    response_model=StudentResponse
)
def update_student(
    student_id: int,
    student: StudentUpdate,
    db: Session = Depends(get_db)
):
    fields = student.model_dump(exclude_none=True)

    if not fields:
        raise HTTPException(
            status_code=400,
            detail="No fields provided."
        )

    set_clause = ", ".join([
        f"{key} = :{key}"
        for key in fields.keys()
    ])

    fields["student_id"] = student_id

    query = text(f"""
        SET NOCOUNT ON;
        UPDATE StudentPerformance
        SET {set_clause}
        OUTPUT INSERTED.*
        WHERE student_id = :student_id
    """)

    result = db.execute(query, fields)
    row = result.mappings().first()

    if not row:
        raise HTTPException(
            status_code=404,
            detail=f"Student {student_id} not found."
        )

    db.commit()

    return dict(row)


# ─────────────────────────────────────────────
# DELETE /students/{student_id}
# ─────────────────────────────────────────────
@router.delete("/{student_id}", status_code=204)
def delete_student(
    student_id: int,
    db: Session = Depends(get_db)
):
    query = text("""
        DELETE FROM StudentPerformance
        WHERE student_id = :student_id
    """)

    result = db.execute(
        query,
        {"student_id": student_id}
    )

    if result.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Student {student_id} not found."
        )

    db.commit()