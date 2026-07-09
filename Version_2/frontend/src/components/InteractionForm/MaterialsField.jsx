import { useSelector } from 'react-redux'

function MaterialsField({ readOnly }) {
  const materialsShared = useSelector(state => state.form.materials_shared)

  return (
    <div className="form-field">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <label className="form-field__label">Materials Shared</label>
        <button className="btn btn--ghost" disabled={readOnly}>🔍 Search/Add</button>
      </div>
      <div className="chip-list">
        {materialsShared && materialsShared.length > 0 ? (
          materialsShared.map((material, index) => (
            <span key={material.id || index} className="chip">
              <span className="chip__icon">📄</span>
              {material.name}
            </span>
          ))
        ) : (
          <span className="chip chip--empty">No materials shared yet.</span>
        )}
      </div>
    </div>
  )
}

export default MaterialsField
