import React, { useState, useEffect, useRef, useLayoutEffect } from "react";
import "./App.css";

function App() {
  const [message, setMessage] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("");
  const [responseData, setResponseData] = useState(null);
  const [outputData, setOutputData] = useState(null);
  const [file, setFile] = useState(null);
  const [response, setResponse] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showTimeline, setShowTimeline] = useState(false);
  const [timelineLines, setTimelineLines] = useState([]);
  const [videoUrl, setVideoUrl] = useState("");
  const [uploadMode, setUploadMode] = useState("file");
  const [frameImages, setFrameImages] = useState({});

  useEffect(() => {
    fetch("http://localhost:5000/api/hello")
      .then((response) => response.json())
      .then((data) => setMessage(data.message))
      .catch((error) => console.error("Error:", error));
  }, []);

  useEffect(() => {
    if (response?.combined_result) {
      setTimelineLines(response.combined_result.timeline.split("\n").filter((line) => line.trim()));
    }
  }, [response]);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setUploadStatus("");
    setResponseData(null);
    setOutputData(null);
  };

  const handleUpload = async () => {
    if (!file) {
      setUploadStatus("Please select a file");
      return;
    }

    setIsLoading(true);
    const formData = new FormData();
    formData.append("video", file);

    try {
      setUploadStatus("Uploading...");
      const response = await fetch("http://localhost:5000/api/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      setResponse(data);

      if (response.ok) {
        setUploadStatus("Upload successful!");
        setOutputData({
          status: "Processing completed",
          originalFile: data.filename,
          videos: data.separated_videos,
          analysis: data.analysis_results,
        });
      } else {
        setUploadStatus("Upload failed");
      }
    } catch (error) {
      console.error("Error:", error);
      setUploadStatus("Upload error");
    } finally {
      setIsLoading(false);
    }
  };

  const handleUrlUpload = async () => {
    if (!videoUrl) {
      setUploadStatus("Please enter video URL");
      return;
    }

    setIsLoading(true);
    try {
      setUploadStatus("Uploading...");
      const response = await fetch("http://localhost:5000/api/upload-url", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url: videoUrl }),
      });

      const data = await response.json();
      setResponse(data);

      if (response.ok) {
        setUploadStatus("Upload successful!");
        setOutputData({
          status: "Processing completed",
          originalFile: data.filename,
          videos: data.separated_videos,
          analysis: data.analysis_results,
        });
      } else {
        setUploadStatus("Upload failed");
      }
    } catch (error) {
      console.error("Error:", error);
      setUploadStatus("Upload error");
    } finally {
      setIsLoading(false);
    }
  };

  const handleGetFrame = async (videoPath, timestamp, index, view) => {
    console.log(`Request frame ${view}:`, { videoPath, timestamp, index });

    if (!videoPath || timestamp === undefined || timestamp === null) {
      console.error("Invalid video path or timestamp:", { videoPath, timestamp, index });
      return;
    }

    try {
      const response = await fetch("http://localhost:5000/api/get_frame", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          video_path: videoPath,
          timestamp: timestamp,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to get screenshot: ${response.status}`);
      }

      const blob = await response.blob();
      const imageUrl = URL.createObjectURL(blob);
      console.log(`Successfully got frame ${view}:`, { index, imageUrl });

      setFrameImages((prev) => {
        const newImages = {
          ...(prev || {}),
          [index]: {
            ...(prev?.[index] || {}),
            [view]: imageUrl,
          },
        };
        console.log("Updated image state:", newImages);
        return newImages;
      });
    } catch (error) {
      console.error(`Failed to get frame ${view}:`, error);
      setUploadStatus(`Failed to get ${view} view screenshot`);
    }
  };

  useEffect(() => {
    if (response?.combined_result && response?.separated_videos?.front && response?.separated_videos?.top) {
      console.log("Video paths:", {
        top: response.separated_videos.top,
        front: response.separated_videos.front,
      });

      timelineLines.forEach((line, index) => {
        const timestampMatch = line.match(/(\d+:\d+)(?:-\d+:\d+)?/);
        if (timestampMatch) {
          const timeStr = timestampMatch[1];
          const [minutes, seconds] = timeStr.split(":").map(Number);
          // If timestamp is 0 seconds, use 1 second
          let timestamp = minutes * 60 + seconds;
          if (timestamp === 0) {
            timestamp = 1;
          }
          console.log(`Processing line ${index}:`, { line, timeStr, originalTimestamp: minutes * 60 + seconds, adjustedTimestamp: timestamp });

          const topPath = response.separated_videos.top.replace(/\\/g, "/");
          const frontPath = response.separated_videos.front.replace(/\\/g, "/");

          if (timestamp >= 0) {
            handleGetFrame(topPath, timestamp, index, "top");
            handleGetFrame(frontPath, timestamp, index, "front");
          } else {
            console.error(`Invalid timestamp ${index}:`, timestamp);
          }
        } else {
          console.error(`Cannot extract timestamp from text ${index}:`, line);
        }
      });
    } else {
      console.log("Missing necessary video information:", {
        hasResult: !!response?.combined_result,
        hasFront: !!response?.separated_videos?.front,
        hasTop: !!response?.separated_videos?.top,
      });
    }
  }, [timelineLines, response]);

  const TimelineView = () => {
    const [editingIndex, setEditingIndex] = useState(null);
    const [editText, setEditText] = useState("");
    const caretRef = useRef({ start: 0, end: 0 });
    const textareaRef = useRef(null);

    // 在布局阶段同步恢复光标位置
    useLayoutEffect(() => {
      const el = textareaRef.current;
      if (el && document.activeElement === el && editingIndex !== null) {
        el.setSelectionRange(caretRef.current.start, caretRef.current.end);
      }
    }, [editText, editingIndex]);

    if (!response?.combined_result) return null;

    const handleEdit = (index) => {
      setEditingIndex(index);
      setEditText(timelineLines[index]);
    };

    const handleChange = (e) => {
      // 保存光标位置
      caretRef.current = {
        start: e.target.selectionStart,
        end: e.target.selectionEnd,
      };
      setEditText(e.target.value);
    };

    const handleSave = (index) => {
      const newLines = [...timelineLines];
      newLines[index] = editText;
      setTimelineLines(newLines);
      setEditingIndex(null);
    };

    const handleCancel = () => {
      setEditingIndex(null);
    };

    return (
      <div className="timeline-container">
        <div className="timeline-header">
          <h2>Timeline View</h2>
          <button className="back-button" onClick={() => setShowTimeline(false)}>
            Back
          </button>
        </div>
        <div className="timeline-content">
          {timelineLines.map((line, index) => (
            <div key={index} className="timeline-item">
              <div className="line-content">
                <div className="line-frame">
                  {frameImages[index] ? (
                    <>
                      {frameImages[index].top ? <img src={frameImages[index].top} alt="Top view screenshot" /> : <div className="frame-placeholder">Loading top view...</div>}
                      {frameImages[index].front ? <img src={frameImages[index].front} alt="Front view screenshot" /> : <div className="frame-placeholder">Loading front view...</div>}
                    </>
                  ) : (
                    <div className="frame-placeholder">Preparing to load...</div>
                  )}
                </div>
                <div className="line-text-container">
                  {editingIndex === index ? (
                    <div className="edit-container">
                      <textarea ref={textareaRef} value={editText} onChange={handleChange} className="edit-textarea" autoFocus />
                      <div className="edit-buttons">
                        <button className="save-button" onClick={() => handleSave(index)}>
                          Save
                        </button>
                        <button className="cancel-button" onClick={handleCancel}>
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <span className="line-text">{line}</span>
                      <button className="edit-button" onClick={() => handleEdit(index)}>
                        Edit
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  if (showTimeline) {
    return <TimelineView />;
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Video Upload System</h1>
        <div style={{ display: "flex", alignItems: "center" }}>
          <a href="https://github.com/ryan0980/20250430_bot_video_recognition" target="_blank" rel="noopener noreferrer" className="github-link">
            GitHub
          </a>
          <span className="author-info">BY: Shi Qiu</span>
        </div>
      </header>

      <div className="main-container">
        <div className="upload-section">
          <h2>Upload Video</h2>
          <div className="upload-container">
            <div className="upload-mode-switch">
              <button className={`mode-button ${uploadMode === "file" ? "active" : ""}`} onClick={() => setUploadMode("file")}>
                File Upload
              </button>
              <button className={`mode-button ${uploadMode === "url" ? "active" : ""}`} onClick={() => setUploadMode("url")}>
                URL Upload
              </button>
            </div>

            {uploadMode === "file" ? (
              <div className="file-upload">
                <input type="file" accept="video/*" onChange={handleFileChange} className="file-input" />
                <div className="upload-button-container">
                  <div className={`status-message ${uploadStatus === "Upload successful!" ? "success" : uploadStatus === "Uploading..." ? "uploading" : uploadStatus.includes("failed") || uploadStatus.includes("error") ? "error" : ""}`}>{uploadStatus}</div>
                  <button onClick={handleUpload} className="upload-button">
                    Upload Video
                  </button>
                </div>
              </div>
            ) : (
              <div className="url-upload">
                <input type="text" value={videoUrl} onChange={(e) => setVideoUrl(e.target.value)} placeholder="Enter video URL" className="url-input" />
                <div className="upload-button-container">
                  <div className={`status-message ${uploadStatus === "Upload successful!" ? "success" : uploadStatus === "Uploading..." ? "uploading" : uploadStatus.includes("failed") || uploadStatus.includes("error") ? "error" : ""}`}>{uploadStatus}</div>
                  <button onClick={handleUrlUpload} className="upload-button">
                    Upload Video
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {response && (
          <div className="response-section">
            <div className="response-box">
              <h3>Server Response</h3>
              <pre>{JSON.stringify(response, null, 2)}</pre>
            </div>
          </div>
        )}

        <div className="result-section">
          {response && (
            <>
              <div className="result-box">
                <h3>Processing Results</h3>
                <div className="result-content">
                  <p>
                    <strong>Original File:</strong> {response.filename}
                  </p>
                  <p>
                    <strong>Status:</strong> {response.message}
                  </p>

                  <div className="separated-videos">
                    <h4>Separated Videos:</h4>
                    {response.separated_videos &&
                      Object.entries(response.separated_videos).map(([view, path]) => (
                        <p key={view}>
                          {view}: {path}
                        </p>
                      ))}
                  </div>

                  <div className="analysis-results">
                    <h4>Action Analysis Results:</h4>
                    {response.analysis_results &&
                      Object.entries(response.analysis_results).map(([view, result]) => (
                        <div key={view} className="view-analysis">
                          <h5>{view} View:</h5>
                          <pre>{result}</pre>
                        </div>
                      ))}
                  </div>
                </div>
              </div>

              <div className="combined-result-box">
                <h3>Combined Results</h3>
                <div className="combined-result-content">
                  {response.combined_result && (
                    <>
                      <div className="video-summary">
                        <h4>Video Summary</h4>
                        <p>{response.combined_result.summary}</p>
                      </div>
                      <h4>Detailed Timeline</h4>
                      <pre>{response.combined_result.timeline}</pre>
                    </>
                  )}
                </div>
                {response.combined_result && (
                  <button className="timeline-button" onClick={() => setShowTimeline(true)}>
                    View Timeline
                  </button>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
