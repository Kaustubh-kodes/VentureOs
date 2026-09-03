"use client";

import { useState } from "react";
import {
  StartupFormData,
  FormErrors,
  Industry,
  Budget,
  Timeline,
  CEOAnalysis,
  KnowledgeSource,
} from "@/types";
import { analyseCEO, startMultiAgentAnalysis } from "@/lib/api";
import CEOAnalysisResult from "./CEOAnalysisResult";

const INDUSTRIES: Industry[] = [
  "EdTech",
  "FinTech",
  "HealthTech",
  "SaaS",
  "AI",
  "E-commerce",
  "Other",
];

const BUDGETS: Budget[] = ["Under $10,000", "$10,000-$50,000", "$50,000+"];

const TIMELINES: Timeline[] = [
  "1-3 months",
  "3-6 months",
  "6-12 months",
  "12+ months",
];

const EMPTY_FORM: StartupFormData = {
  startupIdea: "",
  targetAudience: "",
  industry: "",
  budget: "Under $10,000",
  timeline: "1-3 months",
  additionalContext: "",
};

function validate(data: StartupFormData): FormErrors {
  const errors: FormErrors = {};

  const ideaTrimmed = data.startupIdea.trim();
  if (!ideaTrimmed) {
    errors.startupIdea = "Startup idea is required.";
  } else if (ideaTrimmed.length < 10) {
    errors.startupIdea = "Startup idea must be at least 10 characters.";
  } else if (ideaTrimmed.length > 2000) {
    errors.startupIdea = "Startup idea must not exceed 2000 characters.";
  }

  const audienceTrimmed = data.targetAudience.trim();
  if (!audienceTrimmed) {
    errors.targetAudience = "Target audience is required.";
  } else if (audienceTrimmed.length < 2) {
    errors.targetAudience = "Target audience must be at least 2 characters.";
  }

  if (!data.industry) {
    errors.industry = "Please select an industry.";
  }

  return errors;
}

interface FieldProps {
  label: string;
  required?: boolean;
  error?: string;
  children: React.ReactNode;
}

