-- Create admin actions log table
CREATE TABLE IF NOT EXISTS admin_actions (
    id SERIAL PRIMARY KEY,
    admin_id VARCHAR(6) NOT NULL,
    admin_name VARCHAR(255) NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    target_user_id VARCHAR(6),
    target_user_name VARCHAR(255),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster queries
CREATE INDEX idx_admin_actions_admin_id ON admin_actions(admin_id);
CREATE INDEX idx_admin_actions_created_at ON admin_actions(created_at DESC);