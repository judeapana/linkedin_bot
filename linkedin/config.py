class LocalConfig:
    DEBUG = True
    ENV = 'development'
    SECRET_KEY = '67ad41191a14125b92a988d6f1a8112a8b9f20a4'


class ProductionConfig(LocalConfig):
    DEBUG = False
    ENV = 'production'


class TestingConfig(LocalConfig):
    DEBUG = True
    TESTING = True
    ENV = 'testing'
