import { useSelector, useDispatch } from 'react-redux'
import { updateFormFields } from '../../store/formSlice'

function OutcomesField({ readOnly }) {
  const outcomes = useSelector(state => state.form.outcomes)
  const dispatch = useDispatch()

  return (
    <div className="form-field">
      <label className="form-field__label">Outcomes</label>
      <textarea
        className="form-field__textarea"
        placeholder="Key outcomes or agreements..."
        value={outcomes || ''}
        readOnly={readOnly}
        onChange={(e) => !readOnly && dispatch(updateFormFields({ outcomes: e.target.value }))}
        rows={3}
      />
    </div>
  )
}

export default OutcomesField