function Field({ label, required, error, children }: FieldProps) {
  return (
    <div className="flex flex-col gap-1.5">
      <label className="text-vo-white text-xs font-bold tracking-widest uppercase">
        {label}
        {required && (
          <span className="text-vo-red ml-1" aria-label="required">
            *
          </span>
        )}
      </label>
      {children}
      {error && (
        <p className="text-vo-red text-xs font-medium" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}

const inputBase =
  "bg-vo-dark border border-vo-border text-vo-white placeholder-vo-muted text-sm px-4 py-3 focus:outline-none focus:border-vo-red transition-colors duration-200 w-full";
const inputError = "border-vo-red";

interface StartupFormProps {
  onMultiAgentLaunch?: (sessionId: string) => void;
  onLaunchMultiAgent?: (sessionId: string) => void;
  onSuccess?: () => void;
}

export default function StartupForm({
  onMultiAgentLaunch,
  onLaunchMultiAgent,
  onSuccess,
}: StartupFormProps = {}) {
  const [form, setForm] = useState<StartupFormData>(EMPTY_FORM);
  const [errors, setErrors] = useState<FormErrors>({});
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<CEOAnalysis | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sourcesUsed, setSourcesUsed] = useState<KnowledgeSource[]>([]);

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    if (errors[name as keyof FormErrors]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const newErrors = validate(form);
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);

    const reqData = {
      startup_idea: form.startupIdea.trim(),
      target_audience: form.targetAudience.trim(),
      industry: form.industry,
      budget: form.budget || "Under $10,000",
      timeline: form.timeline || "1-3 months",
      notes: form.additionalContext.trim() || undefined,
    };

    try {
      const launcher = onLaunchMultiAgent || onMultiAgentLaunch;
      if (launcher) {
        const response = await startMultiAgentAnalysis(reqData);
        if (response.success && response.session_id) {
          launcher(response.session_id);
          onSuccess?.();
          return;
        }
      }

      const response = await analyseCEO(reqData);

      if (response.success && response.data) {
        setAnalysisResult(response.data);
        if (response.session_id) {
          setSessionId(response.session_id);
        }
        if (response.sources_used) {
          setSourcesUsed(response.sources_used);
        }
      } else {
        throw new Error("Invalid response format received from server.");
      }
    } catch (err: unknown) {
      const msg =
        err instanceof Error
          ? err.message
          : "An unexpected error occurred while communicating with the AI service.";
      setErrorMessage(msg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setAnalysisResult(null);
    setSessionId(null);
    setSourcesUsed([]);
    setErrorMessage(null);
    setErrors({});
  };

  // If analysis completed, show professional strategy report
  if (analysisResult) {
    return (
      <CEOAnalysisResult
        analysis={analysisResult}
        sessionId={sessionId || undefined}
        sourcesUsed={sourcesUsed}
        onLaunchMultiAgent={sessionId && onMultiAgentLaunch ? () => onMultiAgentLaunch(sessionId) : undefined}
        onReset={handleReset}
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Loading overlay experience */}
      {isLoading && (
        <div
          className="border border-vo-border bg-vo-dark p-8 text-center space-y-4"
          role="status"
          aria-live="polite"
        >
          <div className="flex items-center justify-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-vo-red animate-pulse" />
            <span className="text-vo-red text-xs font-black tracking-widest uppercase">
              VENTUREOS STRATEGY ROOM
            </span>
          </div>
          <div>
            <h3 className="text-vo-white text-base sm:text-lg font-black tracking-wider uppercase mb-1">
              CEO &amp; STRATEGY AGENT
            </h3>
            <p className="text-vo-red text-xs sm:text-sm font-bold tracking-widest uppercase">
              ANALYSING YOUR STARTUP...
            </p>
          </div>
          <p className="text-vo-muted text-xs max-w-sm mx-auto leading-relaxed">
            Evaluating business model, customer problem definition, revenue streams, and 90-day priorities via Gemini.
          </p>
        </div>
      )}

      {/* Error state */}
      {errorMessage && (
        <div
          className="border-l-2 border-vo-red border-y border-r border-vo-border bg-vo-dark p-5"
          role="alert"
        >
          <div className="flex items-center gap-2 mb-1.5">
            <span className="w-2 h-2 rounded-full bg-vo-red" />
            <p className="text-vo-red text-xs font-black tracking-widest uppercase">
              ANALYSIS FAILED
            </p>
          </div>
          <p className="text-vo-white text-sm leading-relaxed mb-3">
            {errorMessage}
          </p>
          <button
            type="button"
            onClick={() => setErrorMessage(null)}
            className="text-vo-muted text-xs uppercase tracking-wider hover:text-vo-white underline"
          >
            Dismiss and edit inputs
          </button>
        </div>
      )}

      {/* Analysis input form */}
      <form onSubmit={handleSubmit} noValidate className="flex flex-col gap-6">
        {/* Startup Idea */}
        <Field label="Startup Idea" required error={errors.startupIdea}>
          <textarea
            name="startupIdea"
            value={form.startupIdea}
            onChange={handleChange}
            placeholder="Describe your startup idea (minimum 10 characters)..."
            rows={4}
            disabled={isLoading}
            className={`${inputBase} resize-none ${
              errors.startupIdea ? inputError : ""
            }`}
            aria-required="true"
            aria-invalid={!!errors.startupIdea}
          />
        </Field>

        {/* Target Audience */}
        <Field label="Target Audience" required error={errors.targetAudience}>
          <input
            type="text"
            name="targetAudience"
            value={form.targetAudience}
            onChange={handleChange}
            placeholder="e.g. College students and recent graduates"
            disabled={isLoading}
            className={`${inputBase} ${errors.targetAudience ? inputError : ""}`}
            aria-required="true"
            aria-invalid={!!errors.targetAudience}
          />
        </Field>

        {/* Industry */}
        <Field label="Industry" required error={errors.industry}>
          <select
            name="industry"
            value={form.industry}
            onChange={handleChange}
            disabled={isLoading}
            className={`${inputBase} ${
              errors.industry ? inputError : ""
            } appearance-none cursor-pointer`}
            aria-required="true"
            aria-invalid={!!errors.industry}
          >
            <option value="">Select industry...</option>
            {INDUSTRIES.map((ind) => (
              <option key={ind} value={ind}>
                {ind}
              </option>
            ))}
          </select>
        </Field>

        <div className="grid sm:grid-cols-2 gap-6">
          {/* Budget */}
          <Field label="Available Budget">
            <select
              name="budget"
              value={form.budget}
              onChange={handleChange}
              disabled={isLoading}
              className={`${inputBase} appearance-none cursor-pointer`}
            >
              {BUDGETS.map((b) => (
                <option key={b} value={b}>
                  {b}
                </option>
              ))}
            </select>
          </Field>

          {/* Timeline */}
          <Field label="Timeline">
            <select
              name="timeline"
              value={form.timeline}
              onChange={handleChange}
              disabled={isLoading}
              className={`${inputBase} appearance-none cursor-pointer`}
            >
              {TIMELINES.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </Field>
        </div>

        {/* Additional Context */}
        <Field label="Additional Context">
          <textarea
            name="additionalContext"
            value={form.additionalContext}
            onChange={handleChange}
            placeholder="Any specific market constraints, geography, or notes..."
            rows={3}
            disabled={isLoading}
            className={`${inputBase} resize-none`}
          />
        </Field>

        {/* Submit */}
        <button
          type="submit"
          disabled={isLoading}
          className="bg-vo-red text-white font-black px-8 py-4 text-sm tracking-widest uppercase hover:bg-vo-red-hover transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-vo-red w-full sm:w-auto"
          aria-label="Submit startup analysis to 7 AI Agents"
        >
          {isLoading ? "ORCHESTRATING 7 AGENTS..." : "LAUNCH 7-AGENT INTELLIGENCE PIPELINE →"}
        </button>
      </form>
    </div>
  );
}
