"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { ConsultResult } from "@/lib/types";

// Dynamic import for ForceGraph2D (canvas-based, SSR unsafe)
import dynamic from "next/dynamic";
const ForceGraph2D = dynamic(() => import("react-force-graph-2d"), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center h-[500px] text-muted">
      Loading graph…
    </div>
  ),
});

/* ── Color palette ──────────────────────────────── */
const COLORS = {
  complaint: "#c026d3", // fuchsia
  symptom: "#6366f1", // indigo
  rubric: "#f59e0b", // amber
  remedy: "#10b981", // emerald
  edge_grade1: "#94a3b8aa", // muted
  edge_grade2: "#f59e0baa", // amber
  edge_grade3: "#10b981cc", // green
  edge_symptom: "#6366f155", // indigo
};

const NODE_LABELS: Record<string, string> = {
  complaint: "Complaint",
  symptom: "Symptom",
  rubric: "Rubric",
  remedy: "Remedy",
};

/* ── Types for the force graph ──────────────────── */
interface GNode {
  id: string;
  label: string;
  type: "complaint" | "symptom" | "rubric" | "remedy";
  score?: number; // only for remedy nodes
  x?: number;
  y?: number;
}

interface GLink {
  source: string;
  target: string;
  grade?: number; // 1-3 for rubric→remedy
  type: "complaint_to_symptom" | "symptom_to_rubric" | "rubric_to_remedy";
}

/* ── Build graph from consult result ────────────── */
function buildGraph(result: ConsultResult): { nodes: GNode[]; links: GLink[] } {
  const nodeMap = new Map<string, GNode>();
  const linkSet = new Set<string>();
  const links: GLink[] = [];

  // 1) Complaint node
  nodeMap.set("__complaint__", {
    id: "__complaint__",
    label: "Patient Complaint",
    type: "complaint",
  });

  // 2) Symptom nodes
  for (const sid of result.symptom_ids) {
    const nid = `sym_${sid}`;
    if (!nodeMap.has(nid)) {
      nodeMap.set(nid, {
        id: nid,
        label: sid.replace(/_/g, " "),
        type: "symptom",
      });
    }
    const lk = `__complaint__->${nid}`;
    if (!linkSet.has(lk)) {
      linkSet.add(lk);
      links.push({
        source: "__complaint__",
        target: nid,
        type: "complaint_to_symptom",
      });
    }
  }

  // 3) From ranked remedies, extract rubric + remedy nodes
  const topRemedies = result.ranked_remedies.slice(0, 10); // keep top 10
  for (const rem of topRemedies) {
    const remId = `rem_${rem.remedy}`;
    if (!nodeMap.has(remId)) {
      nodeMap.set(remId, {
        id: remId,
        label: rem.remedy,
        type: "remedy",
        score: rem.score,
      });
    }

    for (const d of rem.details) {
      // Rubric node
      const rubricText = d.rubric.length > 40 ? d.rubric.slice(0, 37) + "…" : d.rubric;
      const rubricId = `rub_${d.rubric.slice(0, 50)}`;
      if (!nodeMap.has(rubricId)) {
        nodeMap.set(rubricId, {
          id: rubricId,
          label: rubricText,
          type: "rubric",
        });
      }

      // symptom → rubric
      const symId = `sym_${d.symptom_id}`;
      const lk1 = `${symId}->${rubricId}`;
      if (!linkSet.has(lk1) && nodeMap.has(symId)) {
        linkSet.add(lk1);
        links.push({ source: symId, target: rubricId, type: "symptom_to_rubric" });
      }

      // rubric → remedy
      const lk2 = `${rubricId}->${remId}`;
      if (!linkSet.has(lk2)) {
        linkSet.add(lk2);
        links.push({
          source: rubricId,
          target: remId,
          grade: d.grade,
          type: "rubric_to_remedy",
        });
      }
    }
  }

  return { nodes: Array.from(nodeMap.values()), links };
}

