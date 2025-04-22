import { WS_URL, WS_RECONNECT_INTERVAL, WS_MAX_RECONNECT_ATTEMPTS } from '../config';

export type MessageHandler = (data: any) => void;

export interface WebSocketMessage {
  type: string;
  data: any;
}

class WebSocketService {
  private socket: WebSocket | null = null;
  private reconnectAttempts = 0;
  private reconnectTimeout: NodeJS.Timeout | null = null;
  private messageHandlers: Map<string, Set<MessageHandler>> = new Map();
  private isConnecting = false;
  private token: string | null = null;

  constructor() {
    // Initialize token from localStorage
    this.token = localStorage.getItem('auth_token');

    // Listen for storage events to update token
    window.addEventListener('storage', (event) => {
      if (event.key === 'auth_token') {
        this.token = event.newValue;

        // Reconnect with new token if connected
        if (this.isConnected()) {
          this.disconnect();
          this.connect();
        }
      }
    });
  }

  /**
   * Connect to the WebSocket server
   */
  public connect(): Promise<void> {
    if (this.isConnected() || this.isConnecting) {
      return Promise.resolve();
    }

    this.isConnecting = true;

    return new Promise((resolve, reject) => {
      try {
        // Build URL with token if available
        let url = WS_URL;
        if (this.token) {
          url += `?token=${this.token}`;
        }

        this.socket = new WebSocket(url);

        this.socket.onopen = () => {
          console.log('WebSocket connected');
          this.reconnectAttempts = 0;
          this.isConnecting = false;
          resolve();
        };

        this.socket.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        this.socket.onclose = (event) => {
          this.isConnecting = false;

          if (event.wasClean) {
            console.log(`WebSocket closed cleanly, code=${event.code}, reason=${event.reason}`);
          } else {
            console.warn('WebSocket connection died');
            this.reconnect();
          }
        };

        this.socket.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.isConnecting = false;
          reject(error);
        };
      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });
  }

  /**
   * Disconnect from the WebSocket server
   */
  public disconnect(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }

    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }

    this.reconnectAttempts = 0;
  }

  /**
   * Check if connected to the WebSocket server
   */
  public isConnected(): boolean {
    return this.socket !== null && this.socket.readyState === WebSocket.OPEN;
  }

  /**
   * Send a message to the WebSocket server
   */
  public send(type: string, data: any): boolean {
    if (!this.isConnected()) {
      console.warn('Cannot send message, WebSocket not connected');
      return false;
    }

    try {
      const message: WebSocketMessage = { type, data };
      this.socket!.send(JSON.stringify(message));
      return true;
    } catch (error) {
      console.error('Error sending WebSocket message:', error);
      return false;
    }
  }

  /**
   * Subscribe to a message type
   */
  public subscribe(type: string, handler: MessageHandler): void {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, new Set());
    }

    this.messageHandlers.get(type)!.add(handler);
  }

  /**
   * Unsubscribe from a message type
   */
  public unsubscribe(type: string, handler: MessageHandler): void {
    if (!this.messageHandlers.has(type)) {
      return;
    }

    this.messageHandlers.get(type)!.delete(handler);

    if (this.messageHandlers.get(type)!.size === 0) {
      this.messageHandlers.delete(type);
    }
  }

  /**
   * Handle an incoming message
   */
  private handleMessage(message: WebSocketMessage): void {
    const { type, data } = message;

    if (this.messageHandlers.has(type)) {
      const handlers = this.messageHandlers.get(type)!;
      handlers.forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error(`Error in WebSocket message handler for type ${type}:`, error);
        }
      });
    }
  }

  /**
   * Attempt to reconnect to the WebSocket server
   */
  private reconnect(): void {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }

    if (this.reconnectAttempts >= WS_MAX_RECONNECT_ATTEMPTS) {
      console.warn(`Maximum reconnect attempts (${WS_MAX_RECONNECT_ATTEMPTS}) reached`);
      return;
    }

    this.reconnectAttempts++;

    const delay = WS_RECONNECT_INTERVAL * Math.pow(1.5, this.reconnectAttempts - 1);
    console.log(`Reconnecting to WebSocket in ${delay}ms (attempt ${this.reconnectAttempts})`);

    this.reconnectTimeout = setTimeout(() => {
      this.connect().catch((error) => {
        console.error('Error reconnecting to WebSocket:', error);
      });
    }, delay);
  }

  /**
   * Update the authentication token
   */
  public updateToken(token: string | null): void {
    this.token = token;

    // Reconnect with new token if connected
    if (this.isConnected()) {
      this.disconnect();
      this.connect();
    }
  }
}

// Create a singleton instance
const websocketService = new WebSocketService();

export default websocketService;
