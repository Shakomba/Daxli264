from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Membership(db.Model):
    __tablename__ = "membership"
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    household_id = db.Column(db.Integer, db.ForeignKey("household.id"), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    email_verified = db.Column(db.Boolean, default=False, nullable=False)
    email_verification_token_hash = db.Column(db.String(64), nullable=True)
    email_verification_sent_at = db.Column(db.DateTime, nullable=True)
    password_reset_token_hash = db.Column(db.String(64), nullable=True)
    password_reset_sent_at = db.Column(db.DateTime, nullable=True)
    password_reset_expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Flask-Login requirements
    def is_active(self): return True
    def is_authenticated(self): return True
    def is_anonymous(self): return False
    def get_id(self): return str(self.id)

class Household(db.Model):
    __tablename__ = "household"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    join_code = db.Column(db.String(12), nullable=False, unique=True, index=True)
    # User who created the household (best-effort backfilled for older DBs)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class Expense(db.Model):
    __tablename__ = "expense"
    id = db.Column(db.Integer, primary_key=True)
    household_id = db.Column(db.Integer, db.ForeignKey("household.id"), nullable=False, index=True)
    payer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)

    title = db.Column(db.String(120), nullable=False)
    amount_iqd = db.Column(db.Integer, nullable=False)  # integer IQD
    expense_date = db.Column(db.String(10), nullable=False)  # YYYY-MM-DD

    is_archived = db.Column(db.Boolean, default=False, nullable=False, index=True)
    archived_month = db.Column(db.String(7), nullable=True, index=True)  # YYYY-MM

    # Group archived expenses by "settle" sessions.
    # When /settle is triggered, all active expenses get the same settle_id + settled_at.
    archived_settle_id = db.Column(db.String(24), nullable=True, index=True)
    archived_settled_at = db.Column(db.DateTime, nullable=True, index=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class ExpenseParticipant(db.Model):
    __tablename__ = "expense_participant"
    expense_id = db.Column(db.Integer, db.ForeignKey("expense.id"), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
