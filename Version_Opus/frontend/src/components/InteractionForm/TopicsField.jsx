import { useSelector, useDispatch } from 'react-redux'
import { updateFormFields } from '../../store/formSlice'

function TopicsField({ readOnly }) {
  const topicsDiscussed = useSelector(state => state.form.topics_discussed)
  const dispatch = useDispatch()

  return (
    <div className="form-field">
      <label className="form-field__label">Topics Discussed</label>
      <textarea
        className="form-field__textarea"
        placeholder="Topics will be populated by AI assistant..."
        value={topicsDiscussed || ''}
        readOnly={readOnly}
        onChange={(e) => !readOnly && dispatch(updateFormFields({ topics_discussed: e.target.value }))}
        rows={3}
      />
    </div>
  )
}

export default TopicsField
