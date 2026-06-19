from datetime import datetime


def is_expired(user):

    if not user.expiry_date:
        return True

    return datetime.utcnow() > user.expiry_date


def file_limit_reached(user):

    if user.file_limit == -1:
        return False

    return user.files_used >= user.file_limit
