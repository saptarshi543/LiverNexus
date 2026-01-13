"use client";

import React from 'react';

interface ResultCardProps {
    data: any;
}

export default function ResultCard({ data }: ResultCardProps) {
    if (!data) return null;

    const isError = data.error;

    return (
        <div className="glass-panel p-6 rounded-2xl w-full max-w-2xl animate-fade-in mt-8">
            {isError ? (
                <div className="text-danger flex items-center gap-3">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span className="font-semibold">Analysis Failed: {data.error}</span>
                </div>
            ) : (
                <div>
                    <div className="flex justify-between items-start mb-6">
                        <div>
                            <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-teal-400 to-blue-500">
                                AI Analysis Result
                            </h2>
                            <p className="text-slate-400 text-sm mt-1 uppercase tracking-wider font-semibold">
                                Modality: {data.type || "Tabular Data"}
                            </p>
                        </div>

                        <div className="flex flex-col items-end">
                            <span className="text-sm text-slate-400 mb-1">Confidence</span>
                            <div className="text-3xl font-bold text-white">
                                {(data.confidence * 100).toFixed(1)}%
                            </div>
                        </div>
                    </div>

                    <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700/50">
                        <h3 className="text-lg font-semibold text-slate-200 mb-2">Primary Diagnosis</h3>
                        <p className={`text-xl ${data.diagnosis === "Healthy" || data.diagnosis === "Normal" ? "text-success" : "text-warning"}`}>
                            {data.diagnosis}
                        </p>
                    </div>

                    {data.recommendations && data.recommendations.length > 0 && (
                        <div className="bg-blue-500/10 rounded-xl p-6 border border-blue-500/20 mb-6">
                            <h3 className="text-lg font-semibold text-blue-400 mb-3 flex items-center gap-2">
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                                </svg>
                                Recommended Next Steps
                            </h3>
                            <ul className="space-y-2">
                                {data.recommendations.map((rec: string, idx: number) => (
                                    <li key={idx} className="flex items-start gap-2 text-slate-300">
                                        <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-blue-400 flex-shrink-0" />
                                        <span>{rec}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {data.details && (
                        <div className="mt-6">
                            <h4 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-3">Detailed Metrics</h4>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {Object.entries(data.details).map(([key, value]) => (
                                    <div key={key} className="bg-slate-800/50 p-3 rounded-lg flex justify-between items-center">
                                        <span className="text-slate-300 text-sm">{key}</span>
                                        <span className="text-slate-100 font-mono font-medium">
                                            {typeof value === 'number' ? (value < 1 ? (value * 100).toFixed(1) + '%' : value) : value as string}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    <div className="mt-6 pt-6 border-t border-slate-700/50 flex items-center justify-between text-xs text-slate-500">
                        <span>Model: {data.type === "Histopathology Analysis" ? "U-Net" : "ResNet/Ensemble"}</span>
                        <span>ID: {Math.random().toString(36).substr(2, 9).toUpperCase()}</span>
                    </div>
                </div>
            )}
        </div>
    );
}
