import os
import base64
import getpass
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import json
from pathlib import Path
from typing import Dict, Optional

class SecretsManager:
    """Secure storage and management of sensitive configuration data"""
    
    def __init__(self, secrets_file: str = ".env"):
        self.secrets_file = secrets_file
        self.salt_file = ".salt"
        self._fernet = None
        self._ensure_salt()

    def _ensure_salt(self):
        """Ensure salt exists or create new one"""
        if not os.path.exists(self.salt_file):
            salt = os.urandom(16)
            with open(self.salt_file, "wb") as f:
                f.write(salt)

    def _get_salt(self) -> bytes:
        """Get salt from file"""
        with open(self.salt_file, "rb") as f:
            return f.read()

    def _init_encryption(self, password: str):
        """Initialize encryption with password"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self._get_salt(),
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        self._fernet = Fernet(key)

    def _encrypt(self, data: str) -> bytes:
        """Encrypt data"""
        if not self._fernet:
            raise ValueError("Encryption not initialized")
        return self._fernet.encrypt(data.encode())

    def _decrypt(self, data: bytes) -> str:
        """Decrypt data"""
        if not self._fernet:
            raise ValueError("Encryption not initialized")
        return self._fernet.decrypt(data).decode()

    def store_secrets(self, secrets: Dict[str, str], password: Optional[str] = None):
        """Securely store secrets"""
        if password is None:
            password = getpass.getpass("Enter encryption password: ")
            confirm = getpass.getpass("Confirm encryption password: ")
            if password != confirm:
                raise ValueError("Passwords do not match")

        self._init_encryption(password)
        
        # Encrypt secrets
        encrypted_data = {}
        for key, value in secrets.items():
            encrypted_data[key] = base64.b64encode(
                self._encrypt(value)
            ).decode()

        # Store encrypted data
        with open(self.secrets_file, "w") as f:
            for key, value in encrypted_data.items():
                f.write(f"{key}={value}\n")

        print(f"Secrets securely stored in {self.secrets_file}")

    def load_secrets(self, password: Optional[str] = None) -> Dict[str, str]:
        """Load and decrypt secrets"""
        if not os.path.exists(self.secrets_file):
            raise FileNotFoundError(f"Secrets file {self.secrets_file} not found")

        if password is None:
            password = getpass.getpass("Enter decryption password: ")

        self._init_encryption(password)
        
        secrets = {}
        try:
            with open(self.secrets_file, "r") as f:
                for line in f:
                    if "=" in line:
                        key, encrypted_value = line.strip().split("=", 1)
                        encrypted_bytes = base64.b64decode(encrypted_value)
                        secrets[key] = self._decrypt(encrypted_bytes)
            return secrets
        except Exception as e:
            raise ValueError(f"Failed to decrypt secrets: {e}")

    def update_secret(self, key: str, value: str, password: Optional[str] = None):
        """Update a single secret"""
        current_secrets = self.load_secrets(password)
        current_secrets[key] = value
        self.store_secrets(current_secrets, password)

    def remove_secret(self, key: str, password: Optional[str] = None):
        """Remove a single secret"""
        current_secrets = self.load_secrets(password)
        if key in current_secrets:
            del current_secrets[key]
            self.store_secrets(current_secrets, password)

def main():
    """CLI interface for secrets management"""
    manager = SecretsManager()
    
    # Example secrets to store
    default_secrets = {
        "QUICKNODE_RPC_URL": "",
        "PRIVATE_KEY": "",
        "WALLET_ADDRESS": "",
    }
    
    try:
        # Check if secrets file exists
        if not os.path.exists(manager.secrets_file):
            print("No secrets file found. Let's set up your configuration.")
            secrets = {}
            for key in default_secrets:
                value = getpass.getpass(f"Enter {key}: ")
                secrets[key] = value
            
            password = getpass.getpass("Create encryption password: ")
            confirm = getpass.getpass("Confirm encryption password: ")
            
            if password != confirm:
                raise ValueError("Passwords do not match")
                
            manager.store_secrets(secrets, password)
            print("Configuration securely stored!")
            
        else:
            # Load existing secrets
            try:
                password = getpass.getpass("Enter decryption password: ")
                secrets = manager.load_secrets(password)
                print("Current configuration:")
                for key in secrets:
                    masked_value = "****" + secrets[key][-4:] if secrets[key] else ""
                    print(f"{key}: {masked_value}")
                    
            except ValueError as e:
                print(f"Error loading secrets: {e}")
                return
                
            # Update secrets if needed
            update = input("Would you like to update any values? (y/n): ").lower()
            if update == 'y':
                for key in secrets:
                    update_key = input(f"Update {key}? (y/n): ").lower()
                    if update_key == 'y':
                        value = getpass.getpass(f"Enter new {key}: ")
                        manager.update_secret(key, value, password)
                print("Configuration updated!")
                
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
