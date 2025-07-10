import React from "react";
import ProgressBar from "react-progressbar";

function ClassificationResultCard({ result }) {
  const confidencePercentage = Math.round(result.confidence * 100);

  return (
    <div
      className="mt-6 p-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700"
      role="region"
      aria-label="Classification Result"
    >
      <h2 className="text-2xl font-semibold mb-4 text-gray-800 dark:text-gray-200">Classification Result</h2>
      <ul className="space-y-3 text-sm">
        <li>
          <span className="font-medium text-gray-700 dark:text-gray-300">Category:</span>{" "}
          <span>{result.category}</span>
        </li>
        <li>
          <span className="font-medium text-gray-700 dark:text-gray-300">Priority:</span>{" "}
          <span>{result.priority}</span>
        </li>
        <li>
          <span className="font-medium text-gray-700 dark:text-gray-300">Intent:</span>{" "}
          <span>{result.intent}</span>
        </li>
        <li>
          <span className="font-medium text-gray-700 dark:text-gray-300">Queue:</span>{" "}
          <span>{result.recommended_queue}</span>
        </li>
        <li>
          <span className="font-medium text-gray-700 dark:text-gray-300">Confidence:</span>
          <div className="mt-2">
            <ProgressBar
              completed={confidencePercentage}
              bgColor={
                confidencePercentage >= 70
                  ? "#10B981"
                  : confidencePercentage >= 50
                  ? "#F59E0B"
                  : "#EF4444"
              }
              height="10px"
              width="100%"
              labelAlignment="center"
              labelColor="#fff"
              labelSize="12px"
            />
            <span className="text-xs text-gray-600 dark:text-gray-400 mt-1 block">
              {confidencePercentage}%
            </span>
          </div>
        </li>
        <li>
          <span className="font-medium text-gray-700 dark:text-gray-300">Fallback Used:</span>{" "}
          <span>{result.fallback_used ? "Yes" : "No"}</span>
        </li>
        {result.error && (
          <li className="text-red-600 dark:text-red-400">
            <span className="font-medium">Error:</span> {result.error}
          </li>
        )}
      </ul>
    </div>
  );
}

export default ClassificationResultCard;
