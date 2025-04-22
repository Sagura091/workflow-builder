/**
 * WebSocket Hook
 * 
 * This hook provides a way to use WebSockets in React components.
 */

import { useEffect, useCallback } from 'react';
import websocketService, { WebSocketEventType } from '../services/websocket';

type EventHandler = (data: any) => void;

interface UseWebSocketOptions {
  autoConnect?: boolean;
  endpoint?: string;
}

/**
 * Hook for using WebSockets in React components
 * @param options Options for the WebSocket connection
 * @returns Object with methods for interacting with the WebSocket
 */
export const useWebSocket = (options: UseWebSocketOptions = {}) => {
  const { autoConnect = true, endpoint = 'node-instances/ws' } = options;

  // Connect to the WebSocket server
  const connect = useCallback(async () => {
    try {
      await websocketService.connect(endpoint);
      return true;
    } catch (error) {
      console.error('Error connecting to WebSocket:', error);
      return false;
    }
  }, [endpoint]);

  // Disconnect from the WebSocket server
  const disconnect = useCallback(() => {
    websocketService.disconnect();
  }, []);

  // Send a message to the WebSocket server
  const send = useCallback((message: any) => {
    websocketService.send(message);
  }, []);

  // Add an event listener
  const addEventListener = useCallback((eventType: WebSocketEventType, handler: EventHandler) => {
    websocketService.on(eventType, handler);
    
    // Return a function to remove the event listener
    return () => {
      websocketService.off(eventType, handler);
    };
  }, []);

  // Connect to the WebSocket server when the component mounts
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    // Disconnect when the component unmounts
    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  return {
    connect,
    disconnect,
    send,
    addEventListener,
  };
};

export default useWebSocket;
