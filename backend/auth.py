import os
import firebase_admin
from firebase_admin import auth, credentials
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

load_dotenv()

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
        print(f"Firebase Admin Initialized with ADC for project: {project_id}")
    except Exception as e:
        print(f"CRITICAL: Firebase Admin initialization failed: {e}")
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
        print(f"CRITICAL AUTH ERROR: {e}")
        print(f"Token: {token[:10]}...{token[-10:]}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}", # Creating visibility in frontend response too
            headers={"WWW-Authenticate": "Bearer"},
        )
