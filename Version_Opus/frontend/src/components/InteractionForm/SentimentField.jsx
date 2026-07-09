import { useSelector, useDispatch } from 'react-redux'
import { updateFormFields } from '../../store/formSlice'

const sentimentOptions = [
  { value: 'positive', emoji: '😊', label: 'Positive' },
  { value: 'neutral', emoji: '😐', label: 'Neutral' },
  { value: 'negative', emoji: '😟', label: 'Negative' },
]

function SentimentField({ readOnly }) {
  const sentiment = useSelector(state => state.form.sentiment)
  const dispatch = useDispatch()

  const handleClick = (value) => {
    if (!readOnly) {
      dispatch(updateFormFields({ sentiment: value }))
    }
  }

  return (
    <div className="form-field">
      <label className="form-field__label">Observed/Inferred HCP Sentiment</label>
      <div className="sentiment-group">
        {sentimentOptions.map(option => (
          <div
            key={option.value}
            className={`sentiment-option sentiment-option--${option.value} ${
              sentiment === option.value ? 'sentiment-option--active' : ''
            } ${!readOnly ? 'sentiment-option--editable' : ''}`}
            onClick={() => handleClick(option.value)}
          >
            <div className="sentiment-option__radio" />
            <span className="sentiment-option__emoji">{option.emoji}</span>
            <span className="sentiment-option__label">{option.label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default SentimentField
