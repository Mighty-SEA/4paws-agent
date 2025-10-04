/**
 * Update Modal Component
 * Place this in: src/components/UpdateModal.tsx
 */

'use client';

import { useEffect, useState } from 'react';
import { io, Socket } from 'socket.io-client';

interface UpdateInfo {
  current: {
    frontend: string;
    backend: string;
  };
  latest: {
    frontend?: string;
    backend?: string;
  };
  has_update: boolean;
  details: {
    frontend: {
      current: string;
      latest: string | null;
      has_update: boolean;
    };
    backend: {
      current: string;
      latest: string | null;
      has_update: boolean;
    };
  };
}

interface UpdateStatus {
  status: string;
  message: string;
  progress: number;
}

interface Props {
  updateInfo: UpdateInfo;
  updating: boolean;
  onUpdate: () => void;
  onClose: () => void;
  onComplete: () => void;
}

const AGENT_URL = process.env.NEXT_PUBLIC_AGENT_URL || 'http://localhost:5000';

export default function UpdateModal({ updateInfo, updating, onUpdate, onClose, onComplete }: Props) {
  const [updateStatus, setUpdateStatus] = useState<UpdateStatus>({
    status: 'ready',
    message: 'Ready to update',
    progress: 0
  });
  const [socket, setSocket] = useState<Socket | null>(null);

  // Setup WebSocket connection when updating starts
  useEffect(() => {
    if (updating && !socket) {
      const newSocket = io(AGENT_URL);
      
      newSocket.on('update_status', (data: UpdateStatus) => {
        console.log('Update status:', data);
        setUpdateStatus(data);
        
        if (data.status === 'completed') {
          setTimeout(() => {
            onComplete();
          }, 2000);
        } else if (data.status === 'failed') {
          setTimeout(() => {
            alert('Update failed! Please check the agent logs.');
            window.location.reload();
          }, 3000);
        }
      });
      
      setSocket(newSocket);
      
      return () => {
        newSocket.disconnect();
      };
    }
  }, [updating]);

  // Prevent closing modal during update
  const handleClose = () => {
    if (updating) {
      if (confirm('Update is in progress. Are you sure you want to close?')) {
        onClose();
      }
    } else {
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-md w-full mx-4 overflow-hidden">
        {!updating ? (
          // Initial Update Info
          <div className="p-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold flex items-center gap-2">
                <span>🎉</span>
                <span>Update Available!</span>
              </h2>
              <button
                onClick={handleClose}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <p className="text-gray-600 dark:text-gray-400 mb-6">
              A new version is available. Update now to get the latest features and improvements!
            </p>
            
            {/* Update Details */}
            <div className="space-y-3 mb-6">
              {updateInfo.details.frontend.has_update && (
                <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                  <div className="flex items-center justify-between mb-1">
                    <p className="font-semibold text-blue-900 dark:text-blue-100">
                      🎨 Frontend
                    </p>
                    <span className="text-xs bg-blue-500 text-white px-2 py-1 rounded">NEW</span>
                  </div>
                  <p className="text-sm text-blue-700 dark:text-blue-300">
                    <span className="font-mono">{updateInfo.details.frontend.current}</span>
                    {' → '}
                    <span className="font-mono font-bold">{updateInfo.details.frontend.latest}</span>
                  </p>
                </div>
              )}
              
              {updateInfo.details.backend.has_update && (
                <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                  <div className="flex items-center justify-between mb-1">
                    <p className="font-semibold text-green-900 dark:text-green-100">
                      🔧 Backend
                    </p>
                    <span className="text-xs bg-green-500 text-white px-2 py-1 rounded">NEW</span>
                  </div>
                  <p className="text-sm text-green-700 dark:text-green-300">
                    <span className="font-mono">{updateInfo.details.backend.current}</span>
                    {' → '}
                    <span className="font-mono font-bold">{updateInfo.details.backend.latest}</span>
                  </p>
                </div>
              )}
            </div>
            
            {/* Action Buttons */}
            <div className="flex gap-3">
              <button
                onClick={onUpdate}
                className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all font-semibold shadow-lg hover:shadow-xl"
              >
                Update Now
              </button>
              <button
                onClick={handleClose}
                className="flex-1 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 py-3 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-all font-semibold"
              >
                Later
              </button>
            </div>

            <p className="text-xs text-gray-500 dark:text-gray-400 text-center mt-4">
              ⚠️ The application will restart during the update process
            </p>
          </div>
        ) : (
          // Update Progress
          <div className="p-8">
            <UpdateProgress status={updateStatus} />
          </div>
        )}
      </div>
    </div>
  );
}

// Update Progress Component
function UpdateProgress({ status }: { status: UpdateStatus }) {
  const statusConfig: Record<string, { icon: string; color: string }> = {
    stopping_services: { icon: '⏹️', color: 'text-red-500' },
    downloading: { icon: '📥', color: 'text-blue-500' },
    extracting: { icon: '📦', color: 'text-purple-500' },
    migrating: { icon: '🗄️', color: 'text-yellow-500' },
    restarting: { icon: '🔄', color: 'text-green-500' },
    completed: { icon: '✅', color: 'text-green-500' },
    failed: { icon: '❌', color: 'text-red-500' }
  };

  const current = statusConfig[status.status] || statusConfig.downloading;

  return (
    <div className="text-center">
      {/* Animated Icon */}
      <div className={`text-6xl mb-6 ${status.status === 'completed' ? 'animate-bounce' : 'animate-pulse'}`}>
        {current.icon}
      </div>
      
      {/* Status Title */}
      <h3 className={`text-2xl font-bold mb-2 ${current.color}`}>
        {status.status === 'completed' ? 'Update Complete!' : 
         status.status === 'failed' ? 'Update Failed' : 
         'Updating 4Paws...'}
      </h3>
      
      {/* Status Message */}
      <p className="text-gray-600 dark:text-gray-400 mb-6">
        {status.message}
      </p>
      
      {/* Progress Bar */}
      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 mb-4 overflow-hidden">
        <div 
          className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full transition-all duration-500 ease-out"
          style={{ width: `${status.progress}%` }}
        />
      </div>
      
      {/* Progress Percentage */}
      <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">
        {status.progress}%
      </p>
      
      {/* Additional Info */}
      {status.status !== 'completed' && status.status !== 'failed' && (
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Please wait, this may take a few minutes...
          <br />
          <span className="text-xs">Do not close this window</span>
        </p>
      )}
      
      {status.status === 'completed' && (
        <div className="mt-4">
          <p className="text-green-600 dark:text-green-400 font-semibold animate-pulse">
            Reloading application in 2 seconds...
          </p>
          <div className="mt-3 flex items-center justify-center gap-1">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
            <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
            <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
          </div>
        </div>
      )}
      
      {status.status === 'failed' && (
        <p className="text-red-600 dark:text-red-400 mt-4">
          Please check the agent logs and try again.
        </p>
      )}
    </div>
  );
}

