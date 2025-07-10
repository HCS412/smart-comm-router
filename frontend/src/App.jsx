import React, { useState } from "react";
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
  const { register, handleSubmit, formState: { errors }, reset } = useForm({
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

  return (
    <div className="p-6 max-w-2xl mx-auto font-sans">
      <h1 className="text-2xl font-bold mb-4">Triage Agent</h1>
      
      {/* Manual Message Input Form */}
      <form onSubmit={handleSubmit(onTriageSubmit)} className="space-y-4">
        <h2 className="text-lg font-semibold mb-2">Manual Message Input</h2>
        <div>
          <label className="block text-sm font-medium mb-1">Message Content</label>
          <textarea
            {...register("content", {
              required: "Message content is required",
              minLength: { value: 10, message: "Content must be at least 10 characters" }
            })}
            className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-600"
            rows="4"
            placeholder="Paste message content here"
          />
          {errors.content && <ErrorMessage message={errors.content.message} />}
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Sender Email</label>
          <input
            {...register("sender", {
              required: "Sender email is required",
              pattern: { value: /^\S+@\S+$/i, message: "Invalid email format" }
            })}
            type="text"
            className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-600"
            placeholder="Sender email"
          />
          {errors.sender && <ErrorMessage message={errors.sender.message} />}
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Subject</label>
          <input
            {...register("subject")}
            type="text"
            className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-600"
            placeholder="Subject (optional)"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Product</label>
          <select
            {...register("product")}
            className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-600"
          >
            <option value="Discovery">Discovery</option>
            <option value="Hauler">Hauler</option>
            <option value="Pioneer">Pioneer</option>
          </select>
        </div>

        <div className="flex space-x-4">
          <button
            type="submit"
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:bg-blue-300 flex items-center"
            disabled={loading}
          >
            {loading ? <LoadingSpinner /> : "Classify & Draft"}
          </button>
          <button
            type="button"
            onClick={handleReset}
            className="bg-gray-300 text-black px-4 py-2 rounded hover:bg-gray-400"
          >
            Reset
          </button>
        </div>
      </form>

      {/* Ingestion Form */}
      <form onSubmit={handleSubmit(onIngestSubmit)} className="mt-6 space-y-4">
        <h2 className="text-lg font-semibold mb-2">Ingest from Source</h2>
        <div>
          <label className="block text-sm font-medium mb-1">Source</label>
          <select
            {...register("source", { required: "Source is required" })}
            className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-600"
          >
            <option value="gmail">Gmail</option>
            <option value="phone">Phone</option>
          </select>
          {errors.source && <ErrorMessage message={errors.source.message} />}
        </div>

        <button
          type="submit"
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:bg-green-300 flex items-center"
          disabled={loading}
        >
          {loading ? <LoadingSpinner /> : "Ingest & Triage"}
        </button>
      </form>

      {error && <ErrorMessage message={error} />}
      {result && (
        <div className="mt-6 space-y-6">
          <ClassificationResultCard result={result.classification} />
          <DraftResponseCard draft={result.draft.reply_draft} />
        </div>
      )}
    </div>
  );
}

export default App;
