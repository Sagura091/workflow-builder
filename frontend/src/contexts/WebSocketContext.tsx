import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import websocketService, { MessageHandler } from '../services/websocketService';
import { useAuth } from './AuthContext';
import { FEATURES } from '../config';

interface WebSocketContextType {
  isConnected: boolean;
  connect: () => Promise<void>;
  disconnect: () => void;
  subscribe: (type: string, handler: MessageHandler) => void;
  unsubscribe: (type: string, handler: MessageHandler) => void;
  send: (type: string, data: any) => boolean;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

export const WebSocketProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isConnected, setIsConnected] = useState(websocketService.isConnected());

  // Try to use AuthContext, but don't fail if it's not available
  let authState: { isAuthenticated: boolean; token: string | null } = { isAuthenticated: false, token: null };
  try {
    const auth = useAuth();
    authState = auth.authState;
  } catch (error) {
    console.warn('AuthProvider not available, using fallback values for WebSocketProvider');
  }

  // Update connection status when auth state changes
  useEffect(() => {
    if (!FEATURES.WEBSOCKETS_ENABLED) {
      return;
    }

    // Update token when auth state changes
    if (authState.token) {
      websocketService.updateToken(authState.token);
    } else {
      websocketService.updateToken(null);
    }

    // Connect if authenticated
    if (authState.isAuthenticated && !websocketService.isConnected()) {
      websocketService.connect()
        .then(() => setIsConnected(true))
        .catch(error => console.error('Error connecting to WebSocket:', error));
    }

    // Disconnect if not authenticated
    if (!authState.isAuthenticated && websocketService.isConnected()) {
      websocketService.disconnect();
      setIsConnected(false);
    }
  }, [authState.isAuthenticated, authState.token]);

  // Check connection status periodically
  useEffect(() => {
    if (!FEATURES.WEBSOCKETS_ENABLED) {
      return;
    }

    const interval = setInterval(() => {
      const connected = websocketService.isConnected();
      if (connected !== isConnected) {
        setIsConnected(connected);
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [isConnected]);

  // Connect to WebSocket
  const connect = async () => {
    if (!FEATURES.WEBSOCKETS_ENABLED) {
      return Promise.resolve();
    }

    try {
      await websocketService.connect();
      setIsConnected(true);
    } catch (error) {
      console.error('Error connecting to WebSocket:', error);
      setIsConnected(false);
      throw error;
    }
  };

  // Disconnect from WebSocket
  const disconnect = () => {
    if (!FEATURES.WEBSOCKETS_ENABLED) {
      return;
    }

    websocketService.disconnect();
    setIsConnected(false);
  };

  // Subscribe to a message type
  const subscribe = (type: string, handler: MessageHandler) => {
    if (!FEATURES.WEBSOCKETS_ENABLED) {
      return;
    }

    websocketService.subscribe(type, handler);
  };

  // Unsubscribe from a message type
  const unsubscribe = (type: string, handler: MessageHandler) => {
    if (!FEATURES.WEBSOCKETS_ENABLED) {
      return;
    }

    websocketService.unsubscribe(type, handler);
  };

  // Send a message
  const send = (type: string, data: any) => {
    if (!FEATURES.WEBSOCKETS_ENABLED) {
      return false;
    }

    return websocketService.send(type, data);
  };

  const contextValue: WebSocketContextType = {
    isConnected,
    connect,
    disconnect,
    subscribe,
    unsubscribe,
    send,
  };

  return (
    <WebSocketContext.Provider value={contextValue}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocket = (): WebSocketContextType => {
  const context = useContext(WebSocketContext);
  if (context === undefined) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
};

export default WebSocketContext;
