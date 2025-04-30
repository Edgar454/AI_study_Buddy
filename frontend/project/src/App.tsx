import { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import ResultPage from './pages/ResultPage';
import ProtectedRoute from './components/ProtectedRoute';
import { useAuthStore } from './stores/authStore';

function App() {
  const { isAuthenticated, initAuth } = useAuthStore();

  useEffect(() => {
    initAuth();
  }, [initAuth]);

  return (
    <Routes>
      <Route path="/login" element={!isAuthenticated ? <Login /> : <Navigate to="/" />} />
      <Route path="/register" element={!isAuthenticated ? <Register /> : <Navigate to="/" />} />
      <Route 
        path="/" 
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/result/:fileId" 
        element={
          <ProtectedRoute>
            <ResultPage />
          </ProtectedRoute>
        } 
      />
    </Routes>
  );
}

export default App;