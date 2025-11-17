'use client';

import { useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface SearchResult {
  chunk_id: string;
  content: string;
  score: number;
  rerank_score?: number;
  entities: Array<{ name: string; type: string }>;
  relationships: Array<{ source: string; target: string; type: string }>;
}

interface AnswerResult {
  answer: string;
  context: string;
  key_entities: string[];
  sources: SearchResult[];
}

export default function Home() {
  const [query, setQuery] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [workspaceId, setWorkspaceId] = useState("default_workspace");
  const [collectionId, setCollectionId] = useState("");
  const [collectionName, setCollectionName] = useState("");
  
  const [answerResult, setAnswerResult] = useState<AnswerResult | null>(null);
  const [searchResults, setSearchResults] = useState<SearchResult[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file || !collectionId) {
      alert("Please select a file and enter collection info");
      return;
    }

    setUploadStatus("Uploading...");
    const formData = new FormData();
    formData.append("file", file);
    formData.append("workspace_id", workspaceId);
    formData.append("collection_id", collectionId);
    formData.append("collection_name", collectionName || collectionId);

    try {
      const response = await fetch(`${API_URL}/ingest/upload`, {
        method: "POST",
        body: formData,
      });
      
      if (!response.ok) throw new Error("Upload failed");
      
      const data = await response.json();
      setUploadStatus(`Success! Created ${data.chunks} chunks, ${data.entities} entities`);
      setFile(null);
    } catch (error) {
      setUploadStatus("Upload failed");
      console.error(error);
    }
  };

  const handleSearch = async () => {
    if (!query.trim() || !collectionId) {
      alert("Please enter a query and collection ID");
      return;
    }

    setLoading(true);
    setAnswerResult(null);
    setSearchResults(null);

    try {
      // Call both endpoints in parallel
      const [answerRes, searchRes] = await Promise.all([
        fetch(
          `${API_URL}/rag/answer?query=${encodeURIComponent(query)}&workspace_id=${workspaceId}&collection_id=${collectionId}`
        ),
        fetch(
          `${API_URL}/rag/search?query=${encodeURIComponent(query)}&workspace_id=${workspaceId}&collection_id=${collectionId}&limit=10`
        ),
      ]);

      if (answerRes.ok) {
        const answerData = await answerRes.json();
        setAnswerResult(answerData);
      }

      if (searchRes.ok) {
        const searchData = await searchRes.json();
        setSearchResults(searchData.results);
      }
    } catch (error) {
      console.error("Search error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      {/* Header */}
      <header className="border-b border-white/[0.08]">
        <div className="max-w-7xl mx-auto px-8 py-5 flex items-center justify-between">
          <h1 className="text-xl font-semibold">Graph RAG</h1>
          <div className="flex gap-4 text-sm">
            <input
              type="text"
              placeholder="Workspace ID"
              value={workspaceId}
              onChange={(e) => setWorkspaceId(e.target.value)}
              className="px-3 py-1 bg-[#141414] border border-white/[0.08] rounded"
            />
            <input
              type="text"
              placeholder="Collection ID"
              value={collectionId}
              onChange={(e) => setCollectionId(e.target.value)}
              className="px-3 py-1 bg-[#141414] border border-white/[0.08] rounded"
            />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-8 py-12">
        {/* Hero Section */}
        <div className="mb-12">
          <h2 className="text-4xl font-medium mb-3 leading-tight">
            Knowledge Graph RAG System
          </h2>
          <p className="text-lg text-[#b4b4b4]">
            Upload documents and ask questions powered by graph relationships and semantic search
          </p>
        </div>

        {/* Upload Section */}
        <div className="mb-8 p-6 bg-[#0f0f0f] border border-white/[0.08] rounded-lg">
          <h3 className="text-lg font-medium mb-4">Upload Document</h3>
          <div className="grid grid-cols-2 gap-3 mb-3">
            <input
              type="text"
              placeholder="Collection Name (optional)"
              value={collectionName}
              onChange={(e) => setCollectionName(e.target.value)}
              className="px-4 h-10 bg-[#141414] border border-white/[0.08] rounded-lg"
            />
          </div>
          <div className="flex gap-3">
            <label className="flex-1">
              <input
                type="file"
                onChange={handleFileChange}
                className="hidden"
                accept=".txt"
              />
              <div className="h-12 px-4 bg-[#141414] border border-white/[0.08] rounded-lg flex items-center justify-between cursor-pointer hover:border-white/[0.16] transition-colors">
                <span className="text-sm text-[#b4b4b4]">
                  {file ? file.name : "Choose a file..."}
                </span>
              </div>
            </label>
            <button
              onClick={handleUpload}
              disabled={!file || !collectionId}
              className="px-6 h-12 bg-white text-black rounded-lg font-medium hover:bg-[#f5f5f5] disabled:bg-[#1a1a1a] disabled:text-[#666] disabled:cursor-not-allowed transition-colors"
            >
              Upload
            </button>
          </div>
          {uploadStatus && (
            <p className="text-sm text-[#b4b4b4] mt-2">{uploadStatus}</p>
          )}
        </div>

        {/* Search Section */}
        <div className="mb-8">
          <label className="block text-sm font-medium text-[#b4b4b4] mb-3">Ask a Question</label>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="What would you like to know about your documents?"
            className="w-full h-24 px-4 py-3 bg-[#141414] border border-white/[0.08] rounded-lg resize-none focus:outline-none focus:border-white/[0.16] transition-colors text-white placeholder:text-[#666]"
          />
          <button
            onClick={handleSearch}
            disabled={!query.trim() || !collectionId || loading}
            className="mt-3 w-full h-12 bg-white text-black rounded-lg font-medium hover:bg-[#f5f5f5] disabled:bg-[#1a1a1a] disabled:text-[#666] disabled:cursor-not-allowed transition-colors"
          >
            {loading ? "Searching..." : "Search"}
          </button>
        </div>

        {/* Results Section - Side by Side */}
        {(answerResult || searchResults) && (
          <div className="grid grid-cols-2 gap-6 mt-12">
            {/* Answer Section (Left) */}
            <div className="border border-white/[0.08] rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <span className="text-green-400">●</span> Answer
              </h3>
              {answerResult ? (
                <div className="space-y-4">
                  <div className="text-[#e0e0e0] leading-relaxed whitespace-pre-wrap">
                    {answerResult.answer}
                  </div>
                  {answerResult.key_entities.length > 0 && (
                    <div>
                      <p className="text-xs text-[#888] mb-2">Key Entities:</p>
                      <div className="flex flex-wrap gap-2">
                        {answerResult.key_entities.map((entity, i) => (
                          <span
                            key={i}
                            className="px-2 py-1 text-xs bg-[#1a1a1a] border border-white/[0.08] rounded"
                          >
                            {entity}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-[#666]">Loading answer...</p>
              )}
            </div>

            {/* Search Results Section (Right) */}
            <div className="border border-white/[0.08] rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <span className="text-blue-400">●</span> Source Documents
              </h3>
              {searchResults ? (
                <div className="space-y-4 max-h-[600px] overflow-y-auto">
                  {searchResults.map((result, i) => (
                    <div
                      key={i}
                      className="p-4 bg-[#0f0f0f] border border-white/[0.06] rounded-lg"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <span className="text-xs text-[#888]">Source {i + 1}</span>
                        <span className="text-xs text-[#888]">
                          Score: {(result.rerank_score || result.score).toFixed(3)}
                        </span>
                      </div>
                      <p className="text-sm text-[#d0d0d0] mb-3 leading-relaxed">
                        {result.content.substring(0, 200)}...
                      </p>
                      {result.entities.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {result.entities.slice(0, 5).map((entity, j) => (
                            entity.name && (
                              <span
                                key={j}
                                className="px-2 py-0.5 text-xs bg-[#1a1a1a] text-[#999] rounded"
                              >
                                {entity.name}
                              </span>
                            )
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-[#666]">Loading sources...</p>
              )}
            </div>
          </div>
        )}

        {/* Empty State */}
        {!answerResult && !searchResults && !loading && (
          <div className="mt-12 border border-white/[0.08] rounded-lg p-12">
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[#141414] border border-white/[0.08] flex items-center justify-center">
                <svg className="w-8 h-8 text-[#666]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <p className="text-[#666] text-lg">Upload a document and ask a question to get started</p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
