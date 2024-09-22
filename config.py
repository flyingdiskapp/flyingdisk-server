class Config:
    ALLOW_INSTALLATION = True
    ALLOW_LOGIN = True
    ALLOW_REGISTRATION = False
    ALLOW_PUBLISHING_NEW_PACKAGES = True
    ALLOW_PUBLISHING_NEW_RELEASES = True
    REQUIRE_ADMIN_TO_INSTALL = False
    REQUIRE_ADMIN_TO_PUBLISH = True
    REQUIRE_LOGIN_TO_INSTALL = False

    SECRET_KEY = 'changeme'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///flyingdiskrepo.db'