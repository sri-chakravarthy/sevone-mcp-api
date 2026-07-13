"""Tests for credential management"""

import pytest
from cryptography.fernet import Fernet
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from auth.credentials import CredentialManager


def test_generate_key():
    """Test encryption key generation"""
    key = CredentialManager.generate_key()
    assert key is not None
    assert len(key) > 0
    
    # Verify it's a valid Fernet key
    fernet = Fernet(key.encode())
    assert fernet is not None


def test_encrypt_decrypt_password():
    """Test password encryption and decryption"""
    password = "test_password_123"
    key = CredentialManager.generate_key()
    
    # Encrypt
    encrypted = CredentialManager.encrypt_password(password, key)
    assert encrypted != password
    assert len(encrypted) > 0
    
    # Decrypt
    fernet = Fernet(key.encode())
    decrypted = fernet.decrypt(encrypted.encode()).decode()
    assert decrypted == password


def test_encrypt_password_different_keys():
    """Test that different keys produce different encrypted values"""
    password = "test_password_123"
    key1 = CredentialManager.generate_key()
    key2 = CredentialManager.generate_key()
    
    encrypted1 = CredentialManager.encrypt_password(password, key1)
    encrypted2 = CredentialManager.encrypt_password(password, key2)
    
    assert encrypted1 != encrypted2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# Made with Bob
