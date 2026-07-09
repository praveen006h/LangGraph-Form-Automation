import { useSelector } from 'react-redux'

function SamplesField({ readOnly }) {
  const samplesDistributed = useSelector(state => state.form.samples_distributed)

  return (
    <div className="form-field">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <label className="form-field__label">Samples Distributed</label>
        <button className="add-btn" disabled={readOnly}>+ Add Sample</button>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
        {samplesDistributed && samplesDistributed.length > 0 ? (
          samplesDistributed.map((sample, index) => (
            <div key={sample.id || index} className="sample-card">
              <span>💊</span>
              <span className="sample-card__name">{sample.product_name}</span>
              {sample.dosage && <span className="sample-card__details">{sample.dosage}</span>}
              <span className="sample-card__details">Qty: {sample.quantity || 1}</span>
            </div>
          ))
        ) : (
          <span className="chip chip--empty">No samples added.</span>
        )}
      </div>
    </div>
  )
}

export default SamplesField
