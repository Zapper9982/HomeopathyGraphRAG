"use client";

interface Props {
  text: string;
}

export function ExplanationCard({ text }: Props) {
  return (
    <div className="glass-card p-5">
      <div className="flex items-center gap-2 mb-3">
        <span className="section-label">Clinical Explanation</span>
        <span className="tag bg-purple-50 text-purple-600 text-[10px]">AI Generated</span>
      </div>
      <div className="prose prose-sm max-w-none text-foreground/80 leading-relaxed whitespace-pre-wrap text-[14px]">
        {text}
      </div>
    </div>
  );
}
