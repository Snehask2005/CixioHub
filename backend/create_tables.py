from app.db.database import engine, Base
from app.models.user import User
from app.models.notification import Notification


Base.metadata.create_all(bind=engine)

print("Tables created")