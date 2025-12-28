import os
import firebase_admin
from firebase_admin import auth, credentials
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

load_dotenv()

import logging

logger = logging.getLogger(__name__)

# Initialize Firebase Admin
try:
    # Try to get existing app (hot reload safety)
    app = firebase_admin.get_app()
except ValueError:
    try:
        # Initialize with Application Default Credentials (ADC)
        # BUT force the projectID to match the frontend (env var), ignoring the ADC's default "quota project".
        project_id = os.getenv("NEXT_PUBLIC_FIREBASE_PROJECT_ID")
        options = {}
        if project_id:
            options['projectId'] = project_id
            
        app = firebase_admin.initialize_app(options=options) 
        logger.info(f"Firebase Admin Initialized with ADC for project: {project_id}")
    except Exception as e:
        logger.error(f"CRITICAL: Firebase Admin initialization failed: {e}")
        # If this fails, the app cannot verify tokens.
        # We allow it to continue so uvicorn doesn't crash loop if creds are transiently missing,
        # but usage will 500/401.
        pass

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Verifies the Firebase ID token and returns the decoded token dict (including uid, email, etc).
    """
    token = credentials.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        logger.error(f"CRITICAL AUTH ERROR: {e}")
        # logger.error(f"Token: {dict(credentials.credentials)[:10] if credentials else 'None'}...") # Safer logging
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

from sqlalchemy.ext.asyncio import AsyncSession
from . import crud, schemas, models
from .database import get_db

async def get_current_user(
    token: dict = Depends(verify_token), 
    db: AsyncSession = Depends(get_db)
) -> models.User:
    uid = token['uid']
    email = token.get('email', f"{uid}@placeholder.com")
    
    user = await crud.get_user(db, uid)
    if not user:
        # Create user with REAL email from token
        user_create = schemas.UserCreate(id=uid, email=email)
        user = await crud.create_user_if_not_exists(db, user_create)
    elif user.email != email and "placeholder.com" in user.email:
        # Update placeholder email to real email if it changed (and was placeholder)
        # This fixes the "wrong email" issue for existing users
        user.email = email
        await db.commit()
        await db.refresh(user)
        
    return user
