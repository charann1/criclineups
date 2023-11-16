from hashlib import md5
from datetime import datetime
from flask import current_app
from app.extensions import db
from app.auth.email import send_email
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer
from werkzeug.security import generate_password_hash, check_password_hash


class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    EDIT = 8
    ADMIN = 16


class Token(db.Model):
    __tablename__ = "tokens"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(512), index=True)
    type = db.Column(db.String(128), nullable=False, index=True)
    expired = db.Column(db.Boolean, nullable=False, default=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __init__(self, owner, type):
        self.owner = owner
        self.type = type

    def serialize_token(self, expiration=3600, **kwargs):
        if not kwargs:
            kwargs = {"user_id": self.owner.id}
        private_key = current_app.config["SECRET_KEY"]
        serializer = TimedJSONWebSignatureSerializer(private_key, expiration)
        token = serializer.dumps(kwargs).decode("utf-8")
        self.key = token

    @staticmethod
    def deserialize_token(token):
        private_key = TimedJSONWebSignatureSerializer(
            current_app.config["SECRET_KEY"])
        try:
            decoded_payload = private_key.loads(token)
            return decoded_payload
        except Exception:
            return {}

    @staticmethod
    def disable_tokens(token):
        for t in token.owner.tokens:
            if t.type == token.type and t != token:
                t.expired = True
        db.session.commit()

    @classmethod
    def delete_tokens(cls):
        dq = cls.__table__.delete().where(cls.expired)
        db.session.execute(dq)
        db.session.commit()


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship("User", backref="role", lazy="dynamic")

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def add_permission(self, permission):
        if not self.has_permission(permission):
            self.permissions += permission

    def remove_permission(self, permission):
        if self.has_permission(permission):
            self.permissions -= permission

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, permission):
        return self.permissions & permission == permission

    def __repr__(self):
        return "<Role %r>" % self.name

    @classmethod
    def get_roles(cls):
        return cls.query.all()

    @classmethod
    def insert_roles(cls):
        roles = {
            "Member": (Permission.FOLLOW, Permission.COMMENT),
            "Author": (Permission.FOLLOW, Permission.COMMENT, Permission.WRITE),
            "Editor": (
                Permission.FOLLOW,
                Permission.COMMENT,
                Permission.WRITE,
                Permission.EDIT,
            ),
            "Administrator": (
                Permission.FOLLOW,
                Permission.COMMENT,
                Permission.WRITE,
                Permission.EDIT,
                Permission.ADMIN,
            ),
        }
        default_role = "Member"
        for r in roles:
            role = cls.query.filter_by(name=r).first()
            if role is None:
                role = cls(name=r)
            role.reset_permissions()
            for p in roles[r]:
                role.add_permission(p)
            role.default = role.name == default_role
            db.session.add(role)
        db.session.commit()


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, info={"label": "Name"})
    email = db.Column(
        db.String(255),
        unique=True,
        index=True,
        nullable=False,
        info={"label": "Email"},
    )
    password_hash = db.Column(
        db.String(128), nullable=False, server_default="")
    active = db.Column("is_active", db.Boolean(),
                       nullable=False, server_default="1")
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
    confirmed = db.Column(db.Boolean, default=False)
    tokens = db.relationship("Token", backref="owner", lazy="dynamic")
    # Activity
    sign_in_count = db.Column(db.Integer, nullable=False, default=0)
    current_sign_in_on = db.Column(db.DateTime(), default=datetime.utcnow)
    current_sign_in_ip = db.Column(db.String(45))
    last_sign_in_on = db.Column(db.DateTime(), default=datetime.utcnow)
    last_sign_in_ip = db.Column(db.String(45))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email in current_app.config["ADMINS"]:
                self.role = Role.query.filter_by(name="Administrator").first()
            else:
                self.role = Role.query.filter_by(default=True).first()

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def encrypt_password(self, password):
        self.password_hash = generate_password_hash(password)

    def authenticated(self, password):
        return check_password_hash(self.password_hash, password)

    def is_active(self):
        return self.active

    def ping(self, ip):
        self.sign_in_count += 1
        self.current_sign_in_on = datetime.utcnow()
        self.current_sign_in_ip = ip
        self.last_sign_in_on = datetime.utcnow()
        self.last_sign_in_ip = self.current_sign_in_ip
        db.session.commit()

    def avatar(self, size):
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return "https://www.gravatar.com/avatar/{}?d=identicon&s={}".format(
            digest, size
        )

    def initialize_email_request(self, email, subject, template):
        ctx = {"user_id": self.id, "email": email}
        token = Token(self, "email")
        Token.disable_tokens(token)
        token.serialize_token(**ctx)
        db.session.add(token)
        db.session.commit()
        send_email(
            subject=subject,
            to=email,
            template=template,
            ctx={"user": self, "token": token.key},
            async_mail=False,
        )

    def initialize_password_request(self):
        token = Token(self, "password")
        Token.disable_tokens(token)
        token.serialize_token()
        db.session.add(token)
        db.session.commit()
        send_email(
            subject="Reset Your Password",
            to=self.email,
            template="auth/mail/recovery",
            ctx={"user": self, "token": token.key},
            async_mail=False,
        )

    def __repr__(self):
        return "<User {}>".format(self.name)

    @classmethod
    def find_by_email(cls, identity):
        return cls.query.filter(cls.email == identity).first()
