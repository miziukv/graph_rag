'use client';

import { useState } from "react";

export default function Home() {
  const [query, setQuery] = useState("");
  const [file, setFile] = useState<File | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      {/* Header */}
      <header className="border-b border-white/[0.08]">
        <div className="max-w-6xl mx-auto px-8 py-5 flex items-center justify-between">
          <h1 className="text-xl font-semibold">Deep Search</h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-8 py-16">
        {/* Hero Section */}
        <div className="mb-16">
          <h2 className="text-5xl font-medium mb-4 leading-tight">
            Knowledge graph-powered<br />search engine
          </h2>
          <p className="text-lg text-[#b4b4b4]">
            Upload your documents and discover insights through AI-powered semantic search.
          </p>
        </div>

        {/* Upload Section */}
        <div className="mb-8">
          <label className="block text-sm font-medium text-[#b4b4b4] mb-3">Upload document</label>
          <div className="flex gap-3">
            <label className="flex-1">
              <input
                type="file"
                onChange={handleFileChange}
                className="hidden"
                accept=".txt,.pdf,.md,.json"
              />
              <div className="h-12 px-4 bg-[#141414] border border-white/[0.08] rounded-lg flex items-center justify-between cursor-pointer hover:border-white/[0.16] transition-colors">
                <span className="text-sm text-[#b4b4b4]">
                  {file ? file.name : "Choose a file..."}
                </span>
                <svg className="w-5 h-5 text-[#666]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                </svg>
              </div>
            </label>
            <button
              disabled={!file}
              className="px-6 h-12 bg-white text-black rounded-lg font-medium hover:bg-[#f5f5f5] disabled:bg-[#1a1a1a] disabled:text-[#666] disabled:cursor-not-allowed transition-colors"
            >
              Upload
            </button>
          </div>
          <p className="text-xs text-[#666] mt-2">Supports TXT, PDF, MD, JSON files</p>
        </div>

        {/* Search Section */}
        <div className="mb-8">
          <label className="block text-sm font-medium text-[#b4b4b4] mb-3">Search query</label>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask a question about your documents..."
            className="w-full h-32 px-4 py-3 bg-[#141414] border border-white/[0.08] rounded-lg resize-none focus:outline-none focus:border-white/[0.16] transition-colors text-white placeholder:text-[#666]"
          />
          <button
            disabled={!query.trim()}
            className="mt-3 w-full h-12 bg-white text-black rounded-lg font-medium hover:bg-[#f5f5f5] disabled:bg-[#1a1a1a] disabled:text-[#666] disabled:cursor-not-allowed transition-colors"
          >
            Search
          </button>
        </div>

        {/* Results Section */}
        <div className="mt-12">
          <div className="border border-white/[0.08] rounded-lg p-8">
            <div className="text-center py-12">
              <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-[#141414] border border-white/[0.08] flex items-center justify-center">
                <svg className="w-6 h-6 text-[#666]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <p className="text-[#666]">No results yet</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
