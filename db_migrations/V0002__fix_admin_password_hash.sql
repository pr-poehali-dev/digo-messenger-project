-- Fix admin account password hash to use SHA256
UPDATE users SET password_hash = '8b5e8f3e4d5c6a7b9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b6c' WHERE username = 'Digo';
