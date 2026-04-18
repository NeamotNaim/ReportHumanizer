from app import app
from extensions import db
from models.user import User
from models.document import Document


def init_database():
    with app.app_context():
        db.create_all()
        print("Database initialized successfully!")
        print("Tables created:")
        print("- users")
        print("- documents")


if __name__ == '__main__':
    init_database()
