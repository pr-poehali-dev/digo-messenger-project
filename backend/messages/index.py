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
    
    schema = 't_p99070328_digo_messenger_proje'
    
    try:
        if method == 'GET':
            params = event.get('queryStringParameters', {})
            action = params.get('action')
            user_id = params.get('user_id')
            
            # Get user's chats
            if action == 'chats':
                cursor.execute(f"""
                    SELECT DISTINCT 
                        CASE 
                            WHEN sender_id = %s THEN receiver_id 
                            ELSE sender_id 
                        END as chat_user_id,
                        u.username,
                        u.avatar_url
                    FROM {schema}.messages m
                    JOIN {schema}.users u ON (
                        CASE 
                            WHEN m.sender_id = %s THEN m.receiver_id 
                            ELSE m.sender_id 
                        END = u.user_id
                    )
                    WHERE sender_id = %s OR receiver_id = %s
                    
                    UNION
                    
                    SELECT DISTINCT 
                        f.friend_id as chat_user_id,
                        u.username,
                        u.avatar_url
                    FROM {schema}.friends f
                    JOIN {schema}.users u ON f.friend_id = u.user_id
                    WHERE f.user_id = %s
                    
                    UNION
                    
                    SELECT DISTINCT 
                        f.user_id as chat_user_id,
                        u.username,
                        u.avatar_url
                    FROM {schema}.friends f
                    JOIN {schema}.users u ON f.user_id = u.user_id
                    WHERE f.friend_id = %s
                    
                    ORDER BY chat_user_id
                """, (user_id, user_id, user_id, user_id, user_id, user_id))
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
                cursor.execute(f"""
                    SELECT m.*, u.username as sender_name
                    FROM {schema}.messages m
                    JOIN {schema}.users u ON m.sender_id = u.user_id
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
                cursor.execute(f"""
                    SELECT fr.*, u.username as sender_name
                    FROM {schema}.friend_requests fr
                    JOIN {schema}.users u ON fr.sender_id = u.user_id
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
                cursor.execute(f"""
                    SELECT u.user_id, u.username, u.avatar_url
                    FROM {schema}.friends f
                    JOIN {schema}.users u ON f.friend_id = u.user_id
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
            
            # Get typing status
            elif action == 'typing_status':
                other_user_id = params.get('other_user_id')
                cursor.execute(f"""
                    SELECT is_typing, last_updated 
                    FROM {schema}.typing_status 
                    WHERE user_id = %s AND chat_with_id = %s 
                    AND last_updated > NOW() - INTERVAL '5 seconds'
                """, (other_user_id, user_id))
                status = cursor.fetchone()
                
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'is_typing': status['is_typing'] if status else False}),
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
                    f"INSERT INTO {schema}.messages (sender_id, receiver_id, message) VALUES (%s, %s, %s) RETURNING id, created_at",
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
                    f"SELECT * FROM {schema}.friends WHERE user_id = %s AND friend_id = %s",
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
                    f"SELECT * FROM {schema}.friend_requests WHERE sender_id = %s AND receiver_id = %s AND status = 'pending'",
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
                    f"INSERT INTO {schema}.friend_requests (sender_id, receiver_id) VALUES (%s, %s) RETURNING id",
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
            
            # Update typing status
            elif action == 'typing':
                sender_id = body_data.get('sender_id')
                receiver_id = body_data.get('receiver_id')
                is_typing = body_data.get('is_typing', False)
                
                cursor.execute(f"""
                    INSERT INTO {schema}.typing_status (user_id, chat_with_id, is_typing, last_updated)
                    VALUES (%s, %s, %s, NOW())
                    ON CONFLICT (user_id, chat_with_id) 
                    DO UPDATE SET is_typing = %s, last_updated = NOW()
                """, (sender_id, receiver_id, is_typing, is_typing))
                conn.commit()
                
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'status': 'updated'}),
                    'isBase64Encoded': False
                }
            
            # Accept friend request
            elif action == 'accept_request':
                request_id = body_data.get('request_id')
                
                # Get request details
                cursor.execute(f"SELECT sender_id, receiver_id FROM {schema}.friend_requests WHERE id = %s", (request_id,))
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
                    f"INSERT INTO {schema}.friends (user_id, friend_id) VALUES (%s, %s), (%s, %s)",
                    (request['sender_id'], request['receiver_id'], request['receiver_id'], request['sender_id'])
                )
                
                # Update request status
                cursor.execute(f"UPDATE {schema}.friend_requests SET status = 'accepted' WHERE id = %s", (request_id,))
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