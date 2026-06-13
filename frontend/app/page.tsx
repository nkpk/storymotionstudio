"use client";
import { useState } from "react";

const API = "https://ideal-dollop-4g4q7qr95pr2qx56-8000.app.github.dev";

const STYLES = [
  { id: "horror", label: "Horror Cinematic", icon: "☠", color: "#ff2020", glow: "#ff202033" },
  { id: "anime", label: "Anime Recap", icon: "⚡", color: "#00d4ff", glow: "#00d4ff33" },
  { id: "documentary", label: "Documentary", icon: "🎞", color: "#f5c842", glow: "#f5c84233" },
  { id: "science", label: "Science Explainer", icon: "🔬", color: "#7cff6b", glow: "#7cff6b33" },
  { id: "luxury", label: "Luxury Storytelling", icon: "✦", color: "#e8c97e", glow: "#e8c97e33" },
  { id: "shorts", label: "Viral Shorts", icon: "▶", color: "#ff5c87", glow: "#ff5c8733" },
];

const INTENSITIES = ["Low Motion", "Medium Motion", "High Motion", "Cinematic"];
const ASPECT_RATIOS = [
  { id: "16:9", label: "16:9", sub: "YouTube Landscape", w: 48, h: 27 },
  { id: "9:16", label: "9:16", sub: "Shorts / Reels / TikTok", w: 27, h: 48 },
  { id: "1:1", label: "1:1", sub: "Instagram Post", w: 36, h: 36 },
];
const CAPTION_POSITIONS = ["top", "center", "bottom"];
const CAPTION_TYPES = [
  { id: "sentence", label: "Full Sentence", desc: "Show complete sentences" },
  { id: "word", label: "Word by Word", desc: "One word at a time" },
];

