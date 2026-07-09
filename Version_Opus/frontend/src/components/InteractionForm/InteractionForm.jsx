import { useState } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { resetForm } from '../../store/formSlice'
import { submitInteraction } from '../../services/api'
import TopicsField from './TopicsField'
import MaterialsField from './MaterialsField'
import SamplesField from './SamplesField'
import SentimentField from './SentimentField'
import OutcomesField from './OutcomesField'
import FollowUpField from './FollowUpField'
import './InteractionForm.css'

function InteractionForm() {
  const formState = useSelector(state => state.form)
  const dispatch = useDispatch()
  const [manualEditEnabled, setManualEditEnabled] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitMessage, setSubmitMessage] = useState(null)

  const handleSubmit = async () => {
    if (!formState.interaction_id) {
      setSubmitMessage({ type: 'error', text: 'No interaction to submit. Use the AI assistant to log an interaction first.' })
      return
    }
    setIsSubmitting(true)
    try {
      const result = await submitInteraction(formState)
      if (result.success) {
        setSubmitMessage({ type: 'success', text: 'Interaction submitted successfully!' })
      } else {
        setSubmitMessage({ type: 'error', text: result.message || 'Failed to submit' })
      }
    } catch (err) {
      setSubmitMessage({ type: 'error', text: 'Error submitting interaction' })
    } finally {
      setIsSubmitting(false)
      setTimeout(() => setSubmitMessage(null), 3000)
    }
  }

  const handleReset = () => {
    dispatch(resetForm())
    setSubmitMessage(null)
  }

  return (
    <div className="interaction-form">
      <div className="interaction-form__header">
        <div className="interaction-form__title-group">
          <h1 className="interaction-form__title">Interaction Details</h1>
          {formState.hcp_name && (
            <span className="interaction-form__hcp-badge">
              👤 {formState.hcp_name}
              {formState.interaction_date && (
                <span className="interaction-form__date"> · {formState.interaction_date}</span>
              )}
            </span>
          )}
        </div>
        <div className="interaction-form__controls">
          <label className="toggle-switch">
            <input
              type="checkbox"
              checked={manualEditEnabled}
              onChange={(e) => setManualEditEnabled(e.target.checked)}
            />
            <span className="toggle-switch__slider" />
            <span className="toggle-switch__label">
              {manualEditEnabled ? '✏️ Manual Edit' : '🔒 AI Only'}
            </span>
          </label>
        </div>
      </div>

      <div className="interaction-form__fields">
        <TopicsField readOnly={!manualEditEnabled} />
        
        <div className="interaction-form__section-divider">
          <span>Materials Shared / Samples Distributed</span>
        </div>
        
        <MaterialsField readOnly={!manualEditEnabled} />
        <SamplesField readOnly={!manualEditEnabled} />
        <SentimentField readOnly={!manualEditEnabled} />
        <OutcomesField readOnly={!manualEditEnabled} />
        <FollowUpField readOnly={!manualEditEnabled} />
      </div>

      <div className="interaction-form__actions">
        {submitMessage && (
          <div className={`interaction-form__message interaction-form__message--${submitMessage.type}`}>
            {submitMessage.text}
          </div>
        )}
        <div className="interaction-form__buttons">
          <button 
            className="btn btn--secondary" 
            onClick={handleReset}
            type="button"
          >
            Reset Form
          </button>
          <button
            className="btn btn--primary"
            onClick={handleSubmit}
            disabled={isSubmitting || !formState.interaction_id}
            type="button"
          >
            {isSubmitting ? 'Submitting...' : '📤 Submit Interaction'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default InteractionForm
