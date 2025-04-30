import { create } from 'zustand';
import { jwtDecode } from 'jwt-decode';
import { login as apiLogin } from '../services/api';

interface User {
  id: string;
  username: string;
  role: string;
}

interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  loading: boolean;
  error: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  initAuth: () => void;
  isDemoUser: boolean;
}

// Demo user credentials
const DEMO_USER = {
  username: 'demo',
  password: 'demo123'
};

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: false,
  user: null,
  loading: false,
  error: null,
  isDemoUser: false,

  login: async (username, password) => {
    set({ loading: true, error: null });
    try {
      // Check for demo user
      if (username === DEMO_USER.username && password === DEMO_USER.password) {
        const demoUser = {
          id: 'demo-user',
          username: 'Demo User',
          role: 'student'
        };
        
        set({
          isAuthenticated: true,
          user: demoUser,
          loading: false,
          isDemoUser: true
        });
        return;
      }

      const data = await apiLogin(username, password);
      const { access_token } = data;
      
      localStorage.setItem('access_token', access_token);
      
      const decodedToken: any = jwtDecode(access_token);
      
      set({
        isAuthenticated: true,
        user: {
          id: decodedToken.sub,
          username: decodedToken.sub,
          role: decodedToken.role
        },
        loading: false,
        isDemoUser: false
      });
    } catch (err: any) {
      set({
        loading: false,
        error: err.response?.data?.detail || 'Failed to login. Please check your credentials.'
      });
      throw err;
    }
  },

  logout: () => {
    localStorage.removeItem('access_token');
    set({ isAuthenticated: false, user: null, isDemoUser: false });
  },

  initAuth: () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      set({ isAuthenticated: false, user: null });
      return;
    }

    try {
      const decodedToken: any = jwtDecode(token);
      const currentTime = Date.now() / 1000;
      
      if (decodedToken.exp < currentTime) {
        localStorage.removeItem('access_token');
        set({ isAuthenticated: false, user: null });
      } else {
        set({
          isAuthenticated: true,
          user: {
            id: decodedToken.sub,
            username: decodedToken.sub,
            role: decodedToken.role
          }
        });
      }
    } catch (err) {
      localStorage.removeItem('access_token');
      set({ isAuthenticated: false, user: null });
    }
  }
}));