class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite3'
    SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AWS_ACCESS_KEY_ID = "" # your aws access key id
    AWS_SECRET_ACCESS_KEY = "" # your aws secret access key
    S3_BUCKET = "" # youtr S3 Bucket Name