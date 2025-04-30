import { create } from 'zustand';
import { getRecentResults, processMaterial, getTaskStatus } from '../services/api';

export interface StudyResult {
  filename: string;
  result?: {
    explanation: string;
    evaluation: string;
    flashcard_building: string;
    summary: string;
  };
  task_id?: string;
}

// Demo data for testing
const demoResults: StudyResult[] = [
  {
    filename: "Introduction_to_Psychology.pdf",
    result: {
      explanation: "# Introduction to Psychology\n\nPsychology is the scientific study of behavior and mental processes...",
      evaluation: JSON.stringify({
        evaluation_dict: {
          "Beginner": [
            {
              question: "What is psychology?",
              options: [
                "a) Study of plants",
                "b) Study of behavior and mental processes",
                "c) Study of society",
                "d) Study of economics"
              ],
              answer: "b"
            }
          ]
        }
      }),
      flashcard_building: JSON.stringify({
        flascard_dict: {
          "Beginner": [
            {
              section: "Introduction",
              recto: "What is psychology?",
              verso: "Psychology is the scientific study of behavior and mental processes"
            }
          ]
        }
      }),
      summary: "This chapter introduces the fundamental concepts of psychology..."
    }
  },
  {
    filename: "Cognitive_Science.pdf",
    result: {
      explanation: "# Cognitive Science\n\nCognitive science is the interdisciplinary study of the mind...",
      evaluation: JSON.stringify({
        evaluation_dict: {
          "Beginner": [
            {
              question: "What is cognitive science?",
              options: [
                "a) Study of cognition and mental processes",
                "b) Study of computers",
                "c) Study of biology",
                "d) Study of physics"
              ],
              answer: "a"
            }
          ]
        }
      }),
      flashcard_building: JSON.stringify({
        flascard_dict: {
          "Beginner": [
            {
              section: "Introduction",
              recto: "What is cognitive science?",
              verso: "Cognitive science is the interdisciplinary study of the mind"
            }
          ]
        }
      }),
      summary: "This material covers the basics of cognitive science..."
    }
  }
];

type ProcessFileResponse = {
  taskId: string;
  file_id: string;
};

interface StudyState {
  recentResults: StudyResult[];
  currentTaskId: string | null;
  processingStatus: 'idle' | 'pending' | 'success' | 'failure';
  processingProgress: number;
  documentsProcessed: number;
  currentStreak: number;
  fetchRecentResults: () => Promise<void>;
  processFile: (file: File) => Promise<ProcessFileResponse>;
  checkTaskStatus: (taskId: string) => Promise<any>;
  incrementDocumentsProcessed: () => void;
  incrementStreak: () => void;
  resetStreak: () => void;
  useDemo: boolean;
}

export const useStudyStore = create<StudyState>((set, get) => ({
  recentResults: [],
  currentTaskId: null,
  processingStatus: 'idle',
  processingProgress: 0,
  documentsProcessed: parseInt(localStorage.getItem('documentsProcessed') || '0', 10),
  currentStreak: parseInt(localStorage.getItem('currentStreak') || '0', 10),
  useDemo: false, // Set to true to use demo data

  fetchRecentResults: async () => {
    try {
      console.log("useDemo is", get().useDemo);
      if (get().useDemo) {
        set({ recentResults: demoResults });
        return;
      }
      const results = await getRecentResults();
      set({ recentResults: results });
    } catch (error) {
      console.error('Error fetching recent results:', error);
      // Fallback to demo data on error
      set({ recentResults: demoResults });
    }
  },

  
  processFile: async (file) => {
    set({ processingStatus: 'pending', processingProgress: 0 });
    
    try {
      const response = await processMaterial(file);
      
      if (response.task_id) {
        set({ 
          currentTaskId: response.task_id,
          processingProgress: 10
        });
        return {
          taskId: response.task_id,
          file_id: response.file_id
        };
      } else if (response.result) {
        set({ 
          processingStatus: 'success',
          processingProgress: 100
        });
        return 'completed';
      }
      
      return '';
    } catch (error) {
      set({ processingStatus: 'failure', processingProgress: 0 });
      console.error('Error processing file:', error);
      throw error;
    }
  },

  checkTaskStatus: async (taskId) => {
    try {
      if (get().useDemo) {
        return { status: 'Success' };
      }

      const status = await getTaskStatus(taskId);
      
      if (status.status === 'Success') {
        set({ 
          processingStatus: 'success',
          processingProgress: 100
        });
        
        await get().fetchRecentResults();
        get().incrementDocumentsProcessed();
        get().incrementStreak();
      } else if (status.status === 'Failure') {
        set({ processingStatus: 'failure' });
      } else {
        const progressMap: Record<string, number> = {
          'Pending': 30,
          'PROGRESS': 50,
          'STARTED': 70
        };
        
        const progress = progressMap[status.status] || 30;
        set({ processingProgress: progress });
      }
      
      return status;
    } catch (error) {
      console.error('Error checking task status:', error);
      return { status: 'Error' };
    }
  },

  incrementDocumentsProcessed: () => {
    const currentCount = get().documentsProcessed;
    const newCount = currentCount + 1;
    localStorage.setItem('documentsProcessed', newCount.toString());
    set({ documentsProcessed: newCount });
  },

  incrementStreak: () => {
    const currentStreak = get().currentStreak;
    const newStreak = currentStreak + 1;
    localStorage.setItem('currentStreak', newStreak.toString());
    set({ currentStreak: newStreak });
  },

  resetStreak: () => {
    localStorage.setItem('currentStreak', '0');
    set({ currentStreak: 0 });
  }
}));