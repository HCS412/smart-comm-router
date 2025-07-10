import React, { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import axios from "axios";
import axiosRetry from "axios-retry";
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

  // Toggle dark mode
  useEffect(() => {
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    setDarkMode(prefersDark);
  }, []);

  const toggleDarkMode = () => setDarkMode(!darkMode);

  // Handle manual message submission via /triage endpoint
  const onTriageSubmit = async (data) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await axios.post(`${API_BASE_URL}/api/v1/messages/triage`, {
        sender: data.sender,
        content: data.content,
        metadata: {
          subject: data.subject,
          product: data.product,
          channel: data.channel
        }
      });
      setResult(res.data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.message ||
        "Failed to process message. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  // Handle ingestion submission via /ingest endpoint
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
      setError(
        err.response?.data?.detail ||
        err.message ||
        "Failed to ingest message. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    reset();
    setResult(null);
    setError(null);
  };

  // Watch form fields for real-time validation
  const content = watch("content");
  const isContentValid = content && content.length >= 10;

  return (
    <div
      className={`min-h-screen ${
        darkMode ? "bg-gray-900 text-white" : "bg-gradient-to-br from-white to-gray-100 text-gray-900"
      } transition-colors duration-300`}
    >
      <header className="p-6 flex justify-between items-center border-b">
        <h1 className="text-3xl font-bold">Triage Agent</h1>
        <button
          onClick={toggleDarkMode}
          className="px-4 py-2 bg-gray-200 text-gray-800 rounded-full hover:bg-gray-300 dark:bg-gray-700 dark:text-white dark:hover:bg-gray-600"
          aria-label={`Switch to ${darkMode ? "light" : "dark"} mode`}
        >
          {darkMode ? "☀️" : "🌙"}
        </button>
      </header>

      <main className="p-6 max-w-4xl mx-auto">
        {/* Manual Message Input Section */}
        <section className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg mb-6">
          <h2 className="text-2xl font-semibold mb-4">Manual Message Input</h2>
          <form onSubmit={handleSubmit(onTriageSubmit)} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Sender Email</label>
              <input
                {...register("sender", {
                  required: "Sender email is required",
                  pattern: { value: /^\S+@\S+$/i, message: "Invalid email format" }
                })}
                type="text"
                className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700"
                placeholder="user@example.com"
                aria-describedby="sender-error"
              />
              {errors.sender && <ErrorMessage id="sender-error" message={errors.sender.message} />}
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Subject</label>
              <input
                {...register("subject")}
                type="text"
                className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700"
                placeholder="e.g., Invoice Issue"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium mb-1">Message Content</label>
              <textarea
                {...register("content", {
                  required: "Message content is required",
                  minLength: { value: 10, message: "Content must be at least 10 characters" }
                })}
                className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700"
                rows="4"
                placeholder="Enter your message here..."
                aria-describedby="content-error"
              />
              {errors.content && <ErrorMessage id="content-error" message={errors.content.message} />}
              {!errors.content && content && (
                <p className="text-xs text-green-600 mt-1">Content length: {content.length} characters</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Product</label>
              <select
                {...register("product")}
                className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700"
              >
                <option value="Discovery">Discovery</option>
                <option value="Hauler">Hauler</option>
                <option value="Pioneer">Pioneer</option>
              </select>
            </div>

            <div className="md:col-span-2 flex space-x-4">
              <button
                type="submit"
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:bg-blue-300 flex items-center"
                disabled={loading || !isContentValid}
                aria-label="Classify and draft message"
              >
                {loading ? <LoadingSpinner /> : "Classify & Draft"}
              </button>
              <button
                type="button"
                onClick={handleReset}
                className="bg-gray-300 text-gray-800 px-4 py-2 rounded hover:bg-gray-400 dark:bg-gray-600 dark:text-white dark:hover:bg-gray-500"
                aria-label="Reset form"
              >
                Reset
              </button>
            </div>
          </form>
        </section>

        {/* Ingestion Section */}
        <section className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
          <h2 className="text-2xl font-semibold mb-4">Ingest from Source</h2>
          <form onSubmit={handleSubmit(onIngestSubmit)} className="grid grid-cols-1 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Source</label>
              <select
                {...register("source", { required: "Source is required" })}
                className="w-full p-2 border rounded focus:ring-2 focus:ring-green-500 dark:border-gray-600 dark:bg-gray-700"
                aria-describedby="source-error"
              >
                <option value="gmail">Gmail</option>
                <option value="phone">Phone</option>
              </select>
              {errors.source && <ErrorMessage id="source-error" message={errors.source.message} />}
            </div>

            <button
              type="submit"
              className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:bg-green-300 flex items-center"
              disabled={loading}
              aria-label="Ingest and triage message"
            >
              {loading ? <LoadingSpinner /> : "Ingest & Triage"}
            </button>
          </form>
        </section>

        {error && <ErrorMessage message={error} />}
        {result && (
          <section className="mt-6 space-y-6">
            <ClassificationResultCard result={result.classification} />
            <DraftResponseCard draft={result.draft.reply_draft} />
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
