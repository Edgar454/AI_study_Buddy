import { useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import FileUpload from '../components/FileUpload';
import AchievementTracker from '../components/AchievementPopup';
import { useStudyStore } from '../stores/studyStore';
import { useAuthStore } from '../stores/authStore';

const Dashboard = () => {
  const { fetchRecentResults, documentsProcessed  , recentResults } = useStudyStore();
  const { user } = useAuthStore();
  const recentResultsLength = Object.keys(recentResults).length;

  useEffect(() => {
    fetchRecentResults();
  }, [fetchRecentResults]);

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-4xl mx-auto">
          <div className="flex flex-col space-y-8">
            {/* Welcome Section */}
            <div className="bg-white rounded-xl shadow-soft p-6">
              <h1 className="text-2xl font-bold text-gray-800 mb-2">
                Welcome back, {user?.username || 'Student'}
              </h1>
              <p className="text-gray-600">
                Upload your study materials and let our AI assistant help you understand them better.
              </p>
              
              {recentResultsLength > 0 && (
                <div className="mt-4 p-3 bg-primary-50 rounded-lg border border-primary-100">
                  <div className="flex items-center">
                    <div className="mr-3 bg-primary-100 rounded-full p-2">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                    </div>
                    <div>
                      <p className="font-medium text-primary-800">
                        You've processed {recentResultsLength} document{recentResultsLength !== 1 ? 's' : ''}!
                      </p>
                      {recentResultsLength >= 5 && (
                        <p className="text-sm text-primary-600">
                          You're on a roll! Keep going to reach more achievements.
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
            
            {/* File Upload Section */}
            <div className="flex justify-center">
              <FileUpload />
            </div>
            
            {/* Tips Section */}
            <div className="bg-white rounded-xl shadow-soft p-6">
              <h2 className="text-xl font-semibold mb-4 text-gray-800">Tips for Better Results</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-secondary-50 rounded-lg border border-secondary-100">
                  <h3 className="font-medium text-secondary-800 mb-2">Clear PDFs</h3>
                  <p className="text-sm text-secondary-700">
                    Upload clear, well-scanned PDFs for the best results. Our AI performs better with high-quality text.
                  </p>
                </div>
                
                <div className="p-4 bg-primary-50 rounded-lg border border-primary-100">
                  <h3 className="font-medium text-primary-800 mb-2">Test Your Knowledge</h3>
                  <p className="text-sm text-primary-700">
                    After reviewing explanations, use the evaluation section to test your understanding of the material.
                  </p>
                </div>
                
                <div className="p-4 bg-accent-50 rounded-lg border border-accent-100">
                  <h3 className="font-medium text-accent-800 mb-2">Use Flashcards</h3>
                  <p className="text-sm text-accent-700">
                    The generated flashcards are perfect for quick review sessions to reinforce your learning.
                  </p>
                </div>
                
                <div className="p-4 bg-success-50 rounded-lg border border-success-100">
                  <h3 className="font-medium text-success-800 mb-2">Regular Practice</h3>
                  <p className="text-sm text-success-700">
                    Maintain your streak by uploading materials regularly to enhance your learning process.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <AchievementTracker />
    </div>
  );
};

export default Dashboard;