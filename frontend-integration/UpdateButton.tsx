/**
 * Update Button Component for 4Paws Frontend
 * Place this in: src/components/UpdateButton.tsx
 * 
 * Usage in Layout/Topbar:
 * import UpdateButton from '@/components/UpdateButton';
 * <UpdateButton />
 */

'use client';

import { useState, useEffect } from 'react';
import { io, Socket } from 'socket.io-client';
import UpdateModal from './UpdateModal';

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

const AGENT_URL = process.env.NEXT_PUBLIC_AGENT_URL || 'http://localhost:5000';

export default function UpdateButton() {
  const [updateAvailable, setUpdateAvailable] = useState(false);
  const [updateInfo, setUpdateInfo] = useState<UpdateInfo | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [updating, setUpdating] = useState(false);
  const [checkingUpdate, setCheckingUpdate] = useState(false);

  // Check for updates on mount and every 30 minutes
  useEffect(() => {
    checkForUpdates();
    const interval = setInterval(checkForUpdates, 30 * 60 * 1000); // 30 minutes
    return () => clearInterval(interval);
  }, []);

  // Auto-show modal when update is available
  useEffect(() => {
    if (updateAvailable && updateInfo && !updating) {
      // Show modal after 3 seconds
      const timer = setTimeout(() => {
        setShowModal(true);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [updateAvailable, updateInfo, updating]);

  const checkForUpdates = async () => {
    if (checkingUpdate) return;
    
    setCheckingUpdate(true);
    try {
      const res = await fetch(`${AGENT_URL}/api/update/check`);
      const data: UpdateInfo = await res.json();
      
      if (data.has_update) {
        setUpdateAvailable(true);
        setUpdateInfo(data);
        console.log('Update available:', data);
      } else {
        setUpdateAvailable(false);
        setUpdateInfo(data);
      }
    } catch (error) {
      console.error('Failed to check updates:', error);
    } finally {
      setCheckingUpdate(false);
    }
  };

  const handleUpdate = async () => {
    setUpdating(true);
    
    try {
      // Start update
      const res = await fetch(`${AGENT_URL}/api/update/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ component: 'all' })
      });
      
      const result = await res.json();
      
      if (result.success) {
        console.log('Update started successfully');
        // Modal will handle the rest via WebSocket
      } else {
        alert('Failed to start update: ' + (result.error || 'Unknown error'));
        setUpdating(false);
      }
    } catch (error) {
      console.error('Update failed:', error);
      alert('Failed to start update. Please try again.');
      setUpdating(false);
    }
  };

  const handleUpdateComplete = () => {
    setUpdating(false);
    setUpdateAvailable(false);
    setShowModal(false);
    
    // Reload page after 2 seconds
    setTimeout(() => {
      window.location.reload();
    }, 2000);
  };

  return (
    <>
      {/* Update Button */}
      <button
        onClick={() => checkingUpdate ? null : updateAvailable ? setShowModal(true) : checkForUpdates()}
        className={`relative p-2 rounded-lg transition-all ${
          updateAvailable 
            ? 'text-orange-500 hover:bg-orange-50 dark:hover:bg-orange-900/20 animate-pulse' 
            : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
        }`}
        title={updateAvailable ? 'Update Available!' : 'Check for Updates'}
        disabled={checkingUpdate}
      >
        <span className="text-xl">
          {checkingUpdate ? '⏳' : '🔄'}
        </span>
        
        {/* Red Dot Indicator */}
        {updateAvailable && (
          <span className="absolute top-1 right-1 flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
          </span>
        )}
      </button>

      {/* Update Modal */}
      {showModal && updateInfo && (
        <UpdateModal
          updateInfo={updateInfo}
          updating={updating}
          onUpdate={handleUpdate}
          onClose={() => setShowModal(false)}
          onComplete={handleUpdateComplete}
        />
      )}
    </>
  );
}

