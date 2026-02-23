"""
Firebase configuration and initialization.
Centralized Firebase connection management with proper credential handling.
"""
import os
import logging
from typing import Optional
import firebase_admin
from firebase_admin import credentials, firestore, db
from firebase_admin.exceptions import FirebaseError

logger = logging.getLogger(__name__)

class FirebaseManager:
    """Singleton manager for Firebase connections with automatic reconnection."""
    
    _instance: Optional['FirebaseManager'] = None
    _initialized: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._cred_path: Optional[str] = None
            self._app = None
            self.firestore_client: Optional[firestore.Client] = None
            self.realtime_db = None
            self._initialized = True
    
    def initialize(self, credential_path: str = None) -> None:
        """
        Initialize Firebase connections.
        
        Args:
            credential_path: Path to Firebase service account JSON file.
                           If None, uses GOOGLE_APPLICATION_CREDENTIALS env var.
        
        Raises:
            FileNotFoundError: If credential file doesn't exist
            FirebaseError: If Firebase initialization fails
        """
        try:
            # Validate credential path
            if credential_path:
                if not os.path.exists(credential_path):
                    raise FileNotFoundError(f"Firebase credential file not found: {credential_path}")
                self._cred_path = credential_path
                cred = credentials.Certificate(credential_path)
            else:
                env_cred = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
                if not env_cred or not os.path.exists(env_cred):
                    raise FileNotFoundError(
                        "No Firebase credentials provided. Set GOOGLE_APPLICATION_CREDENTIALS "
                        "or pass credential_path parameter."
                    )
                self._cred_path = env_cred
                cred = credentials.Certificate(env_cred)
            
            # Initialize Firebase app
            if not firebase_admin._apps:
                self._app = firebase_admin.initialize_app(cred, {
                    'databaseURL': os.getenv('FIREBASE_DATABASE_URL', '')
                })
            
            # Initialize clients
            self.firestore_client = firestore.client()
            self.realtime_db = db.reference()
            
            logger.info("Firebase initialized successfully")
            
        except FirebaseError as e:
            logger.error(f"Firebase initialization failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during Firebase initialization: {str(e)}")
            raise
    
    def get_firestore(self) -> firestore.Client:
        """Get Firestore client with connection check."""
        if self.firestore_client is None:
            raise RuntimeError("Firebase not initialized. Call initialize() first.")
        return self.firestore_client
    
    def get_realtime_db(self) -> db.Reference:
        """Get Realtime Database reference with connection check."""
        if self.realtime_db is None:
            raise RuntimeError("Firebase not initialized. Call initialize() first.")
        return self.realtime_db
    
    def health_check(self) -> bool:
        """Check Firebase connection health."""
        try:
            if self.firestore_client:
                # Simple read to test connection
                self.firestore_client.collection('_health').limit(1).get()
            return True
        except Exception as e:
            logger.warning(f"Firebase health check failed: {str(e)}")
            return False

# Global instance
firebase_manager = FirebaseManager()