import React, { useState } from "react";

function ErrorMessage({ message, id }) {
  const [isVisible, setIsVisible] = useState(true);

  if (!isVisible) return null;

  return (
    <div
      className="mt-4 p-4 bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-700 text-red-800 dark:text-red-200 rounded-lg flex justify-between items-center"
      role="alert"
      aria-live="assertive"
      aria-describedby={id}
    >
      <span className="text-sm">{message}</span>
      <button
        onClick={() => setIsVisible(false)}
        className="text-red-800 dark:text-red-200 hover:text-red-900 dark:hover:text-red-100 font-semibold ml-4"
        aria-label="Dismiss error"
      >
        ×
      </button>
    </div>
  );
}

export default ErrorMessage;
