import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';

export default function MedicalAgentUI() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [result, loading]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: query }),
      });

      if (!response.ok) throw new Error('Failed to fetch from the Medical API.');

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const isHallucinationBlocked = result?.answer?.includes("I don't know");

  return (
    <div className="w-screen min-h-screen bg-slate-50 text-slate-800 font-sans flex flex-col items-center py-8 px-4 box-border">
      
      {/* 1. Rigid Container with independent grid layout mapping */}
      <div className="w-full max-w-3xl h-[750px] bg-white rounded-3xl shadow-[0_10px_40px_rgba(0,0,0,0.04)] border border-slate-200/80 grid grid-rows-[auto_1fr_auto] overflow-hidden">
        
        {/* HEADER BLOCK */}
        <div className="p-5 border-b border-slate-100 bg-white text-center">
          <h1 className="text-xl font-black text-slate-800 tracking-tight m-0 p-0">Clinical Research Agent</h1>
          <p className="text-xs text-slate-400 font-semibold mt-1 p-0 block">Strict-constraint retrieval engine</p>
        </div>

        {/* INTERMEDIATE DISPLAY VIEWPORT */}
        <div className="p-6 overflow-y-auto bg-slate-50/40 flex flex-col space-y-6 min-h-0">
          
          {/* Empty State Layout */}
          {!result && !loading && !error && (
            <div className="m-auto text-center max-w-sm">
              <p className="text-sm text-slate-400 font-medium leading-relaxed">
                Enter a clinical query below to search verified medical journal databases.
              </p>
            </div>
          )}

          {/* Loading Viewport */}
          {loading && (
            <div className="m-auto flex flex-col items-center justify-center text-blue-600">
              <svg className="animate-spin h-9 w-9 mb-3 text-blue-500" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <circle cx="12" cy="12" r="10" strokeWidth="3" stroke="currentColor" strokeOpacity="0.2" />
                <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
              </svg>
              <span className="font-bold text-xs tracking-wider text-slate-400 uppercase">Searching literature...</span>
            </div>
          )}

          {/* Connection Error Frame */}
          {error && (
            <div className="m-auto bg-red-50 text-red-700 p-4 rounded-xl border border-red-100 max-w-md text-left">
              <p className="font-bold text-sm mb-0.5">Connection Error</p>
              <p className="text-xs opacity-90">{error}</p>
            </div>
          )}

          {/* STRICT DIRECTIONAL FLOW WRAPPERS */}
          {result && !loading && (
            <>
              {/* User Dialogue Stream (Forced Right Anchor) */}
              <div className="w-full flex justify-end items-center m-0 p-0 clear-both">
                <div className="bg-slate-800 text-white px-5 py-3 rounded-2xl rounded-tr-sm max-w-[80%] shadow-sm text-left block">
                  <p className="font-medium text-[14px] leading-relaxed m-0">{result.question}</p>
                </div>
              </div>

              {/* System Analysis Summary (Forced Left Anchor) */}
              <div className="w-full flex justify-start items-center m-0 p-0 clear-both">
                <div className={`w-full max-w-[90%] px-6 py-5 rounded-2xl rounded-tl-sm shadow-sm border text-left block ${isHallucinationBlocked ? 'bg-amber-50/40 border-amber-200' : 'bg-white border-slate-200'}`}>
                  
                  {isHallucinationBlocked && (
                     <div className="inline-block mb-3 text-amber-700 font-bold text-[10px] tracking-widest uppercase bg-amber-100/60 py-1 px-2..5 rounded">
                       ⚠️ Potential Hallucination Blocked
                     </div>
                  )}

                  {/* Markdown Content Output Interface */}
                  <div className="prose prose-slate max-w-none prose-p:leading-relaxed prose-p:text-slate-700 prose-p:text-[14.5px] text-left break-words">
                    <ReactMarkdown>{result.answer}</ReactMarkdown>
                  </div>
                </div>
              </div>
            </>
          )}
          
          <div ref={scrollRef} className="clear-both h-1" />
        </div>

        {/* INPUT COMMAND INTERFACE */}
        <div className="p-4 bg-white border-t border-slate-100">
          <form onSubmit={handleSubmit} className="relative w-full block m-0 p-0">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask a clinical question..."
              className="w-full pl-5 pr-14 py-3.5 bg-slate-50 border border-slate-200 rounded-full focus:outline-none focus:bg-white focus:ring-4 focus:ring-blue-50 focus:border-blue-400 transition-all duration-200 text-slate-700 placeholder-slate-400 text-[14.5px] font-medium box-border block"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="absolute right-2 top-1.5 bottom-1.5 aspect-square bg-blue-600 text-white rounded-full flex items-center justify-center hover:bg-blue-700 disabled:bg-slate-100 disabled:text-slate-300 shadow-sm transition-all m-0 border-0 cursor-pointer"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 translate-x-[0.5px]" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 1.414L10.586 9H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </form>
        </div>

      </div>
    </div>
  );
}