import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import ResultContent from '../components/ResultContent';
import { useStudyStore, StudyResult } from '../stores/studyStore';
import { ChevronLeft, Loader } from 'lucide-react';
import { motion } from 'framer-motion';

const ResultPage = () => {
  const { fileId } = useParams<{ fileId: string }>();
  const { recentResults, fetchRecentResults } = useStudyStore();
  const [currentResult, setCurrentResult] = useState<StudyResult | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await fetchRecentResults();
      setLoading(false);
    };
    
    loadData();
  }, [fetchRecentResults]);

  useEffect(() => {
    if (Object.keys(recentResults).length > 0 && fileId) {

      let rawData = recentResults[fileId];
      if (rawData) {
        // Clean up in case of wrapping ```json...``` blocks
        if (rawData.startsWith("```json")) {
          rawData = rawData.replace(/^```json/, "").replace(/```$/, "").trim();
        }
    
        try {
          const result = JSON.parse(rawData);
          setCurrentResult({"result": result});
          console.log('flashcards_dict', result?.flashcard_building);
        } catch (e) {
          console.error('Failed to parse result JSON for', fileId, e);
          setCurrentResult(null);
        }
      } else {
        setCurrentResult(null);
      }
    }
  }, [recentResults, fileId]);

  const handleBackClick = () => {
    navigate('/');
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-4xl mx-auto">
          <button
            onClick={handleBackClick}
            className="mb-4 flex items-center text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ChevronLeft size={20} />
            <span>Back to Dashboard</span>
          </button>
          
          {loading ? (
            <div className="flex justify-center items-center h-64">
              <div className="flex flex-col items-center">
                <Loader size={40} className="text-primary-500 animate-spin mb-4" />
                <p className="text-gray-600">Loading result...</p>
              </div>
            </div>
          ) : !currentResult ? (
            <div className="bg-white rounded-xl shadow-soft p-6 text-center">
              <h2 className="text-xl font-semibold text-gray-800 mb-2">Result Not Found</h2>
              <p className="text-gray-600 mb-4">
                We couldn't find the result you're looking for. It might have been removed or is still processing.
              </p>
              <button
                onClick={handleBackClick}
                className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors"
              >
                Return to Dashboard
              </button>
            </div>
          ) : currentResult.task_id ? (
            <div className="bg-white rounded-xl shadow-soft p-6 text-center">
              <h2 className="text-xl font-semibold text-gray-800 mb-2">Processing in Progress</h2>
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-primary-100 flex items-center justify-center">
                <Loader size={32} className="text-primary-600 animate-spin" />
              </div>
              <p className="text-gray-600 mb-4">
                Your document is still being processed. This may take a few minutes depending on the size and complexity.
              </p>
              <div className="w-full bg-gray-200 rounded-full h-2.5 mb-4">
                <div className="bg-primary-500 h-2.5 rounded-full animate-pulse" style={{ width: '60%' }}></div>
              </div>
              <p className="text-sm text-gray-500">
                You can safely return to the dashboard and check back later.
              </p>
            </div>
          ) : (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <div className="mb-6">
                <h1 className="text-2xl font-bold text-gray-800 mb-2">
                  {currentResult.filename}
                </h1>
                <p className="text-gray-600">
                  Study material processed and analyzed by our AI assistant.
                </p>
              </div>
              
              {currentResult.result && (
                <ResultContent result={currentResult.result} />
              )}
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ResultPage;