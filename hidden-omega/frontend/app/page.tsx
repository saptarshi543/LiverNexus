"use client";

import React, { useState } from 'react';
import UploadArea from '@/components/UploadArea';
import ResultCard from '@/components/ResultCard';

export default function Home() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [processingStep, setProcessingStep] = useState<string>("");

  const handleUpload = async (file: File) => {
    setIsProcessing(true);
    setResult(null);
    setProcessingStep("Uploading to Secure Server...");

    try {
      const formData = new FormData();
      formData.append('file', file);

      // Simulate network delay for effect
      await new Promise(r => setTimeout(r, 800));

      setProcessingStep("Router Agent Analysis: Identifying Modality...");
      await new Promise(r => setTimeout(r, 1200));

      const isTabular = file.name.endsWith('.json') || file.name.endsWith('.csv');
      const endpoint = isTabular ? 'http://localhost:8000/analyze/tabular' : 'http://localhost:8000/analyze/image';

      let body;
      let headers = {};

      if (isTabular) {
        // For tabular, read text and send as JSON
        const text = await file.text();
        // Basic parsing for JSON, if CSV would need more logic. 
        // For demo assuming JSON for now or robust CSV handling backend. 
        // Router expects dict for 'tabular'.
        try {
          body = JSON.stringify(JSON.parse(text));
          headers = { 'Content-Type': 'application/json' };
        } catch (e) {
          // Fallback for CSV or error
          throw new Error("Invalid JSON format for tabular data");
        }
      } else {
        const formData = new FormData();
        formData.append('file', file);
        body = formData;
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: headers,
        body: body,
      });

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const data = await response.json();
      setProcessingStep(`Delegating to ${data.type || 'Specialist'} Agent...`);
      await new Promise(r => setTimeout(r, 1000));

      setResult(data);
    } catch (error) {
      console.error(error);
      setResult({ error: "Failed to connect to AI Agents. Ensure Backend is running." });
    } finally {
      setIsProcessing(false);
      setProcessingStep("");
    }
  };

  return (
    <main className="min-h-screen p-8 md:p-12 lg:p-24 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-[#0f172a] to-black">
      <div className="max-w-5xl mx-auto flex flex-col items-center">

        {/* Header */}
        <div className="text-center mb-16 animate-fade-in space-y-4">
          <div className="inline-block px-4 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm font-medium mb-4">
            New Generation Diagnostics
          </div>
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-white mb-6">
            Liver<span className="text-primary">AI</span>
          </h1>
          <p className="text-lg text-slate-400 max-w-2xl mx-auto leading-relaxed">
            Advanced autonomous agents for multi-modal liver disease diagnostics.
            Detecting MASLD, Fibrosis, and HCC with histopathological precision.
          </p>
        </div>

        {/* Main Interface */}
        <div className="w-full max-w-3xl glass-panel p-8 rounded-3xl relative overflow-hidden">
          {/* Decorative Glow */}
          <div className="absolute -top-20 -right-20 w-64 h-64 bg-blue-500/20 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute -bottom-20 -left-20 w-64 h-64 bg-cyan-500/20 rounded-full blur-3xl pointer-events-none" />

          <div className="relative z-10">
            <UploadArea onUpload={handleUpload} isProcessing={isProcessing} />
          </div>
        </div>

        {/* Dynamic Status */}
        {isProcessing && (
          <div className="mt-8 flex items-center gap-3 text-slate-300 animate-pulse">
            <div className="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
            <span className="font-mono">{processingStep}</span>
          </div>
        )}

        {/* Results */}
        <div className="w-full flex justify-center pb-20">
          <ResultCard data={result} />
        </div>

      </div>
    </main>
  );
}
