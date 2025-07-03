import axios from 'axios';

const API_URL = '/api'; // Replace with your FastAPI server URL

// Get the current token from localStorage
const getAuthToken = () => {
  return localStorage.getItem('access_token');
};

// Create an axios instance with the base URL and token
const axiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add an interceptor to attach the auth token to each request
axiosInstance.interceptors.request.use(
  (config) => {
    const token = getAuthToken();
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// User login to get the access token
export const login = async (username: string, password: string) => {
  const params = new URLSearchParams();
  params.append("username", username);
  params.append("password", password);

  try {
    const response = await axios.post(`${API_URL}/token/`, params, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error logging in:', error);
    throw error;
  }
};

// User registration
export const register = async (username: string, password: string) => {
  try {
    const response = await axios.post(`${API_URL}/register/`, null, {
      params: {
        username,
        password
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error registering user:', error);
    throw error;
  }
};

// Fetch recent results of the user
export const getRecentResults = async () => {
  try {
    const response = await axiosInstance.get('/recent-results/');
    return response.data;
  } catch (error) {
    console.error('Error fetching recent results:', error);
    throw error;
  }
};

// Process a file upload
export const processMaterial = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await axiosInstance.post('/process-material/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    console.log('Processing started:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error processing material:', error);
    throw error;
  }
};

// Check the task status by task ID
export const getTaskStatus = async (taskId: string) => {
  try {
    const response = await axiosInstance.get(`/task-status/${taskId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching task status:', error);
    throw error;
  }
};