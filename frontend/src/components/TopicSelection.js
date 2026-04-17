import React, { useState, useEffect } from "react";

export default function TopicSelection({ topics, selectedTopics, setSelectedTopics, onNext }) {
  const [isAutomatic, setIsAutomatic] = useState(true);

  // Initialize selectedTopics if empty and we switch out of automatic
  useEffect(() => {
    if (!isAutomatic && Object.keys(selectedTopics).length === 0 && topics?.modules) {
      const initialSelection = {};
      Object.entries(topics.modules).forEach(([modName, modData]) => {
        initialSelection[modName] = Array.isArray(modData) ? [...modData] : [...(modData.topics || [])];
      });
      setSelectedTopics(initialSelection);
    }
  }, [isAutomatic, selectedTopics, setSelectedTopics, topics]);

  if (!topics || !topics.modules) {
    return (
      <section className="card">
        <h2 className="card-title">
          <span className="card-icon">🎯</span> Select Topics
        </h2>
        <p>No syllabus topics found. Please upload a syllabus first.</p>
      </section>
    );
  }

  const handleTopicToggle = (modName, topicList, topic, isChecked) => {
    setSelectedTopics((prev) => {
      const updatedMod = prev[modName] ? [...prev[modName]] : [...topicList];
      if (isChecked) {
        if (!updatedMod.includes(topic)) updatedMod.push(topic);
      } else {
        const index = updatedMod.indexOf(topic);
        if (index > -1) updatedMod.splice(index, 1);
      }
      return { ...prev, [modName]: updatedMod };
    });
  };

  const handleSelectAll = (modName, topicList, selectAll) => {
    setSelectedTopics((prev) => ({
      ...prev,
      [modName]: selectAll ? [...topicList] : [],
    }));
  };

  return (
    <section className="card">
      <h2 className="card-title">
        <span className="card-icon">🎯</span> Select Examination Topics
      </h2>
      <p className="card-desc">
        Choose specific topics to limit the scope of the generated questions.
        Or leave it on "Automatic" to use the entire syllabus.
      </p>

      <div className="page-toggle-row">
        <label className="switch">
          <input
            type="checkbox"
            checked={isAutomatic}
            onChange={(e) => {
              setIsAutomatic(e.target.checked);
              if (e.target.checked) setSelectedTopics({}); // Clear selections to signal full automatic to backend
            }}
          />
          <span className="switch-slider"></span>
        </label>
        <span className="page-toggle-label">
          {isAutomatic ? "Automatic (Process entire syllabus)" : "Custom Topic Selection"}
        </span>
      </div>

      {!isAutomatic && (
        <div className="topic-selection-grid">
          {Object.entries(topics.modules).map(([modName, modData]) => {
            const topicList = Array.isArray(modData) ? modData : (modData.topics || []);
            const currentlySelected = selectedTopics[modName] || [];
            const isAllSelected = currentlySelected.length === topicList.length;

            return (
              <div key={modName} className="module-card topic-picker-card">
                <div className="module-header-flex">
                  <span className="module-badge">{modName}</span>
                  <label className="select-all-label">
                    <input
                      type="checkbox"
                      checked={isAllSelected}
                      onChange={(e) => handleSelectAll(modName, topicList, e.target.checked)}
                    />
                    Select All
                  </label>
                </div>
                
                <ul className="topic-list interactive-topic-list">
                  {topicList.map((t, i) => {
                    const isChecked = selectedTopics[modName]?.includes(t) ?? true;
                    return (
                      <li key={i}>
                        <label className="topic-checkbox-label">
                          <input
                            type="checkbox"
                            checked={isChecked}
                            onChange={(e) => handleTopicToggle(modName, topicList, t, e.target.checked)}
                          />
                          <span className="topic-text">{t}</span>
                        </label>
                      </li>
                    );
                  })}
                </ul>
              </div>
            );
          })}
        </div>
      )}

      <button className="btn green next-btn" onClick={onNext} style={{ marginTop: "20px" }}>
        Continue to Semantic Mapping →
      </button>
    </section>
  );
}
