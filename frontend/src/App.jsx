import React, { useState } from "react";
import axios from "axios";
import ClassificationResultCard from "./components/ClassificationResultCard";

function App() {
  const [input, setInput] = useState({
    sender: "",
    subject: "",
    content: "",
    product: "Discovery",
    channel: "email"
  });

  const [result, setResult] = useState(null);

  const handleClassify = async () => {
    try {
      const res = await axios.post("http://localhost:8000/api/webhook/incoming", input);
      setResult(res.data);
    } catch (err) {
      alert("Classification failed. Check console.");
      console.error(err);
    }
  };

  return (
    <div className="p-6 max-w-2xl mx-auto font-sans">
      <h1 className="text-2xl font-bold mb-4">Triage Agent</h1>

      <textarea
        className="w-full p-2 border mb-2"
        rows="4"
        placeholder="Paste message content here"
        onChange={(e) => setInput({ ...input, content: e.target.value })}
      />

      <input
        type="text"
        className="w-full p-2 border mb-2"
        placeholder="Subject"
        onChange={(e) => setInput({ ...input, subject: e.target.value })}
      />

      <input
        type="text"
        className="w-full p-2 border mb-2"
        placeholder="Sender email"
        onChange={(e) => setInput({ ...input, sender: e.target.value })}
      />

      <select
        className="w-full p-2 border mb-4"
        onChange={(e) => setInput({ ...input, product: e.target.value })}
      >
        <option value="Discovery">Discovery</option>
        <option value="Hauler">Hauler</option>
        <option value="Pioneer">Pioneer</option>
      </select>

      <button
        className="bg-blue-600 text-white px-4 py-2 rounded"
        onClick={handleClassify}
      >
        Classify
      </button>

      {result && <ClassificationResultCard result={result} />}
    </div>
  );
}

export default App;
