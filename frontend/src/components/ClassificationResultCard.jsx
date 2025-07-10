import React from "react";
import ProgressBar from "react-progressbar";

function ClassificationResultCard({ result }) {
  const confidencePercentage = Math.round(result.confidence * 100);

  return (
    <div
      className="mt-6 p-6 border rounded-lg shadow-lg bg-white"
      role="region"
      aria-label="Classification Result"
    >
      <h2 className="text-xl font-semibold mb-4 text-gray-800">Classification Result</h2>
      <ul className="space-y-2 text-sm">
        <li>
          <strong className="font-medium">Category:</strong> {result.category}
        </li>
        <li>
          <strong className="font-medium">Priority:</strong> {result.priority}
        </li>
        <li>
          <strong className="font-medium">Intent:</strong> {result.intent}
        </li>
        <li>
          <strong className="font-medium">Queue:</strong> {result.recommended_queue}
        </li>
        <li>
          <strong className="font-medium">Confidence:</strong>
          <div className="mt-1">
            <ProgressBar
              completed={confidencePercentage}
              bgColor={confidencePercentage >= 70 ? "#10B981" : confidencePercentage >= 50 ? "#F59E0B" : "#EF4444"}
              height="8px"
              width="100%"
              labelAlignment="center"
              labelColor="#fff"
              labelSize="12px"
            />
            <span className="text-xs text-gray-600">{confidencePercentage}%</span>
          </div>
        </li>
        <li>
          <strong className="font-medium">Fallback Used:</strong> {result.fallback_used ? "Yes" : "No"}
        </li>
        {result.error && (
          <li className="text-red-600">
            <strong className="font-medium">Error:</strong> {result.error}
          </li>
        )}
      </ul>
    </div>
  );
}

export default ClassificationResultCard;
