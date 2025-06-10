import React, { useState, createContext, useContext } from 'react';
import PropTypes from 'prop-types';
import { FaCheckCircle, FaExclamationTriangle, FaInfoCircle, FaTimesCircle, FaTimes } from 'react-icons/fa';
import '../../styles/toast1.css' // Import your toast styles

// Create Toast Context
const ToastContext = createContext();

// Simple Toast Component
const Toast = ({ id, message, type, onRemove, isRemoving }) => {
  let IconComponent;
  if (type === 'success') {
    IconComponent = FaCheckCircle;
  } else if (type === 'error') {
    IconComponent = FaTimesCircle;
  } else if (type === 'warning') {
    IconComponent = FaExclamationTriangle;
  } else {
    IconComponent = FaInfoCircle;
  }
  return (
    <div className={`notification-alert variant-${type} ${isRemoving ? 'is-removing' : ''}`} id={`toast-${id}`}>
      <div className="alert-icon">
        <IconComponent />
      </div>
      <div className="alert-message">{message}</div>
      <button className="btn alert-close" onClick={() => onRemove(id)}>
        <FaTimes />
      </button>
    </div>
  );
};

Toast.propTypes = {
  id: PropTypes.number.isRequired,
  message: PropTypes.string.isRequired,
  type: PropTypes.oneOf(['success', 'error', 'warning', 'info']).isRequired,
  onRemove: PropTypes.func.isRequired,
  isRemoving: PropTypes.bool,
};

// Toast Provider Component
const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);  const addToast = (message, type = 'success') => {
    const id = Date.now() + Math.random();
    
    // Add toast to state
    setToasts(prev => [...prev, { id, message, type, isRemoving: false }]);
    
    // Set timeout to remove this specific toast
    setTimeout(() => removeToast(id), 4000);
    
    return id;
  };const markToastAsRemoving = (id) => {
    setToasts(prev => prev.map(toast => 
      toast.id === id ? { ...toast, isRemoving: true } : toast
    ));
  };

  const actuallyRemoveToast = (id) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  };

  const removeToast = (id) => {
    // First, mark the toast as removing to trigger animation
    markToastAsRemoving(id);
    
    // After animation duration, actually remove the toast
    setTimeout(() => actuallyRemoveToast(id), 300);
  };

  const success = (message) => addToast(message, 'success');
  const error = (message) => addToast(message, 'error');
  const warning = (message) => addToast(message, 'warning');
  const info = (message) => addToast(message, 'info');  const clear = () => {
    setToasts([]);
  };

  const value = React.useMemo(() => ({
    success,
    error,
    warning,
    info,
    clear,
    // Backwards compatibility with old names
    showSuccess: success,
    showError: error,
    showWarning: warning,
    showMessage: info,
  }), []);

  return (
    <ToastContext.Provider value={value}>
      {children}      {toasts.length > 0 && (
        <div className="notification-container" id="toast-notification-area">
          {toasts.map(toast => (
            <Toast 
              key={toast.id} 
              id={toast.id}
              message={toast.message}
              type={toast.type}
              isRemoving={toast.isRemoving}
              onRemove={removeToast} 
            />
          ))}
        </div>
      )}
    </ToastContext.Provider>
  );
};

ToastProvider.propTypes = {
  children: PropTypes.node.isRequired,
};

// Custom Hook
const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

export { ToastProvider, useToast }
