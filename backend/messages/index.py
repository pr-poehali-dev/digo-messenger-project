"""
Business: Send and receive messages, manage friend requests for Digo messenger
Args: event - dict with httpMethod, body, queryStringParameters
      context - object with attributes: request_id, function_name
Returns: HTTP response dict with messages or friend request data
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
                'Access-Control-Allow-Headers': 'Content-Type, X-User-Id',
                'Access-Control-Max-Age': '86400'
            },
            'body': '',
            'isBase64Encoded': False
        }
    
    db_url = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        if method == 'GET':
            params = event.get('queryStringParameters', {})
            action = params.get('action')
            user_id = params.get('user_id')
            
            # Get user's chats
            if action == 'chats':
                cursor.execute("""
                    SELECT DISTINCT 
                        CASE 
                            WHEN sender_id = %s THEN receiver_id 
                            ELSE sender_id 
                        END as chat_user_id,
                        u.username,
                        u.avatar_url
                    FROM messages m
                    JOIN users u ON (
                        CASE 
                            WHEN m.sender_id = %s THEN m.receiver_id 
                            ELSE m.sender_id 
                        END = u.user_id
                    )
                    WHERE sender_id = %s OR receiver_id = %s
                    ORDER BY chat_user_id
                """, (user_id, user_id, user_id, user_id))
                chats = cursor.fetchall()
                
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps([dict(chat) for chat in chats]),
                    'isBase64Encoded': False
                }
            
            # Get messages with specific user
            elif action == 'messages':
                other_user_id = params.get('other_user_id')
                cursor.execute("""
                    SELECT m.*, u.username as sender_name
                    FROM messages m
                    JOIN users u ON m.sender_id = u.user_id
                    WHERE (sender_id = %s AND receiver_id = %s) 
                       OR (sender_id = %s AND receiver_id = %s)
                    ORDER BY created_at ASC
                """, (user_id, other_user_id, other_user_id, user_id))
                messages = cursor.fetchall()
                
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps([dict(msg) for msg in messages], default=str),
                    'isBase64Encoded': False
                }
            
            # Get friend requests
            elif action == 'requests':
                cursor.execute("""
                    SELECT fr.*, u.username as sender_name
                    FROM friend_requests fr
                    JOIN users u ON fr.sender_id = u.user_id
                    WHERE receiver_id = %s AND status = 'pending'
                    ORDER BY created_at DESC
                """, (user_id,))
                requests = cursor.fetchall()
                
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps([dict(req) for req in requests], default=str),
                    'isBase64Encoded': False
                }
            
            # Get friends list
            elif action == 'friends':
                cursor.execute("""
                    SELECT u.user_id, u.username, u.avatar_url
                    FROM friends f
                    JOIN users u ON f.friend_id = u.user_id
                    WHERE f.user_id = %s
                    ORDER BY u.username
                """, (user_id,))
                friends = cursor.fetchall()
                
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps([dict(friend) for friend in friends]),
                    'isBase64Encoded': False
                }
        
        elif method == 'POST':
            body_data = json.loads(event.get('body', '{}'))
            action = body_data.get('action')
            
            # Send message
            if action == 'send':
                sender_id = body_data.get('sender_id')
                receiver_id = body_data.get('receiver_id')
                message = body_data.get('message')
                
                cursor.execute(
                    "INSERT INTO messages (sender_id, receiver_id, message) VALUES (%s, %s, %s) RETURNING id, created_at",
                    (sender_id, receiver_id, message)
                )
                result = cursor.fetchone()
                conn.commit()
                
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'id': result['id'], 'created_at': str(result['created_at'])}),
                    'isBase64Encoded': False
                }
            
            # Send friend request
            elif action == 'friend_request':
                sender_id = body_data.get('sender_id')
                receiver_id = body_data.get('receiver_id')
                
                # Check if already friends
                cursor.execute(
                    "SELECT * FROM friends WHERE user_id = %s AND friend_id = %s",
                    (sender_id, receiver_id)
                )
                if cursor.fetchone():
                    return {
                        'statusCode': 400,
                        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                        'body': json.dumps({'error': 'Already friends'}),
                        'isBase64Encoded': False
                    }
                
                # Check if request already exists
                cursor.execute(
                    "SELECT * FROM friend_requests WHERE sender_id = %s AND receiver_id = %s AND status = 'pending'",
                    (sender_id, receiver_id)
                )
                if cursor.fetchone():
                    return {
                        'statusCode': 400,
                        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                        'body': json.dumps({'error': 'Request already sent'}),
                        'isBase64Encoded': False
                    }
                
                cursor.execute(
                    "INSERT INTO friend_requests (sender_id, receiver_id) VALUES (%s, %s) RETURNING id",
                    (sender_id, receiver_id)
                )
                result = cursor.fetchone()
                conn.commit()
                
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'id': result['id'], 'status': 'sent'}),
                    'isBase64Encoded': False
                }
            
            # Accept friend request
            elif action == 'accept_request':
                request_id = body_data.get('request_id')
                
                # Get request details
                cursor.execute("SELECT sender_id, receiver_id FROM friend_requests WHERE id = %s", (request_id,))
                request = cursor.fetchone()
                
                if not request:
                    return {
                        'statusCode': 404,
                        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                        'body': json.dumps({'error': 'Request not found'}),
                        'isBase64Encoded': False
                    }
                
                # Add to friends (both directions)
                cursor.execute(
                    "INSERT INTO friends (user_id, friend_id) VALUES (%s, %s), (%s, %s)",
                    (request['sender_id'], request['receiver_id'], request['receiver_id'], request['sender_id'])
                )
                
                # Update request status
                cursor.execute("UPDATE friend_requests SET status = 'accepted' WHERE id = %s", (request_id,))
                conn.commit()
                
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'status': 'accepted'}),
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
