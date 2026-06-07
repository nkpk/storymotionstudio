"use client";
import { useState } from "react";

const STYLES = [
  { id: "horror", label: "Horror Cinematic", icon: "☠", color: "#ff2020" },
  { id: "anime", label: "Anime Recap", icon: "⚡", color: "#00d4ff" },
  { id: "documentary", label: "Documentary", icon: "🎞", color: "#f5c842" },
  { id: "science", label: "Science Explainer", icon: "🔬", color: "#7cff6b" },
  { id: "luxury", label: "Luxury Storytelling", icon: "✦", color: "#e8c97e" },
  { id: "shorts", label: "Viral Shorts", icon: "▶", color: "#ff5c87" },
];

const INTENSITIES = ["Low Motion", "Medium Motion", "High Motion", "Cinematic"];

export default function Home() {
  const [step, setStep] = useState(1);
  const [selectedStyle, setSelectedStyle] = useState("horror");
  const [selectedIntensity, setSelectedIntensity] = useState(2);

  return (
    <main style={{minHeight:"100vh", background:"#090909", color:"#fff", fontFamily:"sans-serif"}}>

      {/* NAV */}
      <nav style={{padding:"20px 32px", borderBottom:"1px solid #ffffff11", display:"flex", alignItems:"center", justifyContent:"space-between"}}>
        <div style={{color:"#e8c97e", fontSize:"20px", fontWeight:"bold"}}>
          ▶ StoryMotion Studio
        </div>
        <div style={{display:"flex", gap:"8px"}}>
          {[1,2,3,4].map(n => (
            <div key={n} style={{
              width:"32px", height:"32px", borderRadius:"50%",
              background: step === n ? "#e8c97e" : "#ffffff11",
              color: step === n ? "#000" : "#ffffff44",
              display:"flex", alignItems:"center", justifyContent:"center",
              fontSize:"13px", fontWeight:"bold", cursor:"pointer"
            }} onClick={() => setStep(n)}>
              {n}
            </div>
          ))}
        </div>
      </nav>

      {/* STEP 1 - UPLOAD */}
      {step === 1 && (
        <div style={{textAlign:"center", padding:"60px 20px 40px"}}>
          <h1 style={{fontSize:"2.5rem", fontWeight:"900", marginBottom:"12px"}}>
            Upload Your Assets
          </h1>
          <p style={{color:"#ffffff55", marginBottom:"40px"}}>
            Images · Narration · Music · Captions
          </p>

          <div style={{maxWidth:"500px", margin:"0 auto", border:"2px dashed #ffffff22", borderRadius:"16px", padding:"48px 20px", cursor:"pointer"}}>
            <div style={{fontSize:"48px", marginBottom:"16px"}}>🖼</div>
            <div style={{fontSize:"18px", color:"#ffffff88", marginBottom:"8px"}}>Drop images here</div>
            <div style={{fontSize:"13px", color:"#ffffff44"}}>1–500 images · PNG JPG WEBP</div>
            <button style={{marginTop:"24px", background:"#e8c97e", border:"none", borderRadius:"10px", padding:"14px 32px", color:"#000", fontWeight:"700", fontSize:"15px", cursor:"pointer"}}>
              Upload Images
            </button>
          </div>

          <div style={{maxWidth:"500px", margin:"20px auto", display:"grid", gridTemplateColumns:"1fr 1fr", gap:"12px"}}>
            <div style={{border:"1px solid #ffffff11", borderRadius:"10px", padding:"14px", cursor:"pointer", color:"#ffffff66"}}>🎙 Narration</div>
            <div style={{border:"1px solid #ffffff11", borderRadius:"10px", padding:"14px", cursor:"pointer", color:"#ffffff66"}}>🎵 Music</div>
            <div style={{border:"1px solid #ffffff11", borderRadius:"10px", padding:"14px", cursor:"pointer", color:"#ffffff66", gridColumn:"span 2"}}>📝 SRT Captions (optional)</div>
          </div>

          <button onClick={() => setStep(2)} style={{marginTop:"20px", background:"linear-gradient(135deg, #e8c97e, #c9973e)", border:"none", borderRadius:"12px", padding:"16px 48px", color:"#000", fontWeight:"700", fontSize:"16px", cursor:"pointer"}}>
            Next: Select Style →
          </button>
        </div>
      )}

      {/* STEP 2 - STYLE */}
      {step === 2 && (
        <div style={{textAlign:"center", padding:"60px 20px 40px"}}>
          <h1 style={{fontSize:"2.5rem", fontWeight:"900", marginBottom:"12px"}}>Select Your Style</h1>
          <p style={{color:"#ffffff55", marginBottom:"40px"}}>Choose the visual style for your video</p>

          <div style={{maxWidth:"600px", margin:"0 auto", display:"grid", gridTemplateColumns:"1fr 1fr 1fr", gap:"12px", marginBottom:"32px"}}>
            {STYLES.map(s => (
              <div key={s.id} onClick={() => setSelectedStyle(s.id)} style={{
                border:`1px solid ${selectedStyle === s.id ? s.color : "#ffffff11"}`,
                borderRadius:"12px", padding:"20px 12px",
                cursor:"pointer",
                background: selectedStyle === s.id ? s.color+"22" : "transparent",
                boxShadow: selectedStyle === s.id ? `0 0 20px ${s.color}33` : "none",
                transition:"all 0.2s"
              }}>
                <div style={{fontSize:"28px", marginBottom:"8px"}}>{s.icon}</div>
                <div style={{fontSize:"12px", color: selectedStyle === s.id ? "#fff" : "#ffffff66", fontWeight:"500"}}>{s.label}</div>
              </div>
            ))}
          </div>

          <div style={{display:"flex", gap:"12px", justifyContent:"center"}}>
            <button onClick={() => setStep(1)} style={{background:"transparent", border:"1px solid #ffffff22", borderRadius:"12px", padding:"14px 32px", color:"#fff", fontSize:"15px", cursor:"pointer"}}>
              ← Back
            </button>
            <button onClick={() => setStep(3)} style={{background:"linear-gradient(135deg, #e8c97e, #c9973e)", border:"none", borderRadius:"12px", padding:"14px 32px", color:"#000", fontWeight:"700", fontSize:"15px", cursor:"pointer"}}>
              Next: Set Intensity →
            </button>
          </div>
        </div>
      )}

      {/* STEP 3 - INTENSITY */}
      {step === 3 && (
        <div style={{textAlign:"center", padding:"60px 20px 40px"}}>
          <h1 style={{fontSize:"2.5rem", fontWeight:"900", marginBottom:"12px"}}>Set Motion Intensity</h1>
          <p style={{color:"#ffffff55", marginBottom:"40px"}}>How much movement do you want?</p>

          <div style={{maxWidth:"500px", margin:"0 auto", display:"flex", flexDirection:"column", gap:"12px", marginBottom:"32px"}}>
            {INTENSITIES.map((label, i) => (
              <div key={i} onClick={() => setSelectedIntensity(i)} style={{
                border:`1px solid ${selectedIntensity === i ? "#e8c97e" : "#ffffff11"}`,
                borderRadius:"12px", padding:"18px 24px",
                cursor:"pointer",
                background: selectedIntensity === i ? "#e8c97e" : "transparent",
                color: selectedIntensity === i ? "#000" : "#ffffff66",
                fontWeight: selectedIntensity === i ? "700" : "400",
                fontSize:"15px", transition:"all 0.2s",
                display:"flex", alignItems:"center", justifyContent:"space-between"
              }}>
                <span>{label}</span>
                <div style={{display:"flex", gap:"3px", alignItems:"flex-end"}}>
                  {[6,10,14,18].map((h, k) => (
                    <div key={k} style={{width:"4px", height:`${h}px`, borderRadius:"2px", background: k <= i ? (selectedIntensity === i ? "#000" : "#e8c97e") : "#ffffff22"}}/>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div style={{display:"flex", gap:"12px", justifyContent:"center"}}>
            <button onClick={() => setStep(2)} style={{background:"transparent", border:"1px solid #ffffff22", borderRadius:"12px", padding:"14px 32px", color:"#fff", fontSize:"15px", cursor:"pointer"}}>
              ← Back
            </button>
            <button onClick={() => setStep(4)} style={{background:"linear-gradient(135deg, #e8c97e, #c9973e)", border:"none", borderRadius:"12px", padding:"14px 32px", color:"#000", fontWeight:"700", fontSize:"15px", cursor:"pointer"}}>
              Next: Generate →
            </button>
          </div>
        </div>
      )}

      {/* STEP 4 - GENERATE */}
      {step === 4 && (
        <div style={{textAlign:"center", padding:"60px 20px 40px"}}>
          <h1 style={{fontSize:"2.5rem", fontWeight:"900", marginBottom:"12px"}}>Ready to Generate</h1>
          <p style={{color:"#ffffff55", marginBottom:"40px"}}>
            Style: {STYLES.find(s => s.id === selectedStyle)?.label} · {INTENSITIES[selectedIntensity]}
          </p>

          <div style={{maxWidth:"500px", margin:"0 auto", border:"1px solid #ffffff11", borderRadius:"16px", padding:"48px 20px", marginBottom:"32px"}}>
            <div style={{fontSize:"48px", marginBottom:"16px"}}>✦</div>
            <div style={{fontSize:"18px", color:"#ffffff88", marginBottom:"8px"}}>Everything is ready</div>
            <div style={{fontSize:"13px", color:"#ffffff44"}}>Click generate to create your video</div>
          </div>

          <div style={{display:"flex", gap:"12px", justifyContent:"center"}}>
            <button onClick={() => setStep(3)} style={{background:"transparent", border:"1px solid #ffffff22", borderRadius:"12px", padding:"14px 32px", color:"#fff", fontSize:"15px", cursor:"pointer"}}>
              ← Back
            </button>
            <button style={{background:"linear-gradient(135deg, #e8c97e, #c9973e)", border:"none", borderRadius:"12px", padding:"14px 48px", color:"#000", fontWeight:"700", fontSize:"16px", cursor:"pointer", boxShadow:"0 0 40px #e8c97e44"}}>
              ✦ Generate Video
            </button>
          </div>
        </div>
      )}

    </main>
  );
}