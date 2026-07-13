#!/usr/bin/env python3
"""
Utility script to encrypt SevOne password for .env file

Usage:
    python scripts/encrypt_password.py
"""

from cryptography.fernet import Fernet
import getpass
import sys


def generate_key():
    """Generate a new Fernet encryption key"""
    return Fernet.generate_key().decode()


def encrypt_password(password: str, key: str) -> str:
    """Encrypt password using Fernet"""
    fernet = Fernet(key.encode())
    encrypted = fernet.encrypt(password.encode())
    return encrypted.decode()


def main():
    print("=" * 60)
    print("SevOne Password Encryption Utility")
    print("=" * 60)
    print()
    
    # Check if key exists
    print("Do you have an encryption key? (y/n)")
    has_key = input().strip().lower()
    
    if has_key == 'y':
        print("\nEnter your encryption key:")
        key = input().strip()
        if not key:
            print("❌ Error: Encryption key cannot be empty")
            sys.exit(1)
    else:
        print("\nGenerating new encryption key...")
        key = generate_key()
        print(f"\n{'=' * 60}")
        print("Your encryption key (save this in .env as SEVONE_ENCRYPTION_KEY):")
        print(f"{'=' * 60}")
        print(key)
        print(f"{'=' * 60}")
        print("\n⚠️  IMPORTANT: Save this key securely!")
        print("   You'll need it to decrypt the password.")
        print()
    
    # Get password
    print("\nEnter SevOne password to encrypt:")
    password = getpass.getpass()
    
    if not password:
        print("❌ Error: Password cannot be empty")
        sys.exit(1)
    
    # Encrypt
    try:
        encrypted = encrypt_password(password, key)
        print("\n✅ Password encrypted successfully!")
        print(f"\n{'=' * 60}")
        print("Add this to your .env file as SEVONE_PASSWORD_ENCRYPTED:")
        print(f"{'=' * 60}")
        print(encrypted)
        print(f"{'=' * 60}")
        print()
        
        # Show example .env content
        print("Example .env file content:")
        print("-" * 60)
        print("SEVONE_HOSTNAME=your-sevone-hostname.com")
        print("SEVONE_USERNAME=your-username")
        print(f"SEVONE_PASSWORD_ENCRYPTED={encrypted}")
        print(f"SEVONE_ENCRYPTION_KEY={key}")
        print("SEVONE_VERIFY_SSL=false")
        print("LOG_LEVEL=INFO")
        print("-" * 60)
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob
