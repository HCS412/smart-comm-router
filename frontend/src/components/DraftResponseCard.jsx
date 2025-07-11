import React from "react";
import { motion } from "framer-motion";

function DraftResponseCard({ draft }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="mt-6 p-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700"
      role="region"
      aria-label="Draft Response"
    >
      <h2 className="text-2xl font-semibold mb-4 text-dsq-gray-700 dark:text-gray-200">Draft Response</h2>
      <div
        className="text-sm text-dsq-gray-700 dark:text-gray-300 whitespace-pre-wrap bg-gray-50 dark:bg-gray-900 p-4 rounded"
        dangerouslySetInnerHTML={{ __html: draft.replace(/\n/g, "<br>") }}
      />
    </motion.div>
  );
}

export default DraftResponseCard;
