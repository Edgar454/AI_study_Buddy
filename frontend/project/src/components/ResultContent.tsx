import { useState, useEffect } from 'react';
import { BookOpen, Award, Brain, FileDigit, CheckSquare, Maximize } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import Markdown from 'react-markdown'
import "./components.css"

interface ResultContentProps {
  result: {
    explanation: string;
    evaluation: string;
    flashcard_building: string;
    summary: string;
  };
}

type TabType = 'explanation' | 'evaluation' | 'flashcards' | 'summary';

const ResultContent = ({ result }: ResultContentProps) => {
  const [activeTab, setActiveTab] = useState<TabType>('explanation');
  const [visibleText, setVisibleText] = useState('');
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, string>>({});
  const [flippedCards, setFlippedCards] = useState<Record<string, boolean>>({});

  // Streaming effect for explanation
  useEffect(() => {
    if (activeTab === 'explanation') {
      setVisibleText('');
      let index = 0;
      const text = result.explanation;
      
      const interval = setInterval(() => {
        if (index < text.length) {
          setVisibleText(prev => prev + text[index]);
          index++;
        } else {
          clearInterval(interval);
        }
      }, 0.1); // Adjust speed as needed

      return () => clearInterval(interval);
    }
  }, [activeTab, result.explanation]);

  const parseJsonContentExplain = (jsonString: string) => {
    try {
      const cleanedString = jsonString.replace(/```json|```/g, '').trim();
      console.log("cleanedString", cleanedString)
      return JSON.parse(cleanedString);
    } catch (error) {
      console.error('Error parsing JSON:', error);
      return null;
    }
  };

  const parseJsonContent = (raw) => {
    if (!raw || typeof raw !== "string") return null;
  
    let clean = raw.trim();
    
    const jsonBlockMatch = clean.match(/```json\s*([\s\S]*?)```/);
    if (jsonBlockMatch) {
      clean = jsonBlockMatch[1].trim();
    }
  
    // Remove ```json blocks
    if (clean.startsWith("```")) {
      clean = clean
        .replace(/^```(json)?/, "") // remove opening ``` or ```json
        .replace(/```$/, "")        // remove trailing ```
        .trim();
    }
    
  
    // Check for unterminated string before final brackets
    const lastQuote = clean.lastIndexOf('"');
    const lastColon = clean.lastIndexOf(':');
  
    const likelyBroken = clean.slice(lastColon, lastQuote).includes('verso');
    if (likelyBroken && !clean.endsWith('"') && !clean.endsWith('"}]}')) {
      // Trim to before broken string
      const versoStart = clean.lastIndexOf('"verso"');
      clean = clean.slice(0, versoStart).trim();
  
      // Add a placeholder verso and valid ending
      clean += `"verso": "INCOMPLETE - truncated by model"}]}`
    } else if (clean.endsWith('}')) {
      // Do nothing here either.
    }
    else if (!clean.endsWith('}]}}')) {
      // If just slightly off
      clean += '"}]}}';
    }
    console.log("clean", clean)
    try {
      return JSON.parse(clean);
    } catch (e) {
      console.error("Failed to parse flashcard JSON:", e);
      return null;
    }
  };
  
  

  const evaluationData = result.evaluation ? parseJsonContent(result.evaluation) : null;
  const flashcardsData = result.flashcard_building ? parseJsonContent(result.flashcard_building) : null;

  const tabs = [
    { id: 'explanation', label: 'Explanation', icon: <BookOpen size={18} /> },
    { id: 'evaluation', label: 'Evaluation', icon: <CheckSquare size={18} /> },
    { id: 'flashcards', label: 'Flashcards', icon: <Brain size={18} /> },
    { id: 'summary', label: 'Summary', icon: <FileDigit size={18} /> },
  ];

  const handleAnswerSelect = (questionIndex: string, answer: string) => {
    setSelectedAnswers(prev => ({
      ...prev,
      [questionIndex]: answer
    }));
  };

  const toggleCard = (cardId: string) => {
    setFlippedCards(prev => ({
      ...prev,
      [cardId]: !prev[cardId]
    }));
  };

  const getCaseInsensitiveValue = (obj: Record<string, any>, ...possibleKeys: string[]): any => {
    const lowerCased = Object.keys(obj).reduce((acc, key) => {
      acc[key.toLowerCase()] = key;
      return acc;
    }, {} as Record<string, string>);
  
    for (const k of possibleKeys) {
      const actualKey = lowerCased[k.toLowerCase()];
      if (actualKey && obj[actualKey] !== undefined) return obj[actualKey];
    }
  
    return undefined;
  };
  

  const renderEvaluation = () => {
    if (!evaluationData || !evaluationData.evaluation_dict) {
      return <p>No evaluation data available</p>;
    }

    return (
      <div className="space-y-8">
        {Object.entries(evaluationData.evaluation_dict).map(([level, questions]: [string, any]) => (
          <div key={level} className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-800">{level} Level</h3>
            
            {questions.map((q: any, idx: number) => (
              <div key={idx} className="bg-white rounded-lg p-4 shadow-sm border border-gray-100">
                <p className="font-medium text-gray-800 mb-3">{q.question}</p>
                
                <div className="space-y-2">
                  {q.options.map((option: string, optIdx: number) => {
                    const optionLetter = String.fromCharCode(97 + optIdx);
                    const isSelected = selectedAnswers[`${level}-${idx}`] === optionLetter;
                    const isCorrect = q.answer === optionLetter;
                    const showResult = isSelected;
                    
                    return (
                      <motion.div 
                        key={optIdx}
                        onClick={() => handleAnswerSelect(`${level}-${idx}`, optionLetter)}
                        className={`p-2 rounded-md flex items-start space-x-2 cursor-pointer transition-colors ${
                          showResult
                            ? isCorrect
                              ? 'bg-green-50 border border-green-200'
                              : isSelected
                              ? 'bg-red-50 border border-red-200'
                              : 'bg-gray-50'
                            : 'bg-gray-50 hover:bg-gray-100'
                        }`}
                        whileHover={{ scale: 1.01 }}
                        whileTap={{ scale: 0.99 }}
                      >
                        <div className={`w-6 h-6 rounded-full flex items-center justify-center shrink-0 ${
                          showResult
                            ? isCorrect
                              ? 'bg-green-500 text-white'
                              : isSelected
                              ? 'bg-red-500 text-white'
                              : 'bg-gray-200 text-gray-700'
                            : 'bg-gray-200 text-gray-700'
                        }`}>
                          {optionLetter}
                        </div>
                        <p className={showResult
                          ? isCorrect
                            ? 'text-green-800'
                            : isSelected
                            ? 'text-red-800'
                            : 'text-gray-700'
                          : 'text-gray-700'
                        }>
                          {option.substring(3)}
                        </p>
                      </motion.div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        ))}
      </div>
    );
  };

  const renderFlashcards = () => {
    if (!flashcardsData || !flashcardsData.flascard_dict) {
      return <p>No flashcard data available</p>;
    }

    return (
      <div className="space-y-8">
        {Object.entries(flashcardsData.flascard_dict).map(([level, cards]: [string, any]) => (
          <div key={level} className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-800">{level} Level</h3>
            
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              {cards.map((card: any, idx: number) => {
                const cardId = `${level}-${idx}`;
                const isFlipped = flippedCards[cardId];

                return (
                  <motion.div
                    key={idx}
                    className="relative h-64 cursor-pointer perspective"
                    onClick={() => toggleCard(cardId)}
                  >
                    <motion.div
                      className={`relative w-full h-full transition-transform duration-500 transform-style-preserve-3d ${
                        isFlipped ? "rotate-y-180" : ""
                      }`}
                    >
                      {/* Front */}
                      <div className="absolute w-full h-full backface-hidden bg-white rounded-lg shadow-sm border border-gray-100">
                        <div className="bg-primary-50 p-3 border-b border-primary-100">
                          <p className="text-sm text-primary-800 font-medium">
                          {getCaseInsensitiveValue(card, "section")}
                          </p>
                        </div>
                        <div className="p-4">
                          <p className="font-medium text-gray-800">{getCaseInsensitiveValue(card, "recto","front","question", "Recto (Question)")}
                          </p>
                          <p className="text-sm text-gray-500 mt-2">Click to reveal answer</p>
                        </div>
                      </div>

                      {/* Back */}
                      <div className="absolute w-full h-full backface-hidden rotate-y-180 bg-white rounded-lg shadow-sm border border-gray-100">
                        <div className="bg-primary-50 p-3 border-b border-primary-100">
                          <p className="text-sm text-primary-800 font-medium">
                            {card.section||card?.Section}
                          </p>
                        </div>
                        <div className="p-4">
                          <p className="font-medium text-gray-800">{getCaseInsensitiveValue(card, "verso","back", "answer", "Verso (Réponse)")}</p>
                          <p className="text-sm text-gray-500 mt-2">Click to see question</p>
                        </div>
                      </div>
                    </motion.div>
                  </motion.div>

                );
              })}
            </div>
          </div>
        ))}
      </div>
    );
  };
  
  return (
    <div className="bg-white rounded-xl shadow-soft p-6">
      <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg mb-6">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as TabType)}
            className={`flex items-center space-x-2 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeTab === tab.id
                ? 'bg-white text-primary-700 shadow-sm'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-200'
            }`}
          >
            {tab.icon}
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      <motion.div
        key={activeTab}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.2 }}
        className="mt-4"
      >
        {activeTab === 'explanation' && (
          <div className="prose max-w-none">
            <Markdown>{visibleText}</Markdown>
          </div>
        )}

        {activeTab === 'evaluation' && renderEvaluation()}

        {activeTab === 'flashcards' && renderFlashcards()}

        {activeTab === 'summary' && (
          <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-800 mb-3">Summary</h3>
            <p className="text-gray-700 leading-relaxed">{result.summary}</p>
          </div>
        )}
      </motion.div>
    </div>
  );
};

export default ResultContent;