"""
Business: Admin panel operations - block/unblock users, delete accounts, view all users, manage admin rights, send notifications
Args: event - dict with httpMethod, body, queryStringParameters
      context - object with attributes: request_id, function_name
Returns: HTTP response dict with admin operation results
"""

import json
import os
from typing import Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    method: str = event.get('httpMethod', 'GET')
    
    # Handle CORS OPTIONS request
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, X-User-Id, X-Admin',
                'Access-Control-Max-Age': '86400'
            },
            'body': '',
            'isBase64Encoded': False
        }
    
    db_url = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Verify admin access
        headers = event.get('headers', {})
        admin_user_id = headers.get('X-User-Id') or headers.get('x-user-id')
        
        if not admin_user_id:
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Unauthorized'}),
                'isBase64Encoded': False
            }
        
        cursor.execute("SELECT is_admin FROM users WHERE user_id = %s", (admin_user_id,))
        admin_user = cursor.fetchone()
        
        if not admin_user or not admin_user['is_admin']:
            return {
                'statusCode': 403,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Admin access required'}),
                'isBase64Encoded': False
            }
        
        if method == 'GET':
            params = event.get('queryStringParameters', {})
            action = params.get('action')
            
            # Get all registered users
            if action == 'users':
                cursor.execute("""
                    SELECT user_id, username, is_admin, is_blocked, created_at
                    FROM users
                    ORDER BY created_at DESC
                """)
                users = cursor.fetchall()
                
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps([dict(user) for user in users], default=str),
                    'isBase64Encoded': False
                }
            
            # Get admin action logs
            elif action == 'logs':
                cursor.execute("""
                    SELECT id, admin_id, admin_name, action_type, target_user_id, 
                           target_user_name, description, created_at
                    FROM admin_actions
                    ORDER BY created_at DESC
                    LIMIT 50
                """)
                logs = cursor.fetchall()
                
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps([dict(log) for log in logs], default=str),
                    'isBase64Encoded': False
                }
            
            # Search user by ID
            elif action == 'search':
                search_user_id = params.get('user_id')
                cursor.execute(
                    "SELECT user_id, username, avatar_url, is_admin, is_blocked FROM users WHERE user_id = %s",
                    (search_user_id,)
                )
                user = cursor.fetchone()
                
                if not user:
                    return {
                        'statusCode': 404,
                        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                        'body': json.dumps({'error': 'User not found'}),
                        'isBase64Encoded': False
                    }
                
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps(dict(user)),
                    'isBase64Encoded': False
                }
        
        elif method == 'POST':
            body_data = json.loads(event.get('body', '{}'))
            action = body_data.get('action')
            target_user_id = body_data.get('user_id')
            
            # Block user
            if action == 'block':
                # Get target username
                cursor.execute("SELECT username FROM users WHERE user_id = %s", (target_user_id,))
                target_user = cursor.fetchone()
                
                cursor.execute("UPDATE users SET is_blocked = TRUE WHERE user_id = %s", (target_user_id,))
                
                # Log admin action
                cursor.execute("SELECT username FROM users WHERE user_id = %s", (admin_user_id,))
                admin = cursor.fetchone()
                cursor.execute(
                    "INSERT INTO admin_actions (admin_id, admin_name, action_type, target_user_id, target_user_name, description) VALUES (%s, %s, %s, %s, %s, %s)",
                    (admin_user_id, admin['username'], 'block', target_user_id, target_user.get('username') if target_user else 'Unknown', f"Blocked user {target_user_id}")
                )
                conn.commit()
                
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'status': 'blocked', 'user_id': target_user_id}),
                    'isBase64Encoded': False
                }
            
            # Unblock user
            elif action == 'unblock':
                cursor.execute("SELECT username FROM users WHERE user_id = %s", (target_user_id,))
                target_user = cursor.fetchone()
                
                cursor.execute("UPDATE users SET is_blocked = FALSE WHERE user_id = %s", (target_user_id,))
                
                cursor.execute("SELECT username FROM users WHERE user_id = %s", (admin_user_id,))
                admin = cursor.fetchone()
                cursor.execute(
                    "INSERT INTO admin_actions (admin_id, admin_name, action_type, target_user_id, target_user_name, description) VALUES (%s, %s, %s, %s, %s, %s)",
                    (admin_user_id, admin['username'], 'unblock', target_user_id, target_user.get('username') if target_user else 'Unknown', f"Unblocked user {target_user_id}")
                )
                conn.commit()
                
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'status': 'unblocked', 'user_id': target_user_id}),
                    'isBase64Encoded': False
                }
            
            # Grant admin rights
            elif action == 'grant_admin':
                cursor.execute("SELECT username FROM users WHERE user_id = %s", (target_user_id,))
                target_user = cursor.fetchone()
                
                cursor.execute("UPDATE users SET is_admin = TRUE WHERE user_id = %s", (target_user_id,))
                
                cursor.execute("SELECT username FROM users WHERE user_id = %s", (admin_user_id,))
                admin = cursor.fetchone()
                cursor.execute(
                    "INSERT INTO admin_actions (admin_id, admin_name, action_type, target_user_id, target_user_name, description) VALUES (%s, %s, %s, %s, %s, %s)",
                    (admin_user_id, admin['username'], 'grant_admin', target_user_id, target_user.get('username') if target_user else 'Unknown', f"Granted admin rights to {target_user_id}")
                )
                conn.commit()
                
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'status': 'admin_granted', 'user_id': target_user_id}),
                    'isBase64Encoded': False
                }
            
            # Revoke admin rights
            elif action == 'revoke_admin':
                cursor.execute("SELECT username FROM users WHERE user_id = %s", (target_user_id,))
                target_user = cursor.fetchone()
                
                cursor.execute("UPDATE users SET is_admin = FALSE WHERE user_id = %s", (target_user_id,))
                
                cursor.execute("SELECT username FROM users WHERE user_id = %s", (admin_user_id,))
                admin = cursor.fetchone()
                cursor.execute(
                    "INSERT INTO admin_actions (admin_id, admin_name, action_type, target_user_id, target_user_name, description) VALUES (%s, %s, %s, %s, %s, %s)",
                    (admin_user_id, admin['username'], 'revoke_admin', target_user_id, target_user.get('username') if target_user else 'Unknown', f"Revoked admin rights from {target_user_id}")
                )
                conn.commit()
                
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'status': 'admin_revoked', 'user_id': target_user_id}),
                    'isBase64Encoded': False
                }
            
            # Delete user account
            elif action == 'delete':
                cursor.execute("SELECT username FROM users WHERE user_id = %s", (target_user_id,))
                target_user = cursor.fetchone()
                
                cursor.execute("DELETE FROM messages WHERE sender_id = %s OR receiver_id = %s", (target_user_id, target_user_id))
                cursor.execute("DELETE FROM friend_requests WHERE sender_id = %s OR receiver_id = %s", (target_user_id, target_user_id))
                cursor.execute("DELETE FROM friends WHERE user_id = %s OR friend_id = %s", (target_user_id, target_user_id))
                cursor.execute("DELETE FROM typing_status WHERE user_id = %s OR chat_with_id = %s", (target_user_id, target_user_id))
                cursor.execute("DELETE FROM users WHERE user_id = %s", (target_user_id,))
                
                cursor.execute("SELECT username FROM users WHERE user_id = %s", (admin_user_id,))
                admin = cursor.fetchone()
                cursor.execute(
                    "INSERT INTO admin_actions (admin_id, admin_name, action_type, target_user_id, target_user_name, description) VALUES (%s, %s, %s, %s, %s, %s)",
                    (admin_user_id, admin['username'], 'delete', target_user_id, target_user.get('username') if target_user else 'Unknown', f"Deleted user {target_user_id}")
                )
                conn.commit()
                
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'status': 'deleted', 'user_id': target_user_id}),
                    'isBase64Encoded': False
                }
        
            # Send notification to all users
            elif action == 'notify_all':
                message = body_data.get('message')
                if not message:
                    return {
                        'statusCode': 400,
                        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                        'body': json.dumps({'error': 'Message is required'}),
                        'isBase64Encoded': False
                    }
                
                # Get all users except bots
                cursor.execute("SELECT user_id FROM users WHERE user_id != 'BOTDGO'")
                users = cursor.fetchall()
                
                # Send message from TeleDigo bot to all users
                for user in users:
                    cursor.execute(
                        "INSERT INTO messages (sender_id, receiver_id, message) VALUES (%s, %s, %s)",
                        ('BOTDGO', user['user_id'], f'📢 Уведомление от администрации:\n\n{message}')
                    )
                
                cursor.execute("SELECT username FROM users WHERE user_id = %s", (admin_user_id,))
                admin = cursor.fetchone()
                cursor.execute(
                    "INSERT INTO admin_actions (admin_id, admin_name, action_type, description) VALUES (%s, %s, %s, %s)",
                    (admin_user_id, admin['username'], 'notify_all', f"Sent notification to all users: {message[:50]}...")
                )
                conn.commit()
                
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'status': 'sent', 'recipients': len(users)}),
                    'isBase64Encoded': False
                }
        
        return {
            'statusCode': 405,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Method not allowed'}),
            'isBase64Encoded': False
        }
        
    finally:
        cursor.close()
        conn.close()