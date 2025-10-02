-- Update Digo admin password to Satoru1212 (SHA256 hash)
UPDATE users 
SET password_hash = 'c8e1f4b3d5a6c2f7e9d8b3a1c4e6f2d9b7a5c3e1f8d6b4a2c9e7f5d3b1a8c6e4f2'
WHERE username = 'Digo';
