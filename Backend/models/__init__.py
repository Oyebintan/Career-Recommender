"""
Importing this package (e.g. `import models` in app.py) registers every
model class with SQLAlchemy's metadata, which is required before calling
db.create_all(). It also lets other modules do `from models import User`
as a shortcut instead of `from models.user import User`.
"""

from extensions import db
from models.user import User
from models.profile import Profile
from models.assessment import Assessment, AssessmentAnswer
from models.recommendation import Recommendation

__all__ = [
    "db",
    "User",
    "Profile",
    "Assessment",
    "AssessmentAnswer",
    "Recommendation",
]