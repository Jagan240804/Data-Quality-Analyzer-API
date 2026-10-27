import pandas as pd
from flask import Blueprint, jsonify, request
from .models import db, Dataset
from .quality import analyze

api = Blueprint("api", __name__)


@api.get("/health")
def health():
    return jsonify(status="ok")


@api.post("/datasets")
def upload_dataset():
    """Upload a CSV file (form field 'file'); it is analyzed and the report is stored."""
    file = request.files.get("file")
    if file is None or file.filename == "":
        return jsonify(error="No file provided. Send a CSV as form field 'file'"), 400
    if not file.filename.lower().endswith(".csv"):
        return jsonify(error="Only .csv files are supported"), 400

    try:
        df = pd.read_csv(file)
        report = analyze(df)
    except (pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeDecodeError, ValueError) as exc:
        return jsonify(error=f"Could not process file: {exc}"), 400

    dataset = Dataset(
        filename=file.filename,
        rows=report["rows"],
        columns=report["columns"],
        quality_score=report["scores"]["overall"],
        report=report,
    )
    db.session.add(dataset)
    db.session.commit()
    return jsonify(dataset.summary()), 201


@api.get("/datasets")
def list_datasets():
    """List datasets with pagination and optional minimum score filter."""
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 50)
    query = Dataset.query.order_by(Dataset.uploaded_at.desc())
    min_score = request.args.get("min_score", type=float)
    if min_score is not None:
        query = query.filter(Dataset.quality_score >= min_score)
    result = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify(
        items=[d.summary() for d in result.items],
        page=result.page,
        total=result.total,
        pages=result.pages,
    )


@api.get("/datasets/<int:dataset_id>")
def get_dataset(dataset_id):
    return jsonify(db.get_or_404(Dataset, dataset_id).summary())


@api.get("/datasets/<int:dataset_id>/report")
def get_report(dataset_id):
    dataset = db.get_or_404(Dataset, dataset_id)
    return jsonify(dataset=dataset.summary(), report=dataset.report)


@api.delete("/datasets/<int:dataset_id>")
def delete_dataset(dataset_id):
    dataset = db.get_or_404(Dataset, dataset_id)
    db.session.delete(dataset)
    db.session.commit()
    return "", 204
