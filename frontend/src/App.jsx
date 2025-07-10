import React, { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import axios from "axios";
import axiosRetry from "axios-retry";
import { motion, AnimatePresence } from "framer-motion";
import { FaSun, FaMoon } from "react-icons/fa";
import ClassificationResultCard from "./components/ClassificationResultCard";
import DraftResponseCard from "./components/DraftResponseCard";
import LoadingSpinner from "./components/LoadingSpinner";
import ErrorMessage from "./components/ErrorMessage";

// Configure axios retries
axiosRetry(axios, { retries: 3, retryDelay: axiosRetry.exponentialDelay });

// Use environment variable for API base URL
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://localhost:8000";

function App() {
  const { register, handleSubmit, formState: { errors }, watch, reset } = useForm({
    defaultValues: {
      sender: "",
      subject: "",
      content: "",
      product: "Discovery",
      channel: "email",
      source: "gmail",
      metadata: {}
    }
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    setDarkMode(prefersDark);
  }, []);

  const toggleDarkMode = () => setDarkMode(!darkMode);

  const onTriageSubmit = async (data) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await axios.post(`${API_BASE_URL}/api/v1/messages/triage`, {
        sender: data.sender,
        content: data.content,
        metadata: { subject: data.subject, product: data.product, channel: data.channel }
      });
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Failed to process message.");
    } finally {
      setLoading(false);
    }
  };

  const onIngestSubmit = async (data) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await axios.post(`${API_BASE_URL}/api/v1/messages/ingest`, {
        source: data.source,
        mock: true
      });
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Failed to ingest message.");
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    reset();
    setResult(null);
    setError(null);
  };

  const content = watch("content");
  const isContentValid = content && content.length >= 10;

  return (
    <div
      className={`min-h-screen ${
        darkMode
          ? "bg-gray-900 text-white"
          : "bg-gradient-to-br from-dsq-blue-50 to-white"
      } transition-colors duration-300 font-sans`}
    >
      <header className="p-6 flex justify-between items-center bg-dsq-blue-600 text-white shadow-md">
        <div className="flex items-center space-x-3">
          <svg
            className="h-8 w-8"
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" strokeWidth="2"/>
            <path d="M8 12 L12 16 L16 12" stroke="currentColor" strokeWidth="2" fill="none"/>
          </svg>
          <h1 className="text-3xl font-bold">DSQ Triage Agent</h1>
        </div>
        <button
          onClick={toggleDarkMode}
          className="px-4 py-2 bg-white text-dsq-blue-600 rounded-full hover:bg-gray-200 dark:bg-gray-700 dark:text-white dark:hover:bg-gray-600 transition-all duration-200 flex items-center space-x-2"
          aria-label={`Switch to ${darkMode ? "light" : "dark"} mode`}
        >
          {darkMode ? <FaSun /> : <FaMoon />}
          <span>{darkMode ? "Light" : "Dark"}</span>
        </button>
      </header>

      <main className="p-8 max-w-6xl mx-auto">
        <AnimatePresence>
          <motion.section
            key="manual-input"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.5 }}
            className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg mb-8 border border-gray-200 dark:border-gray-700"
          >
            <h2 className="text-2xl font-semibold mb-6 text-dsq-gray-700 dark:text-gray-200">Manual Message Input</h2>
            <form onSubmit={handleSubmit(onTriageSubmit)} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium mb-2 text-dsq-gray-700 dark:text-gray-300">Sender Email</label>
                <input
                  {...register("sender", {
                    required: "Sender email is required",
                    pattern: { value: /^\S+@\S+$/i, message: "Invalid email format" }
                  })}
                  type="text"
                  className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-dsq-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  placeholder="user@example.com"
                  aria-describedby="sender-error"
                />
                {errors.sender && <ErrorMessage id="sender-error" message={errors.sender.message} />}
              </div>

              <div>
                <label className="block text-sm font-medium mb-2 text-dsq-gray-700 dark:text-gray-300">Subject</label>
                <input
                  {...register("subject")}
                  type="text"
                  className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-dsq-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  placeholder="e.g., Invoice Issue"
                />
              </div>

              <div className="col-span-full">
                <label className="block text-sm font-medium mb-2 text-dsq-gray-700 dark:text-gray-300">Message Content</label>
                <textarea
                  {...register("content", {
                    required: "Message content is required",
                    minLength: { value: 10, message: "Content must be at least 10 characters" }
                  })}
                  className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-dsq-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  rows="5"
                  placeholder="Enter your message here..."
                  aria-describedby="content-error"
                />
                {errors.content && <ErrorMessage id="content-error" message={errors.content.message} />}
                {!errors.content && content && (
                  <p className="text-xs text-green-600 dark:text-green-400 mt-2">Length: {content.length} characters</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium mb-2 text-dsq-gray-700 dark:text-gray-300">Product</label>
                <select
                  {...register("product")}
                  className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-dsq-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                >
                  <option value="Discovery">Discovery</option>
                  <option value="Pioneer">Pioneer</option>
                  <option value="Hauler">Hauler</option>
                </select>
              </div>

              <div className="col-span-full flex justify-end space-x-4">
                <button
                  type="submit"
                  className="bg-dsq-blue-600 text-white px-6 py-3 rounded-lg hover:bg-dsq-blue-700 focus:ring-2 focus:ring-dsq-blue-500 disabled:bg-blue-300 flex items-center space-x-2 transition-all duration-200"
                  disabled={loading || !isContentValid}
                  aria-label="Classify and draft message"
                >
                  {loading ? <LoadingSpinner /> : <span>Classify & Draft</span>}
                </button>
                <button
                  type="button"
                  onClick={handleReset}
                  className="bg-gray-300 text-dsq-gray-700 px-6 py-3 rounded-lg hover:bg-gray-400 dark:bg-gray-600 dark:text-gray-200 dark:hover:bg-gray-500 transition-all duration-200"
                  aria-label="Reset form"
                >
                  Reset
                </button>
              </div>
            </form>
          </motion.section>
        </AnimatePresence>

        <AnimatePresence>
          <motion.section
            key="ingest-input"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.5 }}
            className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700"
          >
            <h2 className="text-2xl font-semibold mb-6 text-dsq-gray-700 dark:text-gray-200">Ingest from Source</h2>
            <form onSubmit={handleSubmit(onIngestSubmit)} className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium mb-2 text-dsq-gray-700 dark:text-gray-300">Source</label>
                <select
                  {...register("source", { required: "Source is required" })}
                  className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-dsq-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  aria-describedby="source-error"
                >
                  <option value="gmail">Gmail</option>
                  <option value="phone">Phone</option>
                </select>
                {errors.source && <ErrorMessage id="source-error" message={errors.source.message} />}
              </div>

              <div className="flex justify-end">
                <button
                  type="submit"
                  className="bg-dsq-blue-600 text-white px-6 py-3 rounded-lg hover:bg-dsq-blue-700 focus:ring-2 focus:ring-dsq-blue-500 disabled:bg-blue-300 flex items-center space-x-2 transition-all duration-200"
                  disabled={loading}
                  aria-label="Ingest and triage message"
                >
                  {loading ? <LoadingSpinner /> : <span>Ingest & Triage</span>}
                </button>
              </div>
            </form>
          </motion.section>
        </AnimatePresence>

        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <ErrorMessage message={error} />
            </motion.div>
          )}
          {result && (
            <motion.section
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5 }}
              className="mt-8 space-y-6"
            >
              <ClassificationResultCard result={result.classification} />
              <DraftResponseCard draft={result.draft.reply_draft} />
            </motion.section>
          )}
        </AnimatePresence>
      </main>

      <footer className="p-6 bg-dsq-blue-600 text-white text-center">
        <p className="text-sm">© 2025 DSQ Technology, LLC. All rights reserved.</p>
        <p className="text-xs mt-1">Powered by Discovery, Pioneer, and Hauler solutions</p>
      </footer>
    </div>
  );
}

export default App;