/* ── Component ──────────────────────────────────── */
export function ReasoningGraph({ result }: { result: ConsultResult }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 500 });
  const [hoveredNode, setHoveredNode] = useState<GNode | null>(null);

  // Measure container
  useEffect(() => {
    if (!containerRef.current) return;
    const obs = new ResizeObserver((entries) => {
      for (const e of entries) {
        setDimensions({
          width: e.contentRect.width,
          height: Math.max(500, e.contentRect.height),
        });
      }
    });
    obs.observe(containerRef.current);
    return () => obs.disconnect();
  }, []);

  const graph = useMemo(() => buildGraph(result), [result]);

  const paintNode = useCallback(
    (node: GNode, ctx: CanvasRenderingContext2D, globalScale: number) => {
      const isHovered = hoveredNode?.id === node.id;
      const r =
        node.type === "complaint"
          ? 8
          : node.type === "remedy"
            ? 4 + (node.score || 0) * 8
            : node.type === "symptom"
              ? 5
              : 3;

      const color = COLORS[node.type];

      // Glow for hovered
      if (isHovered) {
        ctx.shadowColor = color;
        ctx.shadowBlur = 15;
      }

      ctx.beginPath();
      ctx.arc(node.x || 0, node.y || 0, r, 0, 2 * Math.PI);
      ctx.fillStyle = color;
      ctx.fill();
      ctx.shadowBlur = 0;

      // Label
      if (globalScale > 0.8 || isHovered || node.type === "remedy" || node.type === "complaint") {
        const fontSize = Math.max(10 / globalScale, 2);
        ctx.font = `${isHovered ? "bold " : ""}${fontSize}px sans-serif`;
        ctx.textAlign = "center";
        ctx.fillStyle = "#334155";
        ctx.fillText(
          node.label,
          node.x || 0,
          (node.y || 0) + r + fontSize + 1
        );
      }
    },
    [hoveredNode]
  );

  const linkColor = useCallback((link: GLink) => {
    if (link.type === "complaint_to_symptom") return COLORS.edge_symptom;
    if (link.type === "symptom_to_rubric") return COLORS.edge_symptom;
    if (link.grade === 3) return COLORS.edge_grade3;
    if (link.grade === 2) return COLORS.edge_grade2;
    return COLORS.edge_grade1;
  }, []);

  const linkWidth = useCallback((link: GLink) => {
    if (link.grade === 3) return 2.5;
    if (link.grade === 2) return 1.5;
    return 0.8;
  }, []);

  if (graph.nodes.length === 0) return null;

  return (
    <div className="glass-card overflow-hidden">
      <div className="px-5 pt-4 pb-2 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-foreground">Reasoning Graph</h3>
          <p className="text-xs text-muted mt-0.5">
            How the system traversed the knowledge graph to reach its conclusions
          </p>
        </div>
        <div className="flex gap-3 text-[10px]">
          {(["complaint", "symptom", "rubric", "remedy"] as const).map((t) => (
            <span key={t} className="flex items-center gap-1">
              <span
                className="inline-block w-2.5 h-2.5 rounded-full"
                style={{ backgroundColor: COLORS[t] }}
              />
              {NODE_LABELS[t]}
            </span>
          ))}
        </div>
      </div>

      {/* Hover info */}
      {hoveredNode && (
        <div className="px-5 py-1.5 text-xs bg-card-hover border-t border-border">
          <span style={{ color: COLORS[hoveredNode.type] }} className="font-semibold">
            [{NODE_LABELS[hoveredNode.type]}]
          </span>{" "}
          {hoveredNode.label}
          {hoveredNode.score !== undefined && (
            <span className="text-muted ml-2">Score: {hoveredNode.score.toFixed(4)}</span>
          )}
        </div>
      )}

      <div ref={containerRef} className="w-full" style={{ height: 500 }}>
        <ForceGraph2D
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          graphData={graph as any}
          width={dimensions.width}
          height={500}
          backgroundColor="#fafbfd"
          nodeCanvasObject={paintNode as never}
          nodePointerAreaPaint={(node, color, ctx) => {
            const n = node as GNode;
            const r = n.type === "complaint" ? 10 : n.type === "remedy" ? 8 : 6;
            ctx.beginPath();
            ctx.arc(n.x || 0, n.y || 0, r, 0, 2 * Math.PI);
            ctx.fillStyle = color;
            ctx.fill();
          }}
          linkColor={linkColor as never}
          linkWidth={linkWidth as never}
          linkDirectionalArrowLength={3}
          linkDirectionalArrowRelPos={0.9}
          linkCurvature={0.15}
          onNodeHover={(node) => setHoveredNode((node as GNode) || null)}
          cooldownTicks={80}
          d3AlphaDecay={0.03}
          d3VelocityDecay={0.3}
          enableZoomInteraction={true}
          enablePanInteraction={true}
        />
      </div>

      {/* Stats footer */}
      <div className="px-5 py-2.5 text-[10px] text-muted border-t border-border flex gap-4">
        <span>{graph.nodes.length} nodes</span>
        <span>{graph.links.length} edges</span>
        <span>{graph.nodes.filter((n) => n.type === "remedy").length} remedies shown</span>
        <span className="ml-auto">Drag to rearrange · Scroll to zoom</span>
      </div>
    </div>
  );
}
