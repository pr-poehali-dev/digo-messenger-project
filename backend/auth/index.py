"""
Business: User registration, login, and authentication for Digo messenger
Args: event - dict with httpMethod, body, queryStringParameters
      context - object with attributes: request_id, function_name
Returns: HTTP response dict with user data or error
"""

import json
import os
import random
from typing import Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
import hashlib

def generate_user_id(cursor) -> str:
    """Generate unique 6-digit user ID"""
    while True:
        user_id = f"{random.randint(100000, 999999):06d}"
        cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
        if not cursor.fetchone():
            return user_id

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    method: str = event.get('httpMethod', 'GET')
    
    # Handle CORS OPTIONS request
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, X-User-Id, X-Auth-Token',
                'Access-Control-Max-Age': '86400'
            },
            'body': '',
            'isBase64Encoded': False
        }
    
    db_url = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        if method == 'POST':
            body_data = json.loads(event.get('body', '{}'))
            action = body_data.get('action')
            
            # Registration
            if action == 'register':
                username = body_data.get('username')
                password = body_data.get('password')
                
                if not username or not password:
                    return {
                        'statusCode': 400,
                        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                        'body': json.dumps({'error': 'Username and password required'}),
                        'isBase64Encoded': False
                    }
                
                # Check if username exists
                cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
                if cursor.fetchone():
                    return {
                        'statusCode': 400,
                        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                        'body': json.dumps({'error': 'Username already exists'}),
                        'isBase64Encoded': False
                    }
                
                # Create new user
                user_id = generate_user_id(cursor)
                password_hash = hash_password(password)
                
                cursor.execute(
                    "INSERT INTO users (user_id, username, password_hash) VALUES (%s, %s, %s) RETURNING user_id, username, is_admin",
                    (user_id, username, password_hash)
                )
                user = cursor.fetchone()
                conn.commit()
                
                # Send welcome message from TeleDigo bot
                cursor.execute(
                    "INSERT INTO messages (sender_id, receiver_id, message) VALUES (%s, %s, %s)",
                    ('BOTDGO', user_id, f'Добро пожаловать в Digo, {username}! 🚀\n\nЯ TeleDigo - твой персональный ассистент. Я буду уведомлять тебя о входах в аккаунт и важных событиях.\n\nТвой ID: {user_id}')
                )
                
                # Create friendship with bot
                cursor.execute(
                    "INSERT INTO friends (user_id, friend_id) VALUES (%s, %s), (%s, %s)",
                    (user_id, 'BOTDGO', 'BOTDGO', user_id)
                )
                conn.commit()
                
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({
                        'user_id': user['user_id'],
                        'username': user['username'],
                        'is_admin': user['is_admin']
                    }),
                    'isBase64Encoded': False
                }
            
            # Login
            elif action == 'login':
                username = body_data.get('username')
                password = body_data.get('password')
                
                if not username or not password:
                    return {
                        'statusCode': 400,
                        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                        'body': json.dumps({'error': 'Username and password required'}),
                        'isBase64Encoded': False
                    }
                
                password_hash = hash_password(password)
                
                cursor.execute(
                    "SELECT user_id, username, is_admin, is_blocked FROM users WHERE username = %s AND password_hash = %s",
                    (username, password_hash)
                )
                user = cursor.fetchone()
                
                if not user:
                    return {
                        'statusCode': 401,
                        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                        'body': json.dumps({'error': 'Invalid credentials'}),
                        'isBase64Encoded': False
                    }
                
                if user['is_blocked']:
                    return {
                        'statusCode': 403,
                        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                        'body': json.dumps({'error': 'Account is blocked'}),
                        'isBase64Encoded': False
                    }
                
                # Send login notification from TeleDigo bot
                import datetime
                now = datetime.datetime.now().strftime('%d.%m.%Y в %H:%M')
                cursor.execute(
                    "INSERT INTO messages (sender_id, receiver_id, message) VALUES (%s, %s, %s)",
                    ('BOTDGO', user['user_id'], f'🔑 Вход в аккаунт\nВремя: {now}\nЕсли это не вы, немедленно смените пароль!')
                )
                conn.commit()
                
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({
                        'user_id': user['user_id'],
                        'username': user['username'],
                        'is_admin': user['is_admin']
                    }),
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