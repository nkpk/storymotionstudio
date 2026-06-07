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

export default function Home() {
  const [step, setStep] = useState(1);
  const [selectedStyle, setSelectedStyle] = useState("horror");
  const [selectedIntensity, setSelectedIntensity] = useState(2);
  const [images, setImages] = useState<File[]>([]);
  const [audio, setAudio] = useState<File | null>(null);
  const [jobId, setJobId] = useState("");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setImages(Array.from(e.target.files));
    }
  };

  const handleAudioUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setAudio(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (images.length === 0) {
      alert("Please select images first");
      return;
    }
    setLoading(true);
    setStatus("Uploading...");
    const formData = new FormData();
    images.forEach(img => formData.append("images", img));
    if (audio) formData.append("audio", audio);
    try {
      const res = await fetch(`${API}/upload`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setJobId(data.job_id);
      setStatus("Uploaded!");
      setLoading(false);
      setStep(2);
    } catch (err) {
      setStatus("Upload failed.");
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    if (!jobId) {
      alert("Please upload images first");
      return;
    }
    setLoading(true);
    setStatus("generating");
    setProgress(0);
    const interval = setInterval(() => {
      setProgress(p => {
        if (p >= 90) { clearInterval(interval); return 90; }
        return p + 5;
      });
    }, 500);
    try {
      const style = STYLES.find(s => s.id === selectedStyle)?.label || "Horror Cinematic";
      const intensity = INTENSITIES[selectedIntensity];
      const res = await fetch(
        `${API}/generate/${jobId}?style=${encodeURIComponent(style)}&intensity=${encodeURIComponent(intensity)}`,
        { method: "POST" }
      );
      const data = await res.json();
      clearInterval(interval);
      setProgress(100);
      setStatus(data.status === "done" ? "done" : "error");
      setLoading(false);
    } catch (err) {
      clearInterval(interval);
      setStatus("error");
      setLoading(false);
    }
  };

  return (
    <main style={{ minHeight: "100vh", background: "#090909", color: "#fff", fontFamily: "sans-serif" }}>

      {/* NAV */}
      <nav style={{ padding: "20px 32px", borderBottom: "1px solid #ffffff11", display: "flex", alignItems: "center", justifyContent: "space-between", background: "#09090988", backdropFilter: "blur(20px)", position: "sticky", top: 0, zIndex: 100 }}>
        <div style={{ color: "#e8c97e", fontSize: "20px", fontWeight: "bold" }}>
          ▶ StoryMotion Studio
        </div>
        <div style={{ display: "flex", gap: "8px" }}>
          {[1, 2, 3, 4].map(n => (
            <div key={n} onClick={() => setStep(n)} style={{
              width: "32px", height: "32px", borderRadius: "50%",
              background: step === n ? "#e8c97e" : "#ffffff11",
              color: step === n ? "#000" : "#ffffff44",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: "13px", fontWeight: "bold", cursor: "pointer"
            }}>
              {n}
            </div>
          ))}
        </div>
      </nav>

      {/* STEP 1 - UPLOAD */}
      {step === 1 && (
        <div style={{ textAlign: "center", padding: "60px 20px 40px" }}>
          <h1 style={{ fontSize: "2.5rem", fontWeight: "900", marginBottom: "12px" }}>
            Upload Your Assets
          </h1>
          <p style={{ color: "#ffffff55", marginBottom: "40px" }}>
            Images · Narration · Music · Captions
          </p>

          {/* IMAGE UPLOAD */}
          <div style={{ maxWidth: "500px", margin: "0 auto", border: `2px dashed ${images.length > 0 ? "#e8c97e55" : "#ffffff22"}`, borderRadius: "16px", padding: "48px 20px", marginBottom: "16px", transition: "border-color 0.3s" }}>
            <div style={{ fontSize: "48px", marginBottom: "16px" }}>🖼</div>
            {images.length === 0 ? (
              <>
                <div style={{ fontSize: "18px", color: "#ffffff88", marginBottom: "8px" }}>Drop images here</div>
                <div style={{ fontSize: "13px", color: "#ffffff44", marginBottom: "24px" }}>1-500 images · PNG JPG WEBP</div>
              </>
            ) : (
              <>
                <div style={{ fontSize: "18px", color: "#e8c97e", marginBottom: "8px" }}>✓ {images.length} images selected</div>
                <div style={{ fontSize: "13px", color: "#ffffff44", marginBottom: "24px" }}>
                  {images.slice(0, 3).map(f => f.name).join(", ")}{images.length > 3 ? `... +${images.length - 3} more` : ""}
                </div>
              </>
            )}
            <label style={{ background: "#e8c97e", borderRadius: "10px", padding: "14px 32px", color: "#000", fontWeight: "700", fontSize: "15px", cursor: "pointer" }}>
              {images.length === 0 ? "Select Images" : "Change Images"}
              <input type="file" multiple accept="image/*" onChange={handleImageUpload} style={{ display: "none" }} />
            </label>
          </div>

          {/* AUDIO UPLOAD */}
          <div style={{ maxWidth: "500px", margin: "0 auto 16px", display: "grid", gridTemplateColumns: "1fr", gap: "12px" }}>
            <label style={{
              border: `1px solid ${audio ? "#e8c97e55" : "#ffffff11"}`,
              borderRadius: "10px", padding: "16px",
              cursor: "pointer",
              color: audio ? "#e8c97e" : "#ffffff66",
              textAlign: "center",
              background: audio ? "#e8c97e08" : "transparent",
              display: "block",
              transition: "all 0.3s"
            }}>
              {audio ? `✓ ${audio.name}` : "🎙 Upload Narration Audio (MP3 / WAV)"}
              <input type="file" accept="audio/*" onChange={handleAudioUpload} style={{ display: "none" }} />
            </label>
          </div>

          {/* OPTIONAL NOTE */}
          <div style={{ maxWidth: "500px", margin: "0 auto 24px" }}>
            <div style={{ fontSize: "12px", color: "#ffffff33", fontFamily: "monospace" }}>
              {audio ? "✓ Audio will sync images automatically" : "No audio? Images will use fixed duration per style"}
            </div>
          </div>

          {status && (
            <div style={{ color: "#e8c97e", marginBottom: "16px", fontSize: "14px" }}>{status}</div>
          )}

          <button
            onClick={handleUpload}
            disabled={loading || images.length === 0}
            style={{
              background: images.length === 0 ? "#ffffff22" : "linear-gradient(135deg, #e8c97e, #c9973e)",
              border: "none", borderRadius: "12px", padding: "16px 48px",
              color: images.length === 0 ? "#ffffff44" : "#000",
              fontWeight: "700", fontSize: "16px",
              cursor: images.length === 0 ? "not-allowed" : "pointer",
              boxShadow: images.length > 0 ? "0 0 30px #e8c97e33" : "none"
            }}>
            {loading ? "Uploading..." : "Upload & Continue →"}
          </button>
        </div>
      )}

      {/* STEP 2 - STYLE */}
      {step === 2 && (
        <div style={{ textAlign: "center", padding: "60px 20px 40px" }}>
          <h1 style={{ fontSize: "2.5rem", fontWeight: "900", marginBottom: "12px" }}>Select Your Style</h1>
          <p style={{ color: "#ffffff55", marginBottom: "40px" }}>Choose the visual style for your video</p>

          <div style={{ maxWidth: "600px", margin: "0 auto", display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "12px", marginBottom: "32px" }}>
            {STYLES.map(s => (
              <div key={s.id} onClick={() => setSelectedStyle(s.id)} style={{
                border: `1px solid ${selectedStyle === s.id ? s.color : "#ffffff11"}`,
                borderRadius: "12px", padding: "20px 12px", cursor: "pointer",
                background: selectedStyle === s.id ? s.glow : "transparent",
                boxShadow: selectedStyle === s.id ? `0 0 20px ${s.glow}` : "none",
                transition: "all 0.2s"
              }}>
                <div style={{ fontSize: "28px", marginBottom: "8px" }}>{s.icon}</div>
                <div style={{ fontSize: "12px", color: selectedStyle === s.id ? "#fff" : "#ffffff66", fontWeight: "500" }}>{s.label}</div>
              </div>
            ))}
          </div>

          <div style={{ display: "flex", gap: "12px", justifyContent: "center" }}>
            <button onClick={() => setStep(1)} style={{ background: "transparent", border: "1px solid #ffffff22", borderRadius: "12px", padding: "14px 32px", color: "#fff", fontSize: "15px", cursor: "pointer" }}>
              Back
            </button>
            <button onClick={() => setStep(3)} style={{ background: "linear-gradient(135deg, #e8c97e, #c9973e)", border: "none", borderRadius: "12px", padding: "14px 32px", color: "#000", fontWeight: "700", fontSize: "15px", cursor: "pointer" }}>
              Next: Set Intensity
            </button>
          </div>
        </div>
      )}

      {/* STEP 3 - INTENSITY */}
      {step === 3 && (
        <div style={{ textAlign: "center", padding: "60px 20px 40px" }}>
          <h1 style={{ fontSize: "2.5rem", fontWeight: "900", marginBottom: "12px" }}>Set Motion Intensity</h1>
          <p style={{ color: "#ffffff55", marginBottom: "40px" }}>How much movement do you want?</p>

          <div style={{ maxWidth: "500px", margin: "0 auto", display: "flex", flexDirection: "column", gap: "12px", marginBottom: "32px" }}>
            {INTENSITIES.map((label, i) => (
              <div key={i} onClick={() => setSelectedIntensity(i)} style={{
                border: `1px solid ${selectedIntensity === i ? "#e8c97e" : "#ffffff11"}`,
                borderRadius: "12px", padding: "18px 24px", cursor: "pointer",
                background: selectedIntensity === i ? "#e8c97e" : "transparent",
                color: selectedIntensity === i ? "#000" : "#ffffff66",
                fontWeight: selectedIntensity === i ? "700" : "400",
                fontSize: "15px", transition: "all 0.2s",
                display: "flex", alignItems: "center", justifyContent: "space-between"
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

          <div style={{ display: "flex", gap: "12px", justifyContent: "center" }}>
            <button onClick={() => setStep(2)} style={{ background: "transparent", border: "1px solid #ffffff22", borderRadius: "12px", padding: "14px 32px", color: "#fff", fontSize: "15px", cursor: "pointer" }}>
              Back
            </button>
            <button onClick={() => setStep(4)} style={{ background: "linear-gradient(135deg, #e8c97e, #c9973e)", border: "none", borderRadius: "12px", padding: "14px 32px", color: "#000", fontWeight: "700", fontSize: "15px", cursor: "pointer" }}>
              Next: Generate
            </button>
          </div>
        </div>
      )}

      {/* STEP 4 - GENERATE */}
      {step === 4 && (
        <div style={{ textAlign: "center", padding: "60px 20px 40px" }}>
          <h1 style={{ fontSize: "2.5rem", fontWeight: "900", marginBottom: "12px" }}>Generate Your Video</h1>
          <p style={{ color: "#ffffff55", marginBottom: "40px" }}>
            {STYLES.find(s => s.id === selectedStyle)?.label} · {INTENSITIES[selectedIntensity]}
            {audio && ` · 🎙 ${audio.name}`}
          </p>

          <div style={{ maxWidth: "500px", margin: "0 auto", border: "1px solid #ffffff11", borderRadius: "16px", padding: "48px 20px", marginBottom: "32px" }}>
            {status === "done" ? (
              <>
                <div style={{ fontSize: "48px", marginBottom: "16px" }}>🎉</div>
                <div style={{ fontSize: "20px", color: "#e8c97e", marginBottom: "8px", fontWeight: "bold" }}>Video Ready!</div>
                <div style={{ fontSize: "13px", color: "#ffffff44", marginBottom: "24px" }}>Your video has been generated successfully</div>
                <button
                  onClick={() => window.open(`${API}/download/${jobId}`)}
                  style={{ background: "linear-gradient(135deg, #e8c97e, #c9973e)", border: "none", borderRadius: "10px", padding: "14px 32px", color: "#000", fontWeight: "700", fontSize: "15px", cursor: "pointer", boxShadow: "0 0 30px #e8c97e44" }}>
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
                <div style={{ fontSize: "18px", color: "#ffffff88", marginBottom: "24px" }}>Generating your video...</div>
                <div style={{ width: "100%", height: "6px", background: "#ffffff11", borderRadius: "100px", overflow: "hidden", marginBottom: "12px" }}>
                  <div style={{ height: "100%", width: `${progress}%`, background: "linear-gradient(90deg, #e8c97e, #ff7c4d)", borderRadius: "100px", transition: "width 0.5s" }} />
                </div>
                <div style={{ fontSize: "13px", color: "#ffffff44" }}>{progress}%</div>
              </>
            ) : (
              <>
                <div style={{ fontSize: "48px", marginBottom: "16px" }}>✦</div>
                <div style={{ fontSize: "18px", color: "#ffffff88", marginBottom: "8px" }}>Everything is ready</div>
                <div style={{ fontSize: "13px", color: "#ffffff44" }}>
                  {images.length} images · {audio ? "With narration" : "No audio"} · {INTENSITIES[selectedIntensity]}
                </div>
              </>
            )}
          </div>

          {status !== "done" && (
            <div style={{ display: "flex", gap: "12px", justifyContent: "center" }}>
              <button onClick={() => setStep(3)} style={{ background: "transparent", border: "1px solid #ffffff22", borderRadius: "12px", padding: "14px 32px", color: "#fff", fontSize: "15px", cursor: "pointer" }}>
                Back
              </button>
              {!loading && (
                <button onClick={handleGenerate} style={{ background: "linear-gradient(135deg, #e8c97e, #c9973e)", border: "none", borderRadius: "12px", padding: "14px 48px", color: "#000", fontWeight: "700", fontSize: "16px", cursor: "pointer", boxShadow: "0 0 40px #e8c97e44" }}>
                  ✦ Generate Video
                </button>
              )}
            </div>
          )}
        </div>
      )}

    </main>
  );
}