from enum import Enum

class AuthorisationSchema(Enum):
    BASIC = 'Basic'
    BEARER = 'OAuth'

class AuthorisationToken():
    def __init__(self, schema: AuthorisationSchema, value: str) -> None:
        self.schema = schema
        self.value = value
        self.user: str | None = None
        self.expiry: float | None = None
        self.reference: str | None = None
        self.role: str | None = None
