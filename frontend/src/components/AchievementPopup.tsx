import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Award, Trophy, Star, X } from 'lucide-react';
import { useStudyStore } from '../stores/studyStore';

interface AchievementPopupProps {
  onClose: () => void;
}

const AchievementPopup = ({ onClose }: AchievementPopupProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8, y: 20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.8, y: 20 }}
      className="fixed bottom-6 right-6 p-4 bg-white rounded-lg shadow-card max-w-xs w-full border-l-4 border-accent-500 z-50"
    >
      <div className="flex items-start">
        <div className="mr-3 flex-shrink-0">
          <div className="w-12 h-12 rounded-full bg-accent-100 flex items-center justify-center">
            <Trophy size={24} className="text-accent-500" />
          </div>
        </div>
        <div className="flex-1">
          <h3 className="font-bold text-gray-900 mb-1">Milestone Reached! 🎉</h3>
          <p className="text-sm text-gray-600 mb-2">
            You've processed your 5th document! Keep up the great work.
          </p>
          <div className="flex space-x-1">
            {[...Array(5)].map((_, i) => (
              <Star key={i} size={16} className="text-yellow-400 fill-yellow-400" />
            ))}
          </div>
        </div>
        <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
          <X size={18} />
        </button>
      </div>
    </motion.div>
  );
};

const AchievementTracker = () => {
  const { documentsProcessed } = useStudyStore();
  const [showAchievement, setShowAchievement] = useState(false);
  const [achievementType, setAchievementType] = useState<'five' | 'ten' | 'fifteen' | 'twenty'>('five');

  useEffect(() => {
    // Check for milestones
    if (documentsProcessed === 5) {
      setAchievementType('five');
      setShowAchievement(true);
    } else if (documentsProcessed === 10) {
      setAchievementType('ten');
      setShowAchievement(true);
    } else if (documentsProcessed === 15) {
      setAchievementType('fifteen');
      setShowAchievement(true);
    } else if (documentsProcessed === 20) {
      setAchievementType('twenty');
      setShowAchievement(true);
    }
  }, [documentsProcessed]);

  return (
    <AnimatePresence>
      {showAchievement && (
        <AchievementPopup onClose={() => setShowAchievement(false)} />
      )}
    </AnimatePresence>
  );
};

export default AchievementTracker;