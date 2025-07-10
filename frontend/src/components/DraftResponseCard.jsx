import React from "react";

function DraftResponseCard({ draft }) {
  return (
    <div
      className="mt-6 p-6 border rounded-lg shadow-lg bg-white"
      role="region"
      aria-label="Draft Response"
    >
      <h2 className="text-xl font-semibold mb-4 text-gray-800">Draft Response</h2>
      <p className="text-sm text-gray-600 whitespace-pre-wrap">{draft}</p>
    </div>
  );
}

export default DraftResponseCard;
