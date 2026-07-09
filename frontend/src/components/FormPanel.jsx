import React from 'react';
import { useSelector } from 'react-redux';

const FormPanel = () => {
  const formState = useSelector((state) => state.form);

  return (
    <div className="panel form-panel">
      <h2 style={{ marginBottom: '1.5rem', color: 'var(--primary-color)' }}>Log Interaction Details</h2>
      
      <div className="form-group">
        <label>HCP Name</label>
        <input type="text" className="form-control" value={formState.hcpName || ''} readOnly placeholder="Populated by AI..." />
      </div>

      <div className="form-group">
        <label>Date</label>
        <input type="text" className="form-control" value={formState.date || ''} readOnly placeholder="Populated by AI..." />
      </div>

      <div className="form-group">
        <label>Topics Discussed</label>
        <textarea className="form-control" value={formState.topics || ''} readOnly placeholder="Populated by AI..."></textarea>
      </div>

      <div className="form-group">
        <label>Materials Shared</label>
        <div className="form-control" style={{ minHeight: '50px' }} readOnly>
          {formState.materials && formState.materials.length > 0 ? (
            <div className="tags-container">
              {formState.materials.map((mat, idx) => <span key={idx} className="tag">{mat}</span>)}
            </div>
          ) : <span style={{ color: '#9ca3af' }}>No materials added.</span>}
        </div>
      </div>

      <div className="form-group">
        <label>Samples Distributed</label>
        <div className="form-control" style={{ minHeight: '50px' }} readOnly>
          {formState.samples && formState.samples.length > 0 ? (
            <div className="tags-container">
              {formState.samples.map((samp, idx) => <span key={idx} className="tag">{samp}</span>)}
            </div>
          ) : <span style={{ color: '#9ca3af' }}>No samples added.</span>}
        </div>
      </div>

      <div className="form-group">
        <label>Observed/Inferred HCP Sentiment</label>
        <div className="radio-group">
          <label className="radio-option">
            <input type="radio" checked={formState.sentiment === 'Positive'} disabled /> 😃 Positive
          </label>
          <label className="radio-option">
            <input type="radio" checked={formState.sentiment === 'Neutral'} disabled /> 😐 Neutral
          </label>
          <label className="radio-option">
            <input type="radio" checked={formState.sentiment === 'Negative'} disabled /> 😠 Negative
          </label>
        </div>
      </div>

      <div className="form-group">
        <label>Outcomes</label>
        <textarea className="form-control" value={formState.outcomes || ''} readOnly placeholder="Populated by AI..."></textarea>
      </div>

      <div className="form-group">
        <label>Follow-up Actions</label>
        <textarea className="form-control" value={formState.followUp || ''} readOnly placeholder="Populated by AI..."></textarea>
      </div>
    </div>
  );
};

export default FormPanel;
