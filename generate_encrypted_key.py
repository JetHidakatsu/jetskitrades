from env.key_manager import KeyManager
import os

def main():
    key_manager = KeyManager()
    new_private_key = KeyManager.generate_new_private_key()
    encrypted_private_key = key_manager.generate_encrypted_private_key(new_private_key)
    
    print(f"New private key (keep this secret!): {new_private_key}")
    print(f"Encrypted private key: {encrypted_private_key}")
    
    # Update .env file
    env_path = os.path.join(os.getcwd(), '.env')
    with open(env_path, 'r') as file:
        lines = file.readlines()
    
    with open(env_path, 'w') as file:
        for line in lines:
            if line.startswith('ENCRYPTED_PRIVATE_KEY='):
                file.write(f'ENCRYPTED_PRIVATE_KEY={encrypted_private_key}\n')
            else:
                file.write(line)
    
    print(f"Updated .env file with new ENCRYPTED_PRIVATE_KEY")

if __name__ == "__main__":
    main()
