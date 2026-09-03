"use client";

import { useState, useEffect, useRef } from "react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { uploadDocument, getDocuments, deleteDocument, getDocumentStatus } from "@/lib/api";
import { KnowledgeDocument } from "@/types";

export default function KnowledgeBasePage() {
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgressState, setUploadProgressState] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchDocs = async () => {
    try {
      const res = await getDocuments();
      if (res.success) {
        setDocuments(res.documents);
      }
    } catch {
      // Supabase or backend may be starting
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
    // Poll every 4 seconds if any document is currently processing
    const interval = setInterval(() => {
      setDocuments((prevDocs) => {
        const hasProcessing = prevDocs.some((d) => d.status === "processing");
        if (hasProcessing) {
          fetchDocs();
        }
        return prevDocs;
      });
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleFileSelect = async (file: File) => {
    const ext = file.name.split(".").pop()?.toLowerCase() || "";
    if (!["pdf", "docx", "txt", "md", "markdown"].includes(ext)) {
      setUploadError(`Unsupported format .${ext}. Supported: PDF, DOCX, TXT, MD.`);
      return;
    }

    setUploadError(null);
    setIsUploading(true);
    setUploadProgressState("Uploading document to VentureOS...");

    try {
      const res = await uploadDocument(file);
      if (res.success) {
        setUploadProgressState("Document uploaded! Extracting text & generating vector embeddings...");
        await fetchDocs();

        // Check status for a few seconds to provide live feedback
        let attempts = 0;
        const statusPoll = setInterval(async () => {
          attempts++;
          try {
            const statusRes = await getDocumentStatus(res.id);
            if (statusRes.status === "completed") {
              setUploadProgressState("Completed! Knowledge chunks and pgvector embeddings ready.");
              clearInterval(statusPoll);
              setIsUploading(false);
              fetchDocs();
            } else if (statusRes.status === "failed") {
              setUploadError(statusRes.error_message || "Document processing failed.");
              clearInterval(statusPoll);
              setIsUploading(false);
              fetchDocs();
            }
          } catch {
            // ignore poll error
          }
          if (attempts > 12) {
            clearInterval(statusPoll);
            setIsUploading(false);
            fetchDocs();
          }
        }, 2000);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to upload document.";
      setUploadError(msg);
      setIsUploading(false);
      setUploadProgressState(null);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleDelete = async (docId: string) => {
    if (!confirm("Are you sure you want to delete this document and all its vector embeddings?")) return;
    try {
      await deleteDocument(docId);
      setDocuments((prev) => prev.filter((d) => d.id !== docId));
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Failed to delete document.");
    }
  };

  const formatFileSize = (bytes?: number | null) => {
    if (!bytes) return "0 B";
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="min-h-screen bg-vo-black text-vo-white flex flex-col">
      <Navbar />

      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 lg:py-24 w-full">
        {/* Page Header */}
        <div className="mb-12 border-b border-vo-border pb-8">
          <div className="flex items-center gap-2 mb-3">
            <span className="w-2 h-2 rounded-full bg-vo-red" />
            <p className="text-vo-red text-xs font-black tracking-widest uppercase">
              RAG &amp; DOCUMENT INTELLIGENCE · PHASE 5
            </p>
          </div>
          <h1 className="text-4xl sm:text-5xl font-black leading-none tracking-tight text-vo-white uppercase mb-3">
            KNOWLEDGE BASE.
          </h1>
          <p className="text-vo-muted text-base max-w-2xl">
            Give VentureOS context about your startup. Upload pitch decks, business plans, market research, or technical specs.
            AI agents retrieve grounded facts and cite sources during analysis.
          </p>
        </div>

        <div className="grid lg:grid-cols-12 gap-10 items-start">
          {/* Left Column — Upload Box */}
          <div className="lg:col-span-5 space-y-6">
            <div className="border border-vo-border bg-vo-dark p-6 sm:p-8">
              <p className="text-vo-white text-xs font-black tracking-widest uppercase mb-4">
                ADD FOUNDER DOCUMENT
              </p>

              {/* Drag & Drop Area */}
              <div
                onDragOver={(e) => {
                  e.preventDefault();
                  setIsDragOver(true);
                }}
                onDragLeave={() => setIsDragOver(false)}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`border-2 border-dashed p-8 text-center cursor-pointer transition-colors duration-200 flex flex-col items-center justify-center min-h-[220px] ${
                  isDragOver
                    ? "border-vo-red bg-vo-black"
                    : "border-vo-border hover:border-vo-red bg-vo-black"
                }`}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.docx,.txt,.md"
                  onChange={(e) => {
                    if (e.target.files && e.target.files[0]) {
                      handleFileSelect(e.target.files[0]);
                    }
                  }}
                  className="hidden"
                />

                <div className="w-12 h-12 mb-4 rounded-full border border-vo-border flex items-center justify-center text-vo-red font-black text-xl">
                  ↑
                </div>

                <p className="text-vo-white text-sm font-bold uppercase tracking-wider mb-1">
                  DRAG &amp; DROP OR CLICK TO BROWSE
                </p>
                <p className="text-vo-muted text-xs">
                  Supported formats: PDF, DOCX, TXT, MD (Max 25 MB)
                </p>
              </div>

              {/* Status Feedback */}
              {isUploading && (
                <div className="mt-4 p-3 border border-vo-border bg-vo-black text-xs space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-vo-red animate-ping" />
                    <span className="text-vo-white font-bold uppercase tracking-wider">
                      PROCESSING PIPELINE
                    </span>
                  </div>
                  <p className="text-vo-muted">{uploadProgressState}</p>
                </div>
              )}

              {uploadError && (
                <div className="mt-4 p-3 border border-vo-red bg-vo-black text-vo-red text-xs">
                  {uploadError}
                </div>
              )}
            </div>

            {/* Architecture Explainer Card */}
            <div className="border border-vo-border bg-vo-dark p-6">
              <p className="text-vo-white text-xs font-black tracking-widest uppercase mb-3">
                HOW DOCUMENT RAG WORKS
              </p>
              <div className="space-y-2.5 text-xs text-vo-muted">
                <p>
                  <strong className="text-vo-white">1. Extraction:</strong> Cleans and normalises text across pages and paragraphs.
                </p>
                <p>
                  <strong className="text-vo-white">2. Chunking:</strong> Divides content into 600-token semantic chunks with 100-token overlap.
                </p>
                <p>
                  <strong className="text-vo-white">3. Embeddings:</strong> Generates 768-dimensional vectors with Google Gen AI.
                </p>
                <p>
                  <strong className="text-vo-white">4. pgvector Search:</strong> Performs cosine similarity matching and feeds top relevant evidence to the CEO Agent.
                </p>
              </div>
            </div>
          </div>

          {/* Right Column — Document List */}
          <div className="lg:col-span-7">
            <div className="border border-vo-border bg-vo-dark p-6 sm:p-8">
              <div className="flex items-center justify-between mb-6 pb-4 border-b border-vo-border">
                <div>
                  <p className="text-vo-white text-xs font-black tracking-widest uppercase">
                    DOCUMENTS IN REPOSITORY
                  </p>
                  <p className="text-vo-muted text-xs mt-0.5">
                    {documents.length} {documents.length === 1 ? "document" : "documents"} loaded
                  </p>
                </div>
                <button
                  onClick={fetchDocs}
                  className="text-vo-muted hover:text-vo-red text-xs font-mono uppercase transition-colors"
                >
                  REFRESH
                </button>
              </div>

              {isLoading ? (
                <p className="text-vo-muted text-xs">Loading repository...</p>
              ) : documents.length === 0 ? (
                <div className="text-center py-12 border border-vo-border bg-vo-black p-6">
                  <p className="text-vo-white text-sm font-bold uppercase mb-1">
                    NO DOCUMENTS UPLOADED YET
                  </p>
                  <p className="text-vo-muted text-xs">
                    Upload your pitch deck or business plan on the left to activate RAG grounding.
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {documents.map((doc) => (
                    <div
                      key={doc.id}
                      className="border border-vo-border bg-vo-black p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                    >
                      <div className="space-y-1 min-w-0 flex-1">
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] font-mono font-bold uppercase px-1.5 py-0.5 bg-vo-dark border border-vo-border text-vo-red">
                            {doc.file_type.toUpperCase()}
                          </span>
                          <span
                            className={`text-[9px] font-mono uppercase px-1.5 py-0.5 border ${
                              doc.status === "completed"
                                ? "border-green-800 text-green-400"
                                : doc.status === "failed"
                                ? "border-vo-red text-vo-red"
                                : "border-yellow-700 text-yellow-400"
                            }`}
                          >
                            {doc.status}
                          </span>
                          {doc.total_chunks > 0 && (
                            <span className="text-[10px] font-mono text-vo-muted">
                              {doc.total_chunks} chunks
                            </span>
                          )}
                        </div>
                        <p className="text-vo-white text-sm font-bold truncate">
                          {doc.filename}
                        </p>
                        <p className="text-vo-muted text-[11px]">
                          {formatFileSize(doc.file_size)}
                          {doc.created_at && (
                            <> · {new Date(doc.created_at).toLocaleDateString()}</>
                          )}
                        </p>
                        {doc.error_message && (
                          <p className="text-vo-red text-[11px] mt-1">{doc.error_message}</p>
                        )}
                      </div>

                      <div>
                        <button
                          onClick={() => handleDelete(doc.id)}
                          className="border border-vo-border hover:border-vo-red text-vo-muted hover:text-vo-red text-xs px-3 py-1.5 uppercase font-bold transition-colors"
                        >
                          DELETE
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
