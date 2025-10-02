const API_URLS = {
  auth: 'https://functions.poehali.dev/e6db6005-f0f6-42a4-8242-9c4be52a6be2',
  messages: 'https://functions.poehali.dev/56733cab-f91a-48f3-9a97-2b35ad31018d',
  admin: 'https://functions.poehali.dev/b88575f9-3ba7-42f8-9a58-7008d30b39bc'
};

export interface User {
  user_id: string;
  username: string;
  is_admin: boolean;
}

export interface Message {
  id: number;
  sender_id: string;
  receiver_id: string;
  message: string;
  sender_name?: string;
  created_at: string;
}

export interface Chat {
  chat_user_id: string;
  username: string;
  avatar_url?: string;
}

export interface FriendRequest {
  id: number;
  sender_id: string;
  receiver_id: string;
  sender_name: string;
  status: string;
  created_at: string;
}

export const api = {
  async register(username: string, password: string): Promise<User> {
    const response = await fetch(API_URLS.auth, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'register', username, password })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Registration failed');
    return data;
  },

  async login(username: string, password: string): Promise<User> {
    const response = await fetch(API_URLS.auth, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'login', username, password })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Login failed');
    return data;
  },

  async getChats(userId: string): Promise<Chat[]> {
    const response = await fetch(`${API_URLS.messages}?action=chats&user_id=${userId}`);
    return response.json();
  },

  async getMessages(userId: string, otherUserId: string): Promise<Message[]> {
    const response = await fetch(`${API_URLS.messages}?action=messages&user_id=${userId}&other_user_id=${otherUserId}`);
    return response.json();
  },

  async sendMessage(senderId: string, receiverId: string, message: string) {
    const response = await fetch(API_URLS.messages, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'send', sender_id: senderId, receiver_id: receiverId, message })
    });
    return response.json();
  },

  async getFriendRequests(userId: string): Promise<FriendRequest[]> {
    const response = await fetch(`${API_URLS.messages}?action=requests&user_id=${userId}`);
    return response.json();
  },

  async sendFriendRequest(senderId: string, receiverId: string) {
    const response = await fetch(API_URLS.messages, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'friend_request', sender_id: senderId, receiver_id: receiverId })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Request failed');
    return data;
  },

  async acceptFriendRequest(requestId: number) {
    const response = await fetch(API_URLS.messages, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'accept_request', request_id: requestId })
    });
    return response.json();
  },

  async getFriends(userId: string) {
    const response = await fetch(`${API_URLS.messages}?action=friends&user_id=${userId}`);
    return response.json();
  },

  async searchUser(userId: string, searchUserId: string) {
    const response = await fetch(`${API_URLS.admin}?action=search&user_id=${searchUserId}`, {
      headers: { 'X-User-Id': userId }
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'User not found');
    return data;
  },

  async getAllUsers(adminUserId: string) {
    const response = await fetch(`${API_URLS.admin}?action=users`, {
      headers: { 'X-User-Id': adminUserId }
    });
    return response.json();
  },

  async blockUser(adminUserId: string, targetUserId: string) {
    const response = await fetch(API_URLS.admin, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-User-Id': adminUserId },
      body: JSON.stringify({ action: 'block', user_id: targetUserId })
    });
    return response.json();
  },

  async grantAdmin(adminUserId: string, targetUserId: string) {
    const response = await fetch(API_URLS.admin, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-User-Id': adminUserId },
      body: JSON.stringify({ action: 'grant_admin', user_id: targetUserId })
    });
    return response.json();
  },

  async revokeAdmin(adminUserId: string, targetUserId: string) {
    const response = await fetch(API_URLS.admin, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-User-Id': adminUserId },
      body: JSON.stringify({ action: 'revoke_admin', user_id: targetUserId })
    });
    return response.json();
  }
};
