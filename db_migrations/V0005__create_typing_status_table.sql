-- Create typing status table for real-time typing indicators
CREATE TABLE IF NOT EXISTS typing_status (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(6) NOT NULL,
    chat_with_id VARCHAR(6) NOT NULL,
    is_typing BOOLEAN DEFAULT FALSE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, chat_with_id)
);

CREATE INDEX IF NOT EXISTS idx_typing_chat_with ON typing_status(chat_with_id);
