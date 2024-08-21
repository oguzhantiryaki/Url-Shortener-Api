import base64
from datetime import datetime
from hashlib import md5

import redis
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import func
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from config.db import get_db
from models.index import Url as DbUrl, User as DbUser, UrlLog
from schemas.index import Url
from .auth import get_username_from_token

url = APIRouter(prefix="/url")

oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
r = redis.Redis(host='localhost', port=6379, db=0, encoding="utf-8", decode_responses=True)


@url.post("/")
def create_short_url(url: str, db: Session = Depends(get_db), token: str = Depends(oauth_2_scheme)):
    if not url:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="URL cannot be empty")

    username = get_username_from_token(token)

    db_user = db.query(DbUser).filter(DbUser.username == username).first()
    today = datetime.now().date()
    if db_user.lastUrlCreateDate.date() < today:
        db_user.lastUrlCreateDate = today
        db_user.dailyCreatedUrl = 1
    elif db_user.dailyCreatedUrl < 50:
        db_user.dailyCreatedUrl += 1
    else:
        raise HTTPException(status_code=403, detail="Daily URL shortening limit exceeded.")

    short_url = shorten_url(url, db)
    db_url = DbUrl(orginalUrl=url, shortUrl=short_url)
    db.add(db_url)
    db.add(db_user)
    db.commit()
    return short_url


@url.get("/shorturl/{shortUrlHash}")
def redirect_orginal_url(shortUrlHash: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    short_url = f"localhost:8000/url/shorturl/{shortUrlHash}"
    orginal_url = r.get(f"{shortUrlHash}")
    if orginal_url is None:
        db_url = db.query(DbUrl).filter(DbUrl.shortUrl == short_url).first()
        if db_url is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found in the database")

        r.set(f"{shortUrlHash}", db_url.orginalUrl)
        background_tasks.add_task(add_url_log, db, short_url)
        return RedirectResponse(url=db_url.orginalUrl)
    else:
        background_tasks.add_task(add_url_log, db, short_url)
        return RedirectResponse(url=orginal_url)


@url.get("/statistic")
def get_statistics(short_url: str, db: Session = Depends(get_db), token: str = Depends(oauth_2_scheme)):
    if not short_url:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Short URL cannot be empty")
    return get_all_stats(short_url, db)


def shorten_url(url: str, db: Session):
    hash_value = md5(str(url + str(datetime.now())).encode()).digest()[-4:]
    hash_value = base64.urlsafe_b64encode(hash_value).decode().rstrip('_-=\n')
    return f"localhost:8000/url/shorturl/{hash_value}"


def add_url_log(db: Session, short_url: str):
    log = UrlLog(shortUrl=short_url)
    db.add(log)
    db.commit()


def get_all_stats(short_url: str, db: Session):
    today = datetime.now().date()

    start_of_today = datetime.combine(today, datetime.min.time())
    daily_count = db.query(func.count(UrlLog.id)).filter(
        UrlLog.shortUrl == short_url, UrlLog.accessDate >= start_of_today
    ).scalar()

    start_of_month = today.replace(day=1)
    monthly_count = db.query(func.count(UrlLog.id)).filter(
        UrlLog.shortUrl == short_url, UrlLog.accessDate >= start_of_month
    ).scalar()

    total_count = db.query(func.count(UrlLog.id)).filter(
        UrlLog.shortUrl == short_url
    ).scalar()

    return {
        "daily_count": daily_count,
        "monthly_count": monthly_count,
        "total_count": total_count
    }