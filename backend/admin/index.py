"""
Business: Admin panel operations - block/unblock users, delete accounts, view all users, manage admin rights
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
                cursor.execute("UPDATE users SET is_blocked = TRUE WHERE user_id = %s", (target_user_id,))
                conn.commit()
                
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'status': 'blocked', 'user_id': target_user_id}),
                    'isBase64Encoded': False
                }
            
            # Unblock user
            elif action == 'unblock':
                cursor.execute("UPDATE users SET is_blocked = FALSE WHERE user_id = %s", (target_user_id,))
                conn.commit()
                
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'status': 'unblocked', 'user_id': target_user_id}),
                    'isBase64Encoded': False
                }
            
            # Grant admin rights
            elif action == 'grant_admin':
                cursor.execute("UPDATE users SET is_admin = TRUE WHERE user_id = %s", (target_user_id,))
                conn.commit()
                
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'status': 'admin_granted', 'user_id': target_user_id}),
                    'isBase64Encoded': False
                }
            
            # Revoke admin rights
            elif action == 'revoke_admin':
                cursor.execute("UPDATE users SET is_admin = FALSE WHERE user_id = %s", (target_user_id,))
                conn.commit()
                
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'status': 'admin_revoked', 'user_id': target_user_id}),
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
