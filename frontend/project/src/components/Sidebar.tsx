import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { BookOpen, Award, BarChart, LogOut } from 'lucide-react';
import { useStudyStore } from '../stores/studyStore';
import { useAuthStore } from '../stores/authStore';
import { motion } from 'framer-motion';

const Sidebar = () => {
  const { recentResults, fetchRecentResults, documentsProcessed, currentStreak } = useStudyStore();
  const { logout, user } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    fetchRecentResults();
  }, [fetchRecentResults, location.pathname]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getRewardLevel = (count: number) => {
    if (count >= 20) return 'Gold';
    if (count >= 15) return 'Silver';
    if (count >= 10) return 'Bronze';
    if (count >= 5) return 'Beginner';
    return 'New';
  };

  return (
    <div className="h-full w-64 bg-white shadow-md flex flex-col">
      {/* User profile section */}
      <div className="p-4 border-b">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
            <span className="text-primary-700 font-bold text-lg">
              {user?.username.charAt(0).toUpperCase()}
            </span>
          </div>
          <div>
            <h3 className="font-medium">{user?.username}</h3>
            <p className="text-xs text-gray-500">{user?.role || 'Student'}</p>
          </div>
        </div>
      </div>
      
      {/* Stats section */}
      <div className="p-4 border-b">
        <h4 className="font-medium text-sm text-gray-500 mb-3">Your Progress</h4>
        
        <motion.div 
          className="flex items-center space-x-3 mb-3"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <div className="w-8 h-8 rounded-full bg-secondary-100 flex items-center justify-center">
            <BookOpen size={16} className="text-secondary-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">Documents</p>
            <p className="font-medium">{documentsProcessed}</p>
          </div>
        </motion.div>
        
        <motion.div 
          className="flex items-center space-x-3 mb-3"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center">
            <BarChart size={16} className="text-primary-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">Current Streak</p>
            <p className="font-medium">{currentStreak} days</p>
          </div>
        </motion.div>
        
        <motion.div 
          className="flex items-center space-x-3"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <div className="w-8 h-8 rounded-full bg-accent-100 flex items-center justify-center">
            <Award size={16} className="text-accent-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">Reward Level</p>
            <p className="font-medium">{getRewardLevel(documentsProcessed)}</p>
          </div>
        </motion.div>
      </div>
      
      {/* Recent Materials */}
      <div className="flex-1 overflow-y-auto p-4">
        <h4 className="font-medium text-sm text-gray-500 mb-3">Recent Materials</h4>
        
        {Object.keys(recentResults).length > 0 ? (
          <div className="space-y-2">
          {Object.entries(recentResults)
            .slice(0, 5)
            .map(([filename, rawData], index) => {
              let cleanData = rawData;
        
              // Remove ```json and ``` if present
              if (cleanData.startsWith("```json")) {
                cleanData = cleanData.replace(/^```json/, "").replace(/```$/, "").trim();
              }
        
              let item;
              try {
                item = JSON.parse(cleanData);
              } catch (e) {
                console.error(`Failed to parse JSON for file ${filename}`, e);
                return null; // Skip this item
              }
        
              return (
                <motion.div
                  key={filename}
                  className="p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors"
                  onClick={() => navigate(`/result/${filename}`)}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 * index }}
                >
                  <p className="text-sm font-medium truncate">{filename}</p>
                  {item.task_id ? (
                    <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-0.5 rounded-full">
                      Processing
                    </span>
                  ) : (
                    <span className="text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded-full">
                      Completed
                    </span>
                  )}
                </motion.div>
              );
            })}
        </div>        
        ) : (
          <p className="text-sm text-gray-500">No recent materials found</p>
        )}
      </div>
      
      {/* Logout button */}
      <div className="p-4 border-t">
        <button
          onClick={handleLogout}
          className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors"
        >
          <LogOut size={18} />
          <span>Logout</span>
        </button>
      </div>
    </div>
  );
};

export default Sidebar;