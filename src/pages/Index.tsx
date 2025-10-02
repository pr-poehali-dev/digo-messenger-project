import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import Icon from '@/components/ui/icon';
import { api, User, Chat, Message, FriendRequest } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

export default function Index() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [activeTab, setActiveTab] = useState('chats');
  const [chats, setChats] = useState<Chat[]>([]);
  const [selectedChat, setSelectedChat] = useState<Chat | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [searchUserId, setSearchUserId] = useState('');
  const [friendRequests, setFriendRequests] = useState<FriendRequest[]>([]);
  const [friends, setFriends] = useState<any[]>([]);
  const [adminUsers, setAdminUsers] = useState<any[]>([]);
  const [adminAction, setAdminAction] = useState('');
  const [adminTargetId, setAdminTargetId] = useState('');
  const [adminLogs, setAdminLogs] = useState<any[]>([]);
  const [notificationMessage, setNotificationMessage] = useState('');
  const [lastMessageCount, setLastMessageCount] = useState(0);
  const [isTyping, setIsTyping] = useState(false);
  const [typingTimeout, setTypingTimeout] = useState<NodeJS.Timeout | null>(null);
  const { toast } = useToast();

  const playNotificationSound = () => {
    const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBTGH0fPTgjMGHm7A7+OZSA0PVqzn77BdGAg+ltryxnMpBSuAzvLZiTUIGGm98OScTgwOUKni8LNgHAU3kdfu0H4yBSN2x/LhjjwLElu17O6nWBUIR5/f88p5KwUlgM/02og2BxpqvO7mnEwMD1Gs5O+zYRsGN5LY8dJ+MwUldsfy4I4/CxFctOzuqVkVCEef4PPLeSsFJIDO8tmINQcaarzv5ppPDA5Rq+Tvs2IbBzaR2PHSfzIGJHbH8+COPwsRXbXs7qlZFQhHn9/yy3orBSR/zvLZiTYHGmq87+mbUQwOUqzl77NiGwc2ktjx0n8yBiV2x/Pgjj8LEV217O6pWRUIR5/f8st6KwUkf87y2Yk2BxpqvO/pm1EMDlKs5e+zYhsHNpLY8dJ/MgYldsfy4I4/CxFctezuqVkVCEef4PPLeisFJH/O8tmJNgcaarzv6ZtRDA5SrOXvs2IbBzaS2PHSfzIGJXbH8+COPwsRXLXs7qlZFQhHn9/yy3orBSR/zvLZiTYHGmq87+mbUQwOUqzl77NiGwc2ktjx0n8yBiV2x/Pgjj8LEV217O6pWRUIR5/f8st6KwUkf87y2Yk2BxpqvO/pm1EMDlKs5e+zYhsHNpLY8dJ/MgYldsfy4I4/CxFctezuqVkVCEef4PPLeisFJH/O8tmJNgcaarzv6ZtRDA5SrOXvs2IbBzaS2PHSfzIGJXbH8+COPwsRXLXs7qlZFQhHn9/yy3orBSR/zvLZiTYHGmq87+mbUQwOUqzl77NiGwc2ktjx0n8yBiV2x/Pgjj8LEVy17O6pWRUIR5/g88t6KwUkf87y2Yk2BxpqvO/pm1EMDlKs5e+zYhsHNpLY8dJ/MgYldsfy4I4/CxFctezuqVkVCEef3/LLeisFJH/O8tmJNgcaarzv6ZtRDA5SrOXvs2IbBzaS2PHSfzIGJXbH8+COPwsRXLXs7qlZFQhHn9/yy3orBSR/zvLZiTYHGmq87+mbUQwOUqzl77NiGwc2ktjx0n8yBiV2x/Pgjj8LEVy17O6pWRUIR5/f8st6KwUkf87y2Yk2BxpqvO/pm1EMDlKs5e+zYhsHNpLY8dJ/MgYldsfy4I4/CxFctezuqVkVCEef3/LLeisFJH/O8tmJNgcaarzv6ZtRDA5SrOXvs2IbBzaS2PHSfzIGJXbH8+COPwsRXLXs7qlZFQhHn9/yy3orBSR/zvLZiTYHGmq87+mbUQwOUqzl77NiGwc2ktjx0n8yBiV2x/Pgjj8LEVy17O6pWRUIR5/f8st6KwUkf87y2Yk2BxpqvO/pm1EMDlKs5e+zYhsHNpLY8dJ/MgYldsfy4I4/CxFctezuqVkVCEef3/LLeisFJH/O8tmJNgcaarzv6ZtRDA5SrOXvs2IbBzaS2PHSfzIGJXbH8+COPwsRXLXs7qlZFQhHn9/yy3orBSR/zvLZiTYHGmq87+mbUQwOUqzl77NiGwc2ktjx0n8yBiV2x/Pgjj8LEVy17O6pWRUIR5/f8st6KwUkf87y2Yk2BxpqvO/pm1EMDlKs5e+zYhsHNpLY8dJ/MgYldsfy4I4/CxFctezuqVkVCEef3/LLeisFJH/O8tmJNgcaarzv6ZtRDA5SrOXvs2IbBzaS2PHSfzIGJXbH8+COPwsRXLXs7qlZFQhHn9/yy3orBSR/zvLZiTYHGmq87+mbUQwOUqzl77NiGwc=');
    audio.volume = 0.3;
    audio.play().catch(() => {});
  };

  useEffect(() => {
    const user = localStorage.getItem('digo_user');
    if (user) {
      const parsedUser = JSON.parse(user);
      setCurrentUser(parsedUser);
      setIsAuthenticated(true);
      
      if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
      }
      loadChats(parsedUser.user_id);
      loadFriendRequests(parsedUser.user_id);
    }
  }, []);

  useEffect(() => {
    if (selectedChat && currentUser) {
      loadMessages(currentUser.user_id, selectedChat.chat_user_id);
      const interval = setInterval(() => {
        loadMessages(currentUser.user_id, selectedChat.chat_user_id);
        checkTypingStatus();
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [selectedChat, currentUser]);

  const checkTypingStatus = async () => {
    if (!currentUser || !selectedChat) return;
    const data = await api.getTypingStatus(currentUser.user_id, selectedChat.chat_user_id);
    setIsTyping(data.is_typing);
  };

  const handleTyping = async () => {
    if (!currentUser || !selectedChat) return;
    
    await api.updateTypingStatus(currentUser.user_id, selectedChat.chat_user_id, true);
    
    if (typingTimeout) clearTimeout(typingTimeout);
    
    const timeout = setTimeout(async () => {
      await api.updateTypingStatus(currentUser.user_id, selectedChat.chat_user_id, false);
    }, 3000);
    
    setTypingTimeout(timeout);
  };

  const handleAuth = async () => {
    try {
      const user = isLogin 
        ? await api.login(username, password)
        : await api.register(username, password);
      
      setCurrentUser(user);
      setIsAuthenticated(true);
      localStorage.setItem('digo_user', JSON.stringify(user));
      loadChats(user.user_id);
      loadFriendRequests(user.user_id);
      toast({ title: isLogin ? 'Добро пожаловать!' : 'Регистрация успешна!' });
    } catch (error: any) {
      toast({ title: 'Ошибка', description: error.message, variant: 'destructive' });
    }
  };

  const loadChats = async (userId: string) => {
    const data = await api.getChats(userId);
    setChats(data);
  };

  const loadMessages = async (userId: string, otherUserId: string) => {
    const data = await api.getMessages(userId, otherUserId);
    
    if (data.length > lastMessageCount && lastMessageCount > 0) {
      const latestMessage = data[data.length - 1];
      if (latestMessage.sender_id !== userId) {
        playNotificationSound();
        if ('Notification' in window && Notification.permission === 'granted') {
          new Notification('Новое сообщение в Digo', {
            body: `${latestMessage.sender_name || 'Пользователь'}: ${latestMessage.message}`,
            icon: '/favicon.svg'
          });
        }
      }
    }
    
    setLastMessageCount(data.length);
    setMessages(data);
  };

  const sendMessage = async () => {
    if (!newMessage.trim() || !selectedChat || !currentUser) return;
    await api.sendMessage(currentUser.user_id, selectedChat.chat_user_id, newMessage);
    await api.updateTypingStatus(currentUser.user_id, selectedChat.chat_user_id, false);
    if (typingTimeout) clearTimeout(typingTimeout);
    setNewMessage('');
    loadMessages(currentUser.user_id, selectedChat.chat_user_id);
  };

  const loadFriendRequests = async (userId: string) => {
    const data = await api.getFriendRequests(userId);
    setFriendRequests(data);
  };

  const handleSearchUser = async () => {
    if (!currentUser || !searchUserId.trim()) return;
    try {
      const user = await api.searchUser(currentUser.user_id, searchUserId);
      toast({ 
        title: 'Пользователь найден',
        description: `${user.username} (ID: ${user.user_id})`
      });
    } catch (error: any) {
      toast({ title: 'Ошибка', description: error.message, variant: 'destructive' });
    }
  };

  const sendFriendRequest = async () => {
    if (!currentUser || !searchUserId.trim()) return;
    try {
      await api.sendFriendRequest(currentUser.user_id, searchUserId);
      toast({ title: 'Запрос отправлен!' });
      setSearchUserId('');
    } catch (error: any) {
      toast({ title: 'Ошибка', description: error.message, variant: 'destructive' });
    }
  };

  const acceptRequest = async (requestId: number) => {
    await api.acceptFriendRequest(requestId);
    if (currentUser) {
      await loadFriendRequests(currentUser.user_id);
      await loadFriends();
      await loadChats(currentUser.user_id);
    }
    toast({ title: 'Заявка принята!' });
  };

  const loadFriends = async () => {
    if (!currentUser) return;
    const data = await api.getFriends(currentUser.user_id);
    setFriends(data);
  };

  const loadAdminUsers = async () => {
    if (!currentUser) return;
    const data = await api.getAllUsers(currentUser.user_id);
    setAdminUsers(data);
  };

  const loadAdminLogs = async () => {
    if (!currentUser) return;
    const data = await api.getAdminLogs(currentUser.user_id);
    setAdminLogs(data);
  };

  const sendNotificationToAll = async () => {
    if (!currentUser || !notificationMessage.trim()) return;
    try {
      const result = await api.sendNotificationToAll(currentUser.user_id, notificationMessage);
      toast({ title: `Уведомление отправлено ${result.recipients} пользователям` });
      setNotificationMessage('');
      loadAdminLogs();
    } catch (error: any) {
      toast({ title: 'Ошибка', description: error.message, variant: 'destructive' });
    }
  };

  const handleAdminAction = async () => {
    if (!currentUser || !adminTargetId.trim()) return;
    try {
      if (adminAction === 'block') {
        await api.blockUser(currentUser.user_id, adminTargetId);
        toast({ title: 'Пользователь заблокирован' });
      } else if (adminAction === 'unblock') {
        await api.unblockUser(currentUser.user_id, adminTargetId);
        toast({ title: 'Пользователь разблокирован' });
      } else if (adminAction === 'grant') {
        await api.grantAdmin(currentUser.user_id, adminTargetId);
        toast({ title: 'Права администратора выданы' });
      } else if (adminAction === 'revoke') {
        await api.revokeAdmin(currentUser.user_id, adminTargetId);
        toast({ title: 'Права администратора отозваны' });
      } else if (adminAction === 'delete') {
        await api.deleteUser(currentUser.user_id, adminTargetId);
        toast({ title: 'Аккаунт удален' });
      }
      setAdminTargetId('');
      setAdminAction('');
      loadAdminUsers();
      loadAdminLogs();
    } catch (error: any) {
      toast({ title: 'Ошибка', description: error.message, variant: 'destructive' });
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('digo_user');
    setIsAuthenticated(false);
    setCurrentUser(null);
    setChats([]);
    setMessages([]);
    setSelectedChat(null);
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex items-center justify-center p-4">
        <Card className="w-full max-w-md p-8 space-y-6">
          <div className="text-center space-y-2">
            <div className="flex items-center justify-center gap-2">
              <Icon name="MessageCircle" size={32} className="text-primary" />
              <h1 className="text-3xl font-bold">Digo</h1>
            </div>
            <p className="text-muted-foreground">Мессенджер нового поколения</p>
          </div>

          <Tabs value={isLogin ? 'login' : 'register'} onValueChange={(v) => setIsLogin(v === 'login')}>
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="login">Вход</TabsTrigger>
              <TabsTrigger value="register">Регистрация</TabsTrigger>
            </TabsList>
            <TabsContent value="login" className="space-y-4">
              <Input placeholder="Логин" value={username} onChange={(e) => setUsername(e.target.value)} />
              <Input type="password" placeholder="Пароль" value={password} onChange={(e) => setPassword(e.target.value)} />
              <Button className="w-full" onClick={handleAuth}>Войти</Button>
            </TabsContent>
            <TabsContent value="register" className="space-y-4">
              <Input placeholder="Логин" value={username} onChange={(e) => setUsername(e.target.value)} />
              <Input type="password" placeholder="Пароль" value={password} onChange={(e) => setPassword(e.target.value)} />
              <Button className="w-full" onClick={handleAuth}>Зарегистрироваться</Button>
            </TabsContent>
          </Tabs>
        </Card>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-background">
      <header className="border-b bg-white px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Icon name="MessageCircle" size={24} className="text-primary" />
          <h1 className="text-xl font-bold">Digo</h1>
        </div>
        <div className="flex items-center gap-3">
          <div className="text-right hidden sm:block">
            <p className="text-sm font-medium">{currentUser?.username}</p>
            <p className="text-xs text-muted-foreground">ID: {currentUser?.user_id}</p>
          </div>
          <Button variant="outline" size="sm" onClick={handleLogout}>
            <Icon name="LogOut" size={16} />
          </Button>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        <div className={`${selectedChat ? 'hidden md:flex' : 'flex'} w-full md:w-80 flex-col border-r bg-white`}>
          <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
            <TabsList className="grid w-full grid-cols-5 rounded-none border-b">
              <TabsTrigger value="chats" className="flex flex-col items-center gap-1 py-2">
                <Icon name="MessageSquare" size={18} />
                <span className="text-xs">Чаты</span>
              </TabsTrigger>
              <TabsTrigger value="search" className="flex flex-col items-center gap-1 py-2">
                <Icon name="Search" size={18} />
                <span className="text-xs">Поиск</span>
              </TabsTrigger>
              <TabsTrigger value="support" className="flex flex-col items-center gap-1 py-2">
                <Icon name="HelpCircle" size={18} />
                <span className="text-xs">Помощь</span>
              </TabsTrigger>
              <TabsTrigger value="profile" className="flex flex-col items-center gap-1 py-2" onClick={loadFriends}>
                <Icon name="User" size={18} />
                <span className="text-xs">Профиль</span>
              </TabsTrigger>
              <TabsTrigger 
                value="settings" 
                className="flex flex-col items-center gap-1 py-2"
                onClick={currentUser?.is_admin ? () => { loadAdminUsers(); loadAdminLogs(); } : undefined}
              >
                <Icon name="Settings" size={18} />
                <span className="text-xs">Настройки</span>
              </TabsTrigger>
            </TabsList>

            <TabsContent value="chats" className="flex-1 m-0">
              <ScrollArea className="h-full">
                {friendRequests.length > 0 && (
                  <div className="p-3 space-y-2">
                    {friendRequests.map((req) => (
                      <Card key={req.id} className="p-3">
                        <p className="text-sm mb-2">
                          <strong>{req.sender_name}</strong> хочет добавить вас в друзья
                        </p>
                        <Button size="sm" onClick={() => acceptRequest(req.id)} className="w-full">
                          Принять
                        </Button>
                      </Card>
                    ))}
                  </div>
                )}
                <div className="divide-y">
                  {chats.map((chat) => (
                    <div
                      key={chat.chat_user_id}
                      className="flex items-center gap-3 p-3 hover:bg-secondary cursor-pointer transition"
                      onClick={() => setSelectedChat(chat)}
                    >
                      <Avatar>
                        <AvatarFallback>{chat.username[0].toUpperCase()}</AvatarFallback>
                      </Avatar>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium truncate">{chat.username}</p>
                        <p className="text-xs text-muted-foreground">ID: {chat.chat_user_id}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </TabsContent>

            <TabsContent value="search" className="flex-1 m-0 p-4 space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Поиск по ID пользователя</label>
                <div className="flex gap-2">
                  <Input 
                    placeholder="Введите 6-значный ID" 
                    value={searchUserId} 
                    onChange={(e) => setSearchUserId(e.target.value)}
                    maxLength={6}
                  />
                  <Button onClick={handleSearchUser}>
                    <Icon name="Search" size={16} />
                  </Button>
                </div>
              </div>
              <Button className="w-full" onClick={sendFriendRequest}>
                Отправить запрос в друзья
              </Button>
            </TabsContent>

            <TabsContent value="support" className="flex-1 m-0 p-4">
              <div className="space-y-4">
                <h3 className="font-semibold">Поддержка Digo</h3>
                <p className="text-sm text-muted-foreground">
                  Если у вас есть вопросы или проблемы, свяжитесь с нами:
                </p>
                <div className="space-y-2">
                  <p className="text-sm">📧 digo.messenger@gmail.com</p>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="profile" className="flex-1 m-0 p-4 space-y-4">
              <div className="text-center space-y-2 pb-4 border-b">
                <Avatar className="w-20 h-20 mx-auto">
                  <AvatarFallback className="text-2xl">
                    {currentUser?.username[0].toUpperCase()}
                  </AvatarFallback>
                </Avatar>
                <h3 className="font-semibold text-lg">{currentUser?.username}</h3>
                <p className="text-sm text-muted-foreground">ID: {currentUser?.user_id}</p>
                {currentUser?.is_admin && (
                  <Badge variant="default">Администратор</Badge>
                )}
              </div>
              <div>
                <h4 className="font-semibold mb-2">Друзья ({friends.length})</h4>
                <ScrollArea className="h-48">
                  {friends.map((friend) => (
                    <div key={friend.user_id} className="flex items-center gap-2 p-2 hover:bg-secondary rounded">
                      <Avatar className="w-8 h-8">
                        <AvatarFallback>{friend.username[0].toUpperCase()}</AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="text-sm font-medium">{friend.username}</p>
                        <p className="text-xs text-muted-foreground">{friend.user_id}</p>
                      </div>
                    </div>
                  ))}
                </ScrollArea>
              </div>
            </TabsContent>

            <TabsContent value="settings" className="flex-1 m-0 p-4 space-y-4">
              {currentUser?.is_admin ? (
                <>
                  <div className="space-y-2">
                    <h3 className="font-semibold text-destructive">⚡ Админ-панель</h3>
                    <div className="space-y-2">
                      <select 
                        className="w-full border rounded p-2 text-sm"
                        value={adminAction}
                        onChange={(e) => setAdminAction(e.target.value)}
                      >
                        <option value="">Выберите действие</option>
                        <option value="block">Заблокировать пользователя</option>
                        <option value="unblock">Разблокировать пользователя</option>
                        <option value="grant">Выдать админ права</option>
                        <option value="revoke">Забрать админ права</option>
                        <option value="delete">Удалить аккаунт</option>
                      </select>
                      <div className="flex gap-2">
                        <Input 
                          placeholder="User ID" 
                          value={adminTargetId}
                          onChange={(e) => setAdminTargetId(e.target.value)}
                        />
                        <Button onClick={handleAdminAction} variant="destructive">
                          Выполнить
                        </Button>
                      </div>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <h4 className="font-semibold">📢 Уведомление всем пользователям</h4>
                    <Input 
                      placeholder="Введите сообщение для всех"
                      value={notificationMessage}
                      onChange={(e) => setNotificationMessage(e.target.value)}
                    />
                    <Button onClick={sendNotificationToAll} className="w-full">
                      Отправить всем
                    </Button>
                  </div>

                  <div>
                    <h4 className="font-semibold mb-2">Все пользователи</h4>
                    <ScrollArea className="h-32">
                      {adminUsers.map((user) => (
                        <div key={user.user_id} className="p-2 border-b text-xs">
                          <p><strong>{user.username}</strong> - {user.user_id}</p>
                          <div className="flex gap-2 mt-1">
                            {user.is_admin && <Badge variant="default" className="text-xs">Admin</Badge>}
                            {user.is_blocked && <Badge variant="destructive" className="text-xs">Blocked</Badge>}
                          </div>
                        </div>
                      ))}
                    </ScrollArea>
                  </div>

                  <div>
                    <h4 className="font-semibold mb-2">📋 История действий</h4>
                    <ScrollArea className="h-32">
                      {adminLogs.map((log) => (
                        <div key={log.id} className="p-2 border-b text-xs">
                          <p className="font-medium">{log.action_type}</p>
                          <p className="text-muted-foreground">{log.description}</p>
                          <p className="text-muted-foreground">{new Date(log.created_at).toLocaleString('ru')}</p>
                        </div>
                      ))}
                    </ScrollArea>
                  </div>
                </>
              ) : (
                <div className="space-y-2">
                  <h3 className="font-semibold">Настройки</h3>
                  <p className="text-sm text-muted-foreground">
                    Здесь будут настройки профиля, уведомлений и приватности.
                  </p>
                </div>
              )}
            </TabsContent>
          </Tabs>
        </div>

        <div className={`${selectedChat ? 'flex' : 'hidden md:flex'} flex-1 flex-col bg-white`}>
          {selectedChat ? (
            <>
              <div className="border-b p-4 flex items-center gap-3">
                <Button 
                  variant="ghost" 
                  size="sm" 
                  className="md:hidden"
                  onClick={() => setSelectedChat(null)}
                >
                  <Icon name="ArrowLeft" size={20} />
                </Button>
                <Avatar>
                  <AvatarFallback>{selectedChat.username[0].toUpperCase()}</AvatarFallback>
                </Avatar>
                <div>
                  <p className="font-semibold">{selectedChat.username}</p>
                  <div className="flex items-center gap-1 text-xs">
                    {isTyping ? (
                      <span className="text-primary">печатает...</span>
                    ) : (
                      <>
                        <div className="w-2 h-2 bg-accent rounded-full"></div>
                        <span className="text-accent">онлайн</span>
                      </>
                    )}
                  </div>
                </div>
              </div>

              <ScrollArea className="flex-1 p-4">
                <div className="space-y-3">
                  {messages.map((msg) => (
                    <div
                      key={msg.id}
                      className={`flex ${msg.sender_id === currentUser?.user_id ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[70%] rounded-2xl px-4 py-2 ${
                          msg.sender_id === currentUser?.user_id
                            ? 'bg-primary text-primary-foreground'
                            : 'bg-secondary text-secondary-foreground'
                        }`}
                      >
                        <p className="text-sm">{msg.message}</p>
                        <p className="text-xs opacity-70 mt-1">
                          {new Date(msg.created_at).toLocaleTimeString('ru', { hour: '2-digit', minute: '2-digit' })}
                        </p>
                      </div>
                    </div>
                  ))}
                  {isTyping && (
                    <div className="flex justify-start">
                      <div className="bg-secondary rounded-2xl px-4 py-2">
                        <div className="flex gap-1">
                          <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{animationDelay: '0ms'}}></div>
                          <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{animationDelay: '150ms'}}></div>
                          <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{animationDelay: '300ms'}}></div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </ScrollArea>

              <div className="border-t p-4">
                <div className="flex gap-2">
                  <Input
                    placeholder="Введите сообщение..."
                    value={newMessage}
                    onChange={(e) => {
                      setNewMessage(e.target.value);
                      handleTyping();
                    }}
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                  />
                  <Button onClick={sendMessage} size="icon">
                    <Icon name="Send" size={18} />
                  </Button>
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-muted-foreground">
              <div className="text-center">
                <Icon name="MessageCircle" size={64} className="mx-auto mb-4 opacity-20" />
                <p>Выберите чат для начала общения</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}