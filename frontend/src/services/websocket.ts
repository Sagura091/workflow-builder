/**
 * WebSocket Service
 * 
 * This service provides a WebSocket connection to the backend for real-time updates.
 */

import { API_BASE_URL } from '../config';

// Event types
export enum WebSocketEventType {
  NODE_INSTANCE_CREATED = 'node_instance_created',
  NODE_INSTANCE_UPDATED = 'node_instance_updated',
  NODE_INSTANCE_DELETED = 'node_instance_deleted',
  CORE_NODE_UPDATED = 'core_node_updated',
}

// Event handlers
type EventHandler = (data: any) => void;

class WebSocketService {
  private socket: WebSocket | null = null;
  private eventHandlers: Map<WebSocketEventType, EventHandler[]> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectTimeout: NodeJS.Timeout | null = null;
  private isConnecting = false;

  /**
   * Connect to the WebSocket server
   * @param endpoint The WebSocket endpoint to connect to
   */
  connect(endpoint: string = 'node-instances/ws'): Promise<void> {
    if (this.socket?.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return Promise.resolve();
    }

    if (this.isConnecting) {
      console.log('WebSocket connection already in progress');
      return Promise.resolve();
    }

    this.isConnecting = true;

    return new Promise((resolve, reject) => {
      try {
        const wsUrl = `${API_BASE_URL.replace('http', 'ws')}/api/${endpoint}`;
        console.log(`Connecting to WebSocket at ${wsUrl}`);
        
        this.socket = new WebSocket(wsUrl);

        this.socket.onopen = () => {
          console.log('WebSocket connected');
          this.reconnectAttempts = 0;
          this.isConnecting = false;
          resolve();
        };

        this.socket.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        this.socket.onclose = (event) => {
          console.log(`WebSocket disconnected: ${event.code} ${event.reason}`);
          this.socket = null;
          this.isConnecting = false;
          
          // Attempt to reconnect
          if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
            console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            
            this.reconnectTimeout = setTimeout(() => {
              this.connect(endpoint).catch(console.error);
            }, delay);
          }
        };

        this.socket.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.isConnecting = false;
          reject(error);
        };
      } catch (error) {
        console.error('Error connecting to WebSocket:', error);
        this.isConnecting = false;
        reject(error);
      }
    });
  }

  /**
   * Disconnect from the WebSocket server
   */
  disconnect(): void {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }

    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }

  /**
   * Send a message to the WebSocket server
   * @param message The message to send
   */
  send(message: any): void {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
    } else {
      console.error('WebSocket not connected');
    }
  }

  /**
   * Add an event handler for a specific event type
   * @param eventType The event type to listen for
   * @param handler The handler function to call when the event occurs
   */
  on(eventType: WebSocketEventType, handler: EventHandler): void {
    if (!this.eventHandlers.has(eventType)) {
      this.eventHandlers.set(eventType, []);
    }
    this.eventHandlers.get(eventType)?.push(handler);
  }

  /**
   * Remove an event handler for a specific event type
   * @param eventType The event type to remove the handler from
   * @param handler The handler function to remove
   */
  off(eventType: WebSocketEventType, handler: EventHandler): void {
    if (!this.eventHandlers.has(eventType)) {
      return;
    }
    
    const handlers = this.eventHandlers.get(eventType);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index !== -1) {
        handlers.splice(index, 1);
      }
    }
  }

  /**
   * Handle a message from the WebSocket server
   * @param message The message to handle
   */
  private handleMessage(message: any): void {
    const { type, data } = message;
    
    if (!type || !data) {
      console.warn('Invalid WebSocket message format:', message);
      return;
    }

    // Call all handlers for this event type
    const handlers = this.eventHandlers.get(type as WebSocketEventType);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error(`Error in WebSocket event handler for ${type}:`, error);
        }
      });
    }
  }
}

// Create a singleton instance
export const websocketService = new WebSocketService();

export default websocketService;
