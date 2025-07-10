import React, { useState } from "react";

function ErrorMessage({ message }) {
  const [isVisible, setIsVisible] = useState(true);

  if (!isVisible) return null;

  return (
    <div
      className="mt-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded flex justify-between items-center"
      role="alert"
      aria-live="assertive"
    >
      <span>{message}</span>
      <button
        onClick={() => setIsVisible(false)}
        className="text-red-700 hover:text-red-900 font-semibold"
        aria-label="Dismiss error"
      >
        &times;
      </button>
    </div>
  );
}

export default ErrorMessage;
