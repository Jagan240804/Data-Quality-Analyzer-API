from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Dataset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    rows = db.Column(db.Integer, nullable=False)
    columns = db.Column(db.Integer, nullable=False)
    quality_score = db.Column(db.Float, nullable=False)
    report = db.Column(db.JSON, nullable=False)

    def summary(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "uploaded_at": self.uploaded_at.isoformat(),
            "rows": self.rows,
            "columns": self.columns,
            "quality_score": self.quality_score,
        }
