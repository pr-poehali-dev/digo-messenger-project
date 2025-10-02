-- Create TeleDigo bot account
INSERT INTO users (user_id, username, password_hash, is_admin, is_blocked)
VALUES ('BOTDGO', 'TeleDigo', 'bot_no_password', FALSE, FALSE)
ON CONFLICT (user_id) DO NOTHING;