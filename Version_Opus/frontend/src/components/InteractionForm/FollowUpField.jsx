import { useSelector, useDispatch } from 'react-redux'
import { updateFormFields } from '../../store/formSlice'

function FollowUpField({ readOnly }) {
  const followUpActions = useSelector(state => state.form.follow_up_actions)
  const dispatch = useDispatch()

  return (
    <div className="form-field">
      <label className="form-field__label">Follow-up Actions</label>
      <textarea
        className="form-field__textarea"
        placeholder="Follow-up actions will be populated by AI assistant..."
        value={followUpActions || ''}
        readOnly={readOnly}
        onChange={(e) => !readOnly && dispatch(updateFormFields({ follow_up_actions: e.target.value }))}
        rows={3}
      />
    </div>
  )
}

export default FollowUpField
