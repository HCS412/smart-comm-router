import React from "react";

function ClassificationResultCard({ result }) {
  return (
    <div className="mt-6 p-4 border rounded shadow bg-white">
      <h2 className="text-xl font-semibold mb-2">Classification Result</h2>
      <ul className="space-y-1">
        <li><strong>Category:</strong> {result.category}</li>
        <li><strong>Priority:</strong> {result.priority}</li>
        <li><strong>Intent:</strong> {result.intent}</li>
        <li><strong>Queue:</strong> {result.recommended_queue}</li>
        <li><strong>Confidence:</strong> {Math.round(result.confidence * 100)}%</li>
        <li><strong>Fallback Used:</strong> {result.fallback_used ? "Yes" : "No"}</li>
        {result.error && <li><strong>Error:</strong> {result.error}</li>}
      </ul>
    </div>
  );
}

export default ClassificationResultCard;
