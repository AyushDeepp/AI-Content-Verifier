import React, { useState } from "react";
import { FaImage, FaVideo, FaCloudUploadAlt } from "react-icons/fa";
import "./UploadCard.css";

const UploadCard = ({ onUpload, type, accept }) => {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (selectedFile) => {
    setFile(selectedFile);
    if (onUpload) {
      onUpload(selectedFile);
    }
  };

  const getUploadIcon = () => {
    switch (type) {
      case "image":
        return <FaImage />;
      case "video":
        return <FaVideo />;
      default:
        return <FaCloudUploadAlt />;
    }
  };

  return (
    <div
      className={`upload-card ${dragActive ? "drag-active" : ""}`}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      <div className="upload-content">
        <div className="upload-icon">{getUploadIcon()}</div>
        {file ? (
          <div className="file-info">
            <p className="file-name">{file.name}</p>
            <p className="file-size">
              {(file.size / 1024 / 1024).toFixed(2)} MB
            </p>
          </div>
        ) : (
          <>
            <h3 className="upload-title">Drag & Drop</h3>
            <p className="upload-subtitle">or click to browse</p>
          </>
        )}
        <input
          type="file"
          id={`file-upload-${type}`}
          accept={accept}
          onChange={handleChange}
          className="file-input"
        />
        <label htmlFor={`file-upload-${type}`} className="upload-button">
          {file ? "Change File" : "Select File"}
        </label>
      </div>
    </div>
  );
};

export default UploadCard;
