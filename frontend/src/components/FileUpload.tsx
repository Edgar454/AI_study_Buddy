import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { FileUp, File, X, AlertCircle } from 'lucide-react';
import { toast } from 'react-toastify';
import { useStudyStore } from '../stores/studyStore';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

const FileUpload = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const { processFile, processingStatus, processingProgress, checkTaskStatus } = useStudyStore();
  const [polling, setPolling] = useState(false);
  const navigate = useNavigate();

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      if (file.type !== 'application/pdf') {
        toast.error('Only PDF files are supported');
        return;
      }
      
      setSelectedFile(file);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    maxFiles: 1
  });

  const handleUpload = async () => {
    if (!selectedFile) {
      toast.warning('Please select a file first');
      return;
    }

    try {
      const {taskId , file_id} = await processFile(selectedFile);
      
      if (taskId === 'completed') {
        toast.success('File processed successfully (from cache)!');
        navigate(`/result/${file_id}`);
        return;
      }
      
      if (taskId) {
        toast.info('Processing started. This may take a few moments...');
        
        setPolling(true);
        const pollInterval = setInterval(async () => {
          const status = await checkTaskStatus(taskId);
          
          if (status.status === 'Success' || status.status === 'Failure') {
            clearInterval(pollInterval);
            setPolling(false);
            
            if (status.status === 'Success') {
              toast.success('File processed successfully!');
              navigate(`/result/${file_id}`);
            } else {
              toast.error('Failed to process file');
            }
          }
        }, 2000);
      }
    } catch (error) {
      toast.error('Error processing file');
    }
  };

  const clearSelectedFile = () => {
    setSelectedFile(null);
  };

  return (
    <div className="w-full max-w-xl">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="p-6 bg-white rounded-xl shadow-soft"
      >
        <h2 className="text-xl font-semibold mb-4 text-gray-800">Upload Study Material</h2>
        
        {processingStatus === 'pending' ? (
          <div className="space-y-4">
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div 
                className="bg-primary-500 h-2.5 rounded-full transition-all duration-300" 
                style={{ width: `${processingProgress}%` }}
              ></div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Processing your document...</span>
              <span className="text-sm font-medium">{processingProgress}%</span>
            </div>
            <p className="text-sm text-gray-500 italic">
              Our AI is analyzing your document. This may take a minute.
            </p>
          </div>
        ) : selectedFile ? (
          <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
            <div className="flex items-start justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-lg bg-primary-100 flex items-center justify-center">
                  <File size={20} className="text-primary-600" />
                </div>
                <div>
                  <p className="font-medium truncate max-w-xs">{selectedFile.name}</p>
                  <p className="text-xs text-gray-500">
                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              </div>
              <button 
                onClick={clearSelectedFile}
                className="text-gray-400 hover:text-gray-600"
              >
                <X size={18} />
              </button>
            </div>
            
            <button
              onClick={handleUpload}
              disabled={processingStatus === 'pending' || polling}
              className="mt-4 w-full flex items-center justify-center space-x-2 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <FileUp size={18} />
              <span>Process Document</span>
            </button>
          </div>
        ) : (
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              isDragActive ? 'border-primary-400 bg-primary-50' : 'border-gray-300 hover:border-primary-300 hover:bg-gray-50'
            }`}
          >
            <input {...getInputProps()} />
            <div className="flex flex-col items-center justify-center space-y-3">
              <div className="w-12 h-12 rounded-full bg-primary-100 flex items-center justify-center">
                <FileUp size={20} className="text-primary-500" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-700">
                  {isDragActive ? 'Drop the file here' : 'Drag & drop a PDF file here'}
                </p>
                <p className="text-xs text-gray-500 mt-1">or click to browse</p>
              </div>
            </div>
          </div>
        )}
        
        <div className="mt-4 flex items-start space-x-2 text-sm text-gray-500">
          <AlertCircle size={16} className="shrink-0 mt-0.5" />
          <p>Only PDF files are supported. Maximum file size is 10MB.</p>
        </div>
      </motion.div>
    </div>
  );
};

export default FileUpload;