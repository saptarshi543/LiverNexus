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
      const endpoint = isTabular ? 'http://127.0.0.1:8000/analyze/tabular' : 'http://127.0.0.1:8000/analyze/image';

      let body: BodyInit | null = null;
      let headers: HeadersInit = {};

      if (isTabular) {
        const text = await file.text();

        try {
          // Try JSON first
          body = JSON.stringify(JSON.parse(text));
          headers = { 'Content-Type': 'application/json' };
        } catch (e) {
          // If JSON fails, try CSV
          try {
            // Split by newline and remove empty lines
            const lines = text.split(/\r?\n/).filter(line => line.trim() !== '');
            if (lines.length < 2) throw new Error("CSV file must have at least a header row and a data row");

            const headers_csv = lines[0].split(',').map(h => h.trim());

            const dataObj: any = {};

            // DETECT FORMAT: Vertical (Parameter, Value) vs Horizontal (ALT, AST, ...)
            if (headers_csv[0].toLowerCase() === 'parameter' && headers_csv[1].toLowerCase() === 'value') {
              // Vertical Format
              for (let i = 1; i < lines.length; i++) {
                const parts = lines[i].split(',');
                if (parts.length >= 2) {
                  const key = parts[0].trim();
                  const val = parts[1].trim();
                  if (!isNaN(Number(val))) {
                    dataObj[key] = Number(val);
                  }
                }
              }
            } else {
              // Horizontal Format (Fallback)
              const values = lines[1].split(',').map(v => v.trim());

              if (headers_csv.length !== values.length) {
                throw new Error(`Column mismatch: Header has ${headers_csv.length} cols, Data has ${values.length}`);
              }

              headers_csv.forEach((h: string, i: number) => {
                const val = values[i];
                // Frontend Validation Relaxed: Allow non-numeric values (IDs, Dates)
                // Backend agent will filter for numeric features.
                if (!isNaN(Number(val)) && val.trim() !== '') {
                  dataObj[h] = Number(val);
                } else {
                  // Pass strings as is
                  dataObj[h] = val;
                }
              });
            }

            body = JSON.stringify(dataObj);
            headers = { 'Content-Type': 'application/json' };
          } catch (csvError: any) {
            throw new Error(csvError.message || "Invalid format. Please upload valid JSON or CSV.");
          }
        }
      } else {
        const formData = new FormData();
        formData.append('file', file);
        body = formData;
      }

      if (!body) throw new Error("Failed to prepare request body.");

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: headers,
        body: body,
      });

      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`);
      }

      const data = await response.json();
      setProcessingStep(`Delegating to ${data.type || 'Specialist'} Agent...`);
      await new Promise(r => setTimeout(r, 1000));

      setResult(data);
    } catch (error: any) {
      console.error(error);
      setResult({ error: error.message || "Failed to connect to AI Agents." });
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
