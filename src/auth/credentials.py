"""Credential management with encryption support"""

from cryptography.fernet import Fernet
import os
from typing import Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class CredentialManager:
    """
    Manages encrypted credentials for SevOne authentication
    
    Features:
    - Load credentials from .env file
    - Decrypt password using Fernet symmetric encryption
    - Provide credentials to authentication manager
    """
    
    def __init__(self):
        self.encryption_key = os.getenv("SEVONE_ENCRYPTION_KEY")
        if not self.encryption_key:
            raise ValueError("SEVONE_ENCRYPTION_KEY not found in environment")
        
        self.fernet = Fernet(self.encryption_key.encode())
    
    def get_credentials(self) -> Tuple[str, str, str]:
        """
        Load and decrypt SevOne credentials
        
        Returns:
            Tuple[hostname, username, decrypted_password]
        
        Raises:
            ValueError: If required environment variables are missing
        """
        hostname = os.getenv("SEVONE_HOSTNAME")
        username = os.getenv("SEVONE_USERNAME")
        encrypted_password = os.getenv("SEVONE_PASSWORD_ENCRYPTED")
        
        if not all([hostname, username, encrypted_password]):
            raise ValueError("Missing required SevOne credentials in .env")
        
        # Decrypt password
        try:
            decrypted_password = self.fernet.decrypt(
                encrypted_password.encode()
            ).decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt password: {str(e)}")
        
        return hostname, username, decrypted_password
    
    @staticmethod
    def encrypt_password(password: str, encryption_key: str) -> str:
        """
        Utility method to encrypt a password
        
        Args:
            password: Plain text password
            encryption_key: Fernet encryption key
        
        Returns:
            Encrypted password as string
        """
        fernet = Fernet(encryption_key.encode())
        encrypted = fernet.encrypt(password.encode())
        return encrypted.decode()
    
    @staticmethod
    def generate_key() -> str:
        """
        Generate a new Fernet encryption key
        
        Returns:
            New encryption key as string
        """
        return Fernet.generate_key().decode()

# Made with Bob
