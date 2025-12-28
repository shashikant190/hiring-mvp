from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import secrets

from db import SessionLocal, engine
from models import Base, Job, Applicant, PageView

from fastapi.staticfiles import StaticFiles

Base.metadata.drop_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# ---------------------------
# HOME — CREATE JOB
# ---------------------------
@app.get("/", response_class=HTMLResponse)
def create_job_form(request: Request):
    return templates.TemplateResponse("create_job.html", {"request": request})


@app.post("/create-job", response_class=HTMLResponse)
def create_job(
    request: Request,
    title: str = Form(...),
    description: str = Form(...)
):
    db: Session = SessionLocal()

    secret = secrets.token_urlsafe(8)

    job = Job(title=title, description=description, secret=secret)
    db.add(job)
    db.commit()
    db.refresh(job)

    base_url = str(request.base_url).rstrip("/")

    apply_link = f"{base_url}/apply/{job.id}"
    admin_link = f"{base_url}/applicants/{job.id}?secret={secret}"

    return templates.TemplateResponse(
        "create_job.html",
        {
            "request": request,
            "apply_link": apply_link,
            "admin_link": admin_link
        }
    )


# ---------------------------
# APPLY — FREELANCER VIEW
# ---------------------------
@app.get("/apply/{job_id}", response_class=HTMLResponse)
def apply_form(job_id: int, request: Request):
    db: Session = SessionLocal()

    job = db.query(Job).filter_by(id=job_id).first()
    if not job:
        return HTMLResponse("<h2>Job not found</h2>", status_code=404)

    view = db.query(PageView).filter_by(job_id=job_id).first()
    if not view:
        db.add(PageView(job_id=job_id, count=1))
    else:
        view.count += 1

    db.commit()

    return templates.TemplateResponse(
        "apply.html",
        {"request": request, "job": job}
    )


@app.post("/apply/{job_id}", response_class=HTMLResponse)
def submit_application(
    job_id: int,
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    country: str = Form(...),
    github: str = Form(""),
    skills: str = Form(...),
    availability: str = Form(...),
    proof: str = Form("")
):
    db: Session = SessionLocal()

    job = db.query(Job).filter_by(id=job_id).first()
    if not job:
        return HTMLResponse("<h2>Job not found</h2>", status_code=404)

    applicant = Applicant(
        job_id=job_id,
        name=name,
        email=email,
        country=country,
        github=github,
        skills=skills,
        availability=availability,
        proof=proof
    )

    db.add(applicant)
    db.commit()

    return HTMLResponse(
        """
        <link rel="stylesheet" href="/static/style.css">
        <div class="container">
          <h2>Application submitted...</h2>
          <p>Thank you for applying.</p>
          <p>You will be redirected to Reddit shortly.</p>

          <a href="https://www.reddit.com" class="button">Return to Reddit</a>
        </div>

        <script>
          setTimeout(() => {
            window.location.href = "https://www.reddit.com";
          }, 3000);
        </script>
        """
    )


# ---------------------------
# APPLICANTS — OWNER VIEW
# ---------------------------
@app.get("/applicants/{job_id}", response_class=HTMLResponse)
def view_applicants(
    job_id: int,
    secret: str,
    request: Request
):
    db: Session = SessionLocal()

    job = db.query(Job).filter_by(id=job_id, secret=secret).first()
    if not job:
        return HTMLResponse("<h2>Unauthorized</h2>", status_code=403)

    applicants = db.query(Applicant).filter_by(job_id=job_id).all()
    view = db.query(PageView).filter_by(job_id=job_id).first()
    page_views = view.count if view else 0

    return templates.TemplateResponse(
        "applicants.html",
        {
            "request": request,
            "job": job,
            "applicants": applicants,
            "page_views": page_views
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