export default function Home() {
  const [step, setStep] = useState(1);
  const [mode, setMode] = useState<"upload" | "ai">("upload");
  const [aiTopic, setAiTopic] = useState("");
  const [aiJobId, setAiJobId] = useState("");
  const [aiStatus, setAiStatus] = useState("");
  const [aiLoading, setAiLoading] = useState(false);
  const [aiTitle, setAiTitle] = useState("");
  const [selectedStyle, setSelectedStyle] = useState("horror");
  const [selectedIntensity, setSelectedIntensity] = useState(2);
  const [selectedRatio, setSelectedRatio] = useState("16:9");
  const [captionPosition, setCaptionPosition] = useState("bottom");
  const [captionType, setCaptionType] = useState("sentence");
  const [images, setImages] = useState<File[]>([]);
  const [audio, setAudio] = useState<File | null>(null);
  const [music, setMusic] = useState<File | null>(null);
  const [jobId, setJobId] = useState("");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) setImages(Array.from(e.target.files));
  };
  const handleAudioUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) setAudio(e.target.files[0]);
  };
  const handleMusicUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) setMusic(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (images.length === 0) { alert("Please select images first"); return; }
    setLoading(true);
    setStatus("Uploading...");
    const formData = new FormData();
    images.forEach(img => formData.append("images", img));
    if (audio) formData.append("audio", audio);
    if (music) formData.append("music", music);
    try {
      const res = await fetch(`${API}/upload`, { method: "POST", body: formData });
      const data = await res.json();
      setJobId(data.job_id);
      setLoading(false);
      setStep(2);
    } catch {
      setStatus("Upload failed.");
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    if (!jobId) { alert("Please upload first"); return; }
    setLoading(true);
    setStatus("generating");
    setProgress(0);

    // Poll real progress
    const pollInterval = setInterval(async () => {
      try {
        const res = await fetch(`${API}/status/${jobId}`);
        const data = await res.json();
        if (data.progress) setProgress(data.progress);
        if (data.status === "done" || data.status === "error") {
          clearInterval(pollInterval);
          setStatus(data.status);
          setLoading(false);
        }
      } catch {}
    }, 1000);

    try {
      const style = STYLES.find(s => s.id === selectedStyle)?.label || "Horror Cinematic";
      const intensity = INTENSITIES[selectedIntensity];
      await fetch(
        `${API}/generate/${jobId}?style=${encodeURIComponent(style)}&intensity=${encodeURIComponent(intensity)}&aspect_ratio=${encodeURIComponent(selectedRatio)}&caption_position=${captionPosition}&caption_type=${captionType}`,
        { method: "POST" }
      );
    } catch {
      setStatus("error");
      setLoading(false);
    }
  };

  const card = (active: boolean, color = "#e8c97e") => ({
    border: `1px solid ${active ? color : "#ffffff11"}`,
    borderRadius: "12px",
    padding: "16px",
    cursor: "pointer",
    background: active ? color + "18" : "transparent",
    transition: "all 0.2s",
  });

  const handleAiGenerate = async () => {
    if (!aiTopic.trim()) { alert("Enter a topic"); return; }
    setAiLoading(true);
    setAiStatus("generating");
    try {
      const style = STYLES.find(s => s.id === selectedStyle)?.label || "Science Explainer";
      const res = await fetch(
        `${API}/ai/generate?topic=${encodeURIComponent(aiTopic)}&style=${encodeURIComponent(style)}&duration=60&aspect_ratio=${encodeURIComponent(selectedRatio)}`,
        { method: "POST" }
      );
      const data = await res.json();
      const jid = data.job_id;
      setAiJobId(jid);

      const poll = setInterval(async () => {
        try {
          const sres = await fetch(`${API}/status/${jid}`);
          const sdata = await sres.json();
          if (sdata.status === "done") {
            clearInterval(poll);
            setAiTitle(sdata.title || "Your Video");
            setAiStatus("done");
            setAiLoading(false);
          } else if (sdata.status === "error") {
            clearInterval(poll);
            setAiStatus("error");
            setAiLoading(false);
          }
        } catch {}
      }, 3000);
    } catch {
      setAiStatus("error");
      setAiLoading(false);
    }
  };
  
  return (
    <main style={{ minHeight: "100vh", background: "#090909", color: "#fff", fontFamily: "sans-serif" }}>

      {/* NAV */}
      <nav style={{ padding: "16px 24px", borderBottom: "1px solid #ffffff11", display: "flex", alignItems: "center", justifyContent: "space-between", background: "#09090988", backdropFilter: "blur(20px)", position: "sticky", top: 0, zIndex: 100, flexWrap: "wrap", gap: "10px" }}>
        <div style={{ color: "#e8c97e", fontSize: "18px", fontWeight: "bold" }}>▶ StoryMotion Studio</div>
        <div style={{ display: "flex", gap: "8px" }}>
          <button onClick={() => setMode("upload")} style={{
            background: mode === "upload" ? "#e8c97e" : "#ffffff11",
            color: mode === "upload" ? "#000" : "#ffffff66",
            border: "none", borderRadius: "8px", padding: "8px 16px",
            fontSize: "13px", fontWeight: "600", cursor: "pointer"
          }}>📁 Upload Mode</button>
          <button onClick={() => setMode("ai")} style={{
            background: mode === "ai" ? "#e8c97e" : "#ffffff11",
            color: mode === "ai" ? "#000" : "#ffffff66",
            border: "none", borderRadius: "8px", padding: "8px 16px",
            fontSize: "13px", fontWeight: "600", cursor: "pointer"
          }}>✦ AI Text-to-Video</button>
        </div>
        {mode === "upload" && (
        <div style={{ display: "flex", gap: "6px" }}>
          {[1, 2, 3, 4].map(n => (
            <div key={n} onClick={() => setStep(n)} style={{
              width: "30px", height: "30px", borderRadius: "50%",
              background: step === n ? "#e8c97e" : "#ffffff11",
              color: step === n ? "#000" : "#ffffff44",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: "12px", fontWeight: "bold", cursor: "pointer"
            }}>{n}</div>
          ))}
        </div>
        )}
      </nav>
 
      {mode === "ai" && (
        <div style={{ maxWidth: "560px", margin: "0 auto", padding: "40px 20px", textAlign: "center" }}>
          <h1 style={{ fontSize: "2rem", fontWeight: "900", marginBottom: "8px" }}>AI Text-to-Video</h1>
          <p style={{ color: "#ffffff55", marginBottom: "28px" }}>Just type a topic — AI writes the script, plans scenes, and generates the video</p>

          <textarea
            value={aiTopic}
            onChange={(e) => setAiTopic(e.target.value)}
            placeholder="e.g. Why do airplanes survive lightning?"
            style={{
              width: "100%", minHeight: "100px", background: "#0d0d0d",
              border: "1px solid #ffffff22", borderRadius: "12px",
              padding: "16px", color: "#fff", fontSize: "15px",
              marginBottom: "20px", fontFamily: "sans-serif", resize: "vertical"
            }}
          />

          {/* Style selector for AI mode */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "10px", marginBottom: "20px" }}>
            {STYLES.map(s => (
              <div key={s.id} onClick={() => setSelectedStyle(s.id)} style={{
                border: `1px solid ${selectedStyle === s.id ? s.color : "#ffffff11"}`,
                borderRadius: "10px", padding: "12px 8px", cursor: "pointer", textAlign: "center",
                background: selectedStyle === s.id ? s.glow : "transparent",
              }}>
                <div style={{ fontSize: "20px", marginBottom: "4px" }}>{s.icon}</div>
                <div style={{ fontSize: "10px", color: selectedStyle === s.id ? "#fff" : "#ffffff55" }}>{s.label}</div>
              </div>
            ))}
          </div>

          {/* Aspect ratio */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "10px", marginBottom: "28px" }}>
            {ASPECT_RATIOS.map(r => (
              <div key={r.id} onClick={() => setSelectedRatio(r.id)} style={{
                border: `1px solid ${selectedRatio === r.id ? "#e8c97e" : "#ffffff11"}`,
                borderRadius: "10px", padding: "10px", cursor: "pointer", textAlign: "center",
                background: selectedRatio === r.id ? "#e8c97e18" : "transparent",
              }}>
                <div style={{ fontSize: "13px", fontWeight: "700", color: selectedRatio === r.id ? "#e8c97e" : "#fff" }}>{r.label}</div>
                <div style={{ fontSize: "10px", color: "#ffffff44" }}>{r.sub}</div>
              </div>
            ))}
          </div>

          <div style={{ border: "1px solid #ffffff11", borderRadius: "16px", padding: "32px 20px", marginBottom: "20px" }}>
            {aiStatus === "done" ? (
              <>
                <div style={{ fontSize: "48px", marginBottom: "16px" }}>🎉</div>
                <div style={{ fontSize: "18px", color: "#e8c97e", marginBottom: "8px", fontWeight: "bold" }}>{aiTitle}</div>
                <div style={{ fontSize: "13px", color: "#ffffff44", marginBottom: "20px" }}>Video generated successfully</div>
                <button onClick={() => window.open(`${API}/download/${aiJobId}`)} style={{
                  background: "linear-gradient(135deg, #e8c97e, #c9973e)", border: "none",
                  borderRadius: "10px", padding: "14px 32px", color: "#000",
                  fontWeight: "700", fontSize: "15px", cursor: "pointer"
                }}>⬇ Download MP4</button>
              </>
            ) : aiStatus === "error" ? (
              <>
                <div style={{ fontSize: "48px", marginBottom: "16px" }}>❌</div>
                <div style={{ fontSize: "16px", color: "#ff4444" }}>Generation failed. Try again.</div>
              </>
            ) : aiLoading ? (
              <>
                <div style={{ fontSize: "16px", color: "#ffffff88", marginBottom: "12px" }}>
                  AI is writing your script and generating scenes...
                </div>
                <div style={{ fontSize: "12px", color: "#ffffff44" }}>This takes 30-60 seconds</div>
              </>
            ) : (
              <>
                <div style={{ fontSize: "40px", marginBottom: "12px" }}>✦</div>
                <div style={{ fontSize: "14px", color: "#ffffff55" }}>Enter a topic and click Generate</div>
              </>
            )}
          </div>

          {aiStatus !== "done" && !aiLoading && (
            <button onClick={handleAiGenerate} style={{
              width: "100%", background: "linear-gradient(135deg, #e8c97e, #c9973e)",
              border: "none", borderRadius: "12px", padding: "16px",
              color: "#000", fontWeight: "700", fontSize: "16px", cursor: "pointer"
            }}>✦ Generate Video from Text</button>
          )}
        </div>
      )}

      {mode === "upload" && (
      <>

      {/* STEP 1 — UPLOAD */}
      {step === 1 && (
        <div style={{ maxWidth: "600px", margin: "0 auto", padding: "40px 20px" }}>
          <h1 style={{ fontSize: "2rem", fontWeight: "900", marginBottom: "8px", textAlign: "center" }}>Upload Assets</h1>
          <p style={{ color: "#ffffff55", marginBottom: "32px", textAlign: "center" }}>Images · Narration · Music</p>

          {/* Images */}
          <div style={{ border: `2px dashed ${images.length > 0 ? "#e8c97e55" : "#ffffff22"}`, borderRadius: "14px", padding: "36px 20px", textAlign: "center", marginBottom: "12px" }}>
            <div style={{ fontSize: "40px", marginBottom: "12px" }}>🖼</div>
            {images.length === 0 ? (
              <>
                <div style={{ fontSize: "16px", color: "#ffffff88", marginBottom: "6px" }}>Select images</div>
                <div style={{ fontSize: "12px", color: "#ffffff44", marginBottom: "20px" }}>1–500 · PNG JPG WEBP</div>
              </>
            ) : (
              <>
                <div style={{ fontSize: "16px", color: "#e8c97e", marginBottom: "6px" }}>✓ {images.length} images selected</div>
                <div style={{ fontSize: "12px", color: "#ffffff44", marginBottom: "20px" }}>
                  {images.slice(0, 3).map(f => f.name).join(", ")}{images.length > 3 ? ` +${images.length - 3} more` : ""}
                </div>
              </>
            )}
            <label style={{ background: "#e8c97e", borderRadius: "8px", padding: "12px 28px", color: "#000", fontWeight: "700", fontSize: "14px", cursor: "pointer" }}>
              {images.length === 0 ? "Select Images" : "Change Images"}
              <input type="file" multiple accept="image/*" onChange={handleImageUpload} style={{ display: "none" }} />
            </label>
          </div>

          {/* Audio */}
          <label style={{ ...card(!!audio), display: "block", textAlign: "center", marginBottom: "10px", color: audio ? "#e8c97e" : "#ffffff55", fontSize: "14px" }}>
            {audio ? `✓ ${audio.name}` : "🎙 Upload Narration Audio (MP3 / WAV)"}
            <input type="file" accept="audio/*" onChange={handleAudioUpload} style={{ display: "none" }} />
          </label>

          {/* Music */}
          <label style={{ ...card(!!music), display: "block", textAlign: "center", marginBottom: "24px", color: music ? "#e8c97e" : "#ffffff55", fontSize: "14px" }}>
            {music ? `✓ ${music.name}` : "🎵 Upload Background Music (optional)"}
            <input type="file" accept="audio/*" onChange={handleMusicUpload} style={{ display: "none" }} />
          </label>

          {music && audio && (
            <div style={{ textAlign: "center", fontSize: "12px", color: "#e8c97e88", marginBottom: "20px" }}>
              ✓ Auto ducking enabled — music will lower when narration plays
            </div>
          )}

          <button onClick={handleUpload} disabled={loading || images.length === 0} style={{
            width: "100%", background: images.length === 0 ? "#ffffff11" : "linear-gradient(135deg, #e8c97e, #c9973e)",
            border: "none", borderRadius: "12px", padding: "16px",
            color: images.length === 0 ? "#ffffff33" : "#000",
            fontWeight: "700", fontSize: "16px", cursor: images.length === 0 ? "not-allowed" : "pointer"
          }}>
            {loading ? "Uploading..." : "Upload & Continue →"}
          </button>
        </div>
      )}

      {/* STEP 2 — STYLE + RATIO */}
      {step === 2 && (
        <div style={{ maxWidth: "640px", margin: "0 auto", padding: "40px 20px" }}>
          <h1 style={{ fontSize: "2rem", fontWeight: "900", marginBottom: "8px", textAlign: "center" }}>Select Style</h1>
          <p style={{ color: "#ffffff55", marginBottom: "28px", textAlign: "center" }}>Choose your visual style and format</p>

          {/* Style grid */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "10px", marginBottom: "28px" }}>
            {STYLES.map(s => (
              <div key={s.id} onClick={() => setSelectedStyle(s.id)} style={{
                border: `1px solid ${selectedStyle === s.id ? s.color : "#ffffff11"}`,
                borderRadius: "12px", padding: "16px 10px", cursor: "pointer", textAlign: "center",
                background: selectedStyle === s.id ? s.glow : "transparent",
                boxShadow: selectedStyle === s.id ? `0 0 16px ${s.glow}` : "none",
                transition: "all 0.2s"
              }}>
                <div style={{ fontSize: "24px", marginBottom: "6px" }}>{s.icon}</div>
                <div style={{ fontSize: "11px", color: selectedStyle === s.id ? "#fff" : "#ffffff55", fontWeight: "500" }}>{s.label}</div>
              </div>
            ))}
          </div>

          {/* Aspect ratio */}
          <div style={{ marginBottom: "28px" }}>
            <div style={{ fontSize: "13px", color: "#ffffff55", marginBottom: "12px", fontFamily: "monospace" }}>ASPECT RATIO</div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "10px" }}>
              {ASPECT_RATIOS.map(r => (
                <div key={r.id} onClick={() => setSelectedRatio(r.id)} style={{
                  ...card(selectedRatio === r.id), textAlign: "center"
                }}>
                  <div style={{ display: "flex", justifyContent: "center", marginBottom: "8px" }}>
                    <div style={{
                      width: `${r.w}px`, height: `${r.h}px`,
                      border: `2px solid ${selectedRatio === r.id ? "#e8c97e" : "#ffffff33"}`,
                      borderRadius: "3px"
                    }} />
                  </div>
                  <div style={{ fontSize: "14px", fontWeight: "700", color: selectedRatio === r.id ? "#e8c97e" : "#fff" }}>{r.label}</div>
                  <div style={{ fontSize: "10px", color: "#ffffff44", marginTop: "3px" }}>{r.sub}</div>
                </div>
              ))}
            </div>
          </div>

          <div style={{ display: "flex", gap: "10px" }}>
            <button onClick={() => setStep(1)} style={{ flex: 1, background: "transparent", border: "1px solid #ffffff22", borderRadius: "12px", padding: "14px", color: "#fff", cursor: "pointer" }}>Back</button>
            <button onClick={() => setStep(3)} style={{ flex: 2, background: "linear-gradient(135deg, #e8c97e, #c9973e)", border: "none", borderRadius: "12px", padding: "14px", color: "#000", fontWeight: "700", cursor: "pointer" }}>Next: Motion →</button>
          </div>
        </div>
      )}

      {/* STEP 3 — INTENSITY + CAPTIONS */}
      {step === 3 && (
        <div style={{ maxWidth: "600px", margin: "0 auto", padding: "40px 20px" }}>
          <h1 style={{ fontSize: "2rem", fontWeight: "900", marginBottom: "8px", textAlign: "center" }}>Motion & Captions</h1>
          <p style={{ color: "#ffffff55", marginBottom: "28px", textAlign: "center" }}>Set intensity and caption style</p>

          {/* Intensity */}
          <div style={{ marginBottom: "28px" }}>
            <div style={{ fontSize: "13px", color: "#ffffff55", marginBottom: "12px", fontFamily: "monospace" }}>MOTION INTENSITY</div>
            <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
              {INTENSITIES.map((label, i) => (
                <div key={i} onClick={() => setSelectedIntensity(i)} style={{
                  border: `1px solid ${selectedIntensity === i ? "#e8c97e" : "#ffffff11"}`,
                  borderRadius: "10px", padding: "14px 18px", cursor: "pointer",
                  background: selectedIntensity === i ? "#e8c97e" : "transparent",
                  color: selectedIntensity === i ? "#000" : "#ffffff66",
                  fontWeight: selectedIntensity === i ? "700" : "400",
                  display: "flex", alignItems: "center", justifyContent: "space-between",
                  transition: "all 0.2s"
                }}>
                  <span>{label}</span>
                  <div style={{ display: "flex", gap: "3px", alignItems: "flex-end" }}>
                    {[6, 10, 14, 18].map((h, k) => (
                      <div key={k} style={{ width: "4px", height: `${h}px`, borderRadius: "2px", background: k <= i ? (selectedIntensity === i ? "#000" : "#e8c97e") : "#ffffff22" }} />
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Caption type */}
          {audio && (
            <>
              <div style={{ marginBottom: "20px" }}>
                <div style={{ fontSize: "13px", color: "#ffffff55", marginBottom: "12px", fontFamily: "monospace" }}>CAPTION STYLE</div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
                  {CAPTION_TYPES.map(c => (
                    <div key={c.id} onClick={() => setCaptionType(c.id)} style={{ ...card(captionType === c.id), textAlign: "center" }}>
                      <div style={{ fontSize: "14px", fontWeight: "700", color: captionType === c.id ? "#e8c97e" : "#fff", marginBottom: "4px" }}>{c.label}</div>
                      <div style={{ fontSize: "11px", color: "#ffffff44" }}>{c.desc}</div>
                    </div>
                  ))}
                </div>
              </div>

              <div style={{ marginBottom: "28px" }}>
                <div style={{ fontSize: "13px", color: "#ffffff55", marginBottom: "12px", fontFamily: "monospace" }}>CAPTION POSITION</div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "10px" }}>
                  {CAPTION_POSITIONS.map(p => (
                    <div key={p} onClick={() => setCaptionPosition(p)} style={{ ...card(captionPosition === p), textAlign: "center" }}>
                      <div style={{ fontSize: "13px", color: captionPosition === p ? "#e8c97e" : "#ffffff66", fontWeight: captionPosition === p ? "700" : "400", textTransform: "capitalize" }}>{p}</div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}

          <div style={{ display: "flex", gap: "10px" }}>
            <button onClick={() => setStep(2)} style={{ flex: 1, background: "transparent", border: "1px solid #ffffff22", borderRadius: "12px", padding: "14px", color: "#fff", cursor: "pointer" }}>Back</button>
            <button onClick={() => setStep(4)} style={{ flex: 2, background: "linear-gradient(135deg, #e8c97e, #c9973e)", border: "none", borderRadius: "12px", padding: "14px", color: "#000", fontWeight: "700", cursor: "pointer" }}>Next: Generate →</button>
          </div>
        </div>
      )}

      {/* STEP 4 — GENERATE */}
      {step === 4 && (
        <div style={{ maxWidth: "560px", margin: "0 auto", padding: "40px 20px", textAlign: "center" }}>
          <h1 style={{ fontSize: "2rem", fontWeight: "900", marginBottom: "8px" }}>Generate Video</h1>
          <p style={{ color: "#ffffff55", marginBottom: "32px" }}>
            {STYLES.find(s => s.id === selectedStyle)?.label} · {selectedRatio} · {INTENSITIES[selectedIntensity]}
            {audio && ` · ${captionType === "word" ? "Word captions" : "Sentence captions"} · ${captionPosition}`}
          </p>

          <div style={{ border: "1px solid #ffffff11", borderRadius: "16px", padding: "40px 20px", marginBottom: "24px" }}>
            {status === "done" ? (
              <>
                <div style={{ fontSize: "48px", marginBottom: "16px" }}>🎉</div>
                <div style={{ fontSize: "20px", color: "#e8c97e", marginBottom: "8px", fontWeight: "bold" }}>Video Ready!</div>
                <div style={{ fontSize: "13px", color: "#ffffff44", marginBottom: "24px" }}>Your video has been generated</div>
                <button onClick={() => window.open(`${API}/download/${jobId}`)} style={{
                  background: "linear-gradient(135deg, #e8c97e, #c9973e)", border: "none",
                  borderRadius: "10px", padding: "14px 32px", color: "#000",
                  fontWeight: "700", fontSize: "15px", cursor: "pointer",
                  boxShadow: "0 0 30px #e8c97e44"
                }}>
                  ⬇ Download MP4
                </button>
              </>
            ) : status === "error" ? (
              <>
                <div style={{ fontSize: "48px", marginBottom: "16px" }}>❌</div>
                <div style={{ fontSize: "18px", color: "#ff4444", marginBottom: "8px" }}>Generation failed</div>
                <div style={{ fontSize: "13px", color: "#ffffff44" }}>Please try again</div>
              </>
            ) : loading ? (
              <>
                <div style={{ fontSize: "16px", color: "#ffffff88", marginBottom: "20px" }}>
                  {progress < 20 ? "Resizing images..." :
                   progress < 40 ? "Generating captions..." :
                   progress < 60 ? "Creating clips..." :
                   progress < 75 ? "Adding transitions..." :
                   progress < 90 ? "Mixing audio..." :
                   "Finalizing video..."}
                </div>
                <div style={{ width: "100%", height: "6px", background: "#ffffff11", borderRadius: "100px", overflow: "hidden", marginBottom: "10px" }}>
                  <div style={{ height: "100%", width: `${progress}%`, background: "linear-gradient(90deg, #e8c97e, #ff7c4d)", borderRadius: "100px", transition: "width 0.5s" }} />
                </div>
                <div style={{ fontSize: "13px", color: "#ffffff44" }}>{progress}%</div>
              </>
            ) : (
              <>
                <div style={{ fontSize: "48px", marginBottom: "16px" }}>✦</div>
                <div style={{ fontSize: "16px", color: "#ffffff88", marginBottom: "8px" }}>Ready to generate</div>
                <div style={{ fontSize: "13px", color: "#ffffff44" }}>
                  {images.length} images · {audio ? "With narration" : "No audio"} · {music ? "With music" : "No music"}
                </div>
              </>
            )}
          </div>

          {status !== "done" && (
            <div style={{ display: "flex", gap: "10px" }}>
              <button onClick={() => setStep(3)} style={{ flex: 1, background: "transparent", border: "1px solid #ffffff22", borderRadius: "12px", padding: "14px", color: "#fff", cursor: "pointer" }}>Back</button>
              {!loading && (
                <button onClick={handleGenerate} style={{
                  flex: 2, background: "linear-gradient(135deg, #e8c97e, #c9973e)",
                  border: "none", borderRadius: "12px", padding: "14px",
                  color: "#000", fontWeight: "700", fontSize: "16px", cursor: "pointer",
                  boxShadow: "0 0 40px #e8c97e44"
                }}>
                  ✦ Generate Video
                </button>
              )}
            </div>
          )}
         </div>
      )}
      </>
      )}
    </main>
  );
}