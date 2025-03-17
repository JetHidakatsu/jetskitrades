import os
import secrets
from env.key_manager import KeyManager

def generate_private_key():
    return secrets.token_bytes(32)

def public_key_from_private(private_key):
    # This is a placeholder. In a real scenario, you'd use the Solana SDK to derive the public key.
    return private_key[:32].hex()

def main():
    key_manager = KeyManager()
    
    # Generate a new private key
    private_key = generate_private_key()
    private_key_hex = private_key.hex()
    public_key = public_key_from_private(private_key)

    encrypted_private_key = key_manager.generate_encrypted_private_key(private_key_hex)
    
    print(f"New public key: {public_key}")
    print(f"New private key (keep this secret!): {private_key_hex}")
    print(f"Encrypted private key: {encrypted_private_key}")
    
    # Update .env file
    env_path = os.path.join(os.getcwd(), '.env')
    with open(env_path, 'r') as file:
        lines = file.readlines()
    
    with open(env_path, 'w') as file:
        for line in lines:
            if line.startswith('ENCRYPTED_PRIVATE_KEY='):
                file.write(f'ENCRYPTED_PRIVATE_KEY={encrypted_private_key}\n')
            elif line.startswith('WALLET_PUBLIC_KEY='):
                file.write(f'WALLET_PUBLIC_KEY={public_key}\n')
            else:
                file.write(line)
    
    print(f"Updated .env file with new ENCRYPTED_PRIVATE_KEY and WALLET_PUBLIC_KEY")

if __name__ == "__main__":
    main()
