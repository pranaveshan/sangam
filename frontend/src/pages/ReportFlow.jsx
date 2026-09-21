import { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useI18n } from '../context/i18n';
import { useVoiceInput, speakText } from '../hooks/useVoiceInput';
import { problemsAPI } from '../utils/api';
import { isOnline, queueReport } from '../utils/offlineQueue';
import useStore from '../context/store';
import DemoBadge from '../components/shared/DemoBadge';

const STEPS = ['collect', 'followup', 'confirm', 'done'];

export default function ReportFlow() {
  const { t, speechCode, lang } = useI18n();
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const { currentUser, authToken, setLastSubmission } = useStore();

  const initialMode = params.get('mode') || 'speak';
  const [step, setStep] = useState('collect');
  const [mode, setMode] = useState(initialMode);
  const [text, setText] = useState('');
  const [location, setLocation] = useState('');
  const [people, setPeople] = useState('');
  const [photo, setPhoto] = useState(null);
  const [photoPreview, setPhotoPreview] = useState(null);
  const [assisted, setAssisted] = useState(false);
  const [consent, setConsent] = useState(true);
  const [analysis, setAnalysis] = useState(null);
  const [edits, setEdits] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [offlineNote, setOfflineNote] = useState(null);
  const [followUps, setFollowUps] = useState([]);

  const voice = useVoiceInput(speechCode);

  useEffect(() => {
    if (voice.transcript) setText(voice.transcript);
  }, [voice.transcript]);

  const combinedText = useMemo(() => {
    const parts = [text.trim()];
    if (location.trim()) parts.push(`Location: ${location.trim()}`);
    if (people.trim()) parts.push(`People affected: ${people.trim()}`);
    return parts.filter(Boolean).join('\n');
  }, [text, location, people]);

  const onPhoto = (file) => {
    setPhoto(file || null);
    if (photoPreview) URL.revokeObjectURL(photoPreview);
    setPhotoPreview(file ? URL.createObjectURL(file) : null);
  };

  const useGps = () => {
    if (!navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLocation((prev) =>
          prev
            ? `${prev} (${pos.coords.latitude.toFixed(4)}, ${pos.coords.longitude.toFixed(4)})`
            : `GPS ${pos.coords.latitude.toFixed(4)}, ${pos.coords.longitude.toFixed(4)}`
        );
      },
      () => {},
      { enableHighAccuracy: true, timeout: 10000 }
    );
  };

  const goAnalyze = async () => {
    if (!text.trim() && !photo) {
      setError(t('report.descriptionPlaceholder'));
      return;
    }
    setError(null);
    setLoading(true);
    try {
      const missing = [];
      if (!location.trim()) missing.push('location');
      if (!people.trim()) missing.push('people');
      if (missing.length && step === 'collect') {
        setFollowUps(missing);
        setStep('followup');
        setLoading(false);
        return;
      }

      if (!isOnline()) {
        const queued = await queueReport({
          text: combinedText,
          location,
          people,
          lang,
          assisted,
          hasPhoto: Boolean(photo),
        });
        setOfflineNote(t('report.offlineSaved'));
        setResult({ queued: true, id: queued.id });
        setStep('done');
        setLoading(false);
        return;
      }

      const res = await problemsAPI.analyze({
        text: combinedText,
        language: lang,
        location_text: location || undefined,
        people_affected_text: people || undefined,
        has_photo: Boolean(photo),
        has_video: Boolean(photo && photo.type?.startsWith('video')),
      });
      setAnalysis(res.data);
      setEdits({
        problem_title: res.data.problem_title || '',
        summary: res.data.summary || '',
        location: res.data.location?.text || location || '',
        social_impact: res.data.social_impact || '',
        category: res.data.category || '',
      });
      setStep('confirm');
    } catch (e) {
      // Honest fallback — still allow manual confirm path
      setAnalysis({
        ai_unavailable: true,
        problem_title: text.slice(0, 80) || 'Community problem',
        summary: text || 'Citizen report pending analysis',
        category: '',
        severity: '',
        urgency: '',
        location: { text: location, confidence: location ? 0.5 : 0 },
        required_expertise: [],
        missing_information: ['AI analysis unavailable'],
        confidence: 0,
        message: t('report.aiUnavailable'),
      });
      setEdits({
        problem_title: text.slice(0, 80) || 'Community problem',
        summary: text,
        location,
        social_impact: '',
        category: '',
      });
      setStep('confirm');
    } finally {
      setLoading(false);
    }
  };

  const onFollowupContinue = () => {
    setStep('collect');
    goAnalyze();
  };

  const submitConfirmed = async () => {
    if (assisted && !consent) {
      setError(t('report.consent'));
      return;
    }
    setLoading(true);
    setError(null);
    try {
      if (!isOnline()) {
        const queued = await queueReport({
          ...edits,
          text: combinedText,
          analysis,
          assisted,
          lang,
        });
        setOfflineNote(t('report.offlineSaved'));
        setResult({ queued: true, id: queued.id });
        setStep('done');
        return;
      }

      const form = new FormData();
      form.append('title', edits.problem_title || 'Community problem');
      form.append('description', edits.summary || text);
      form.append('category', edits.category || analysis?.category || 'Community');
      form.append('location', edits.location || location || 'Not specified');
      form.append('district', analysis?.district || 'Unknown');
      form.append('community_impact', edits.social_impact || analysis?.social_impact || 'To be assessed');
      form.append('people_affected', String(parseInt(people, 10) || analysis?.affected_population_estimate || 0));
      form.append('urgency', analysis?.urgency || 'medium');
      form.append('severity', analysis?.severity || 'medium');
      form.append('language', lang);
      form.append('original_transcript', text);
      form.append('submitted_with_assistance', String(assisted));
      form.append('citizen_consent', String(consent));
      if (currentUser?.id) form.append('reporter_id', String(currentUser.id));
      if (analysis) form.append('intelligence_json', JSON.stringify(analysis));
      if (photo) form.append('photo', photo);

      const headers = {};
      if (authToken) headers.Authorization = `Bearer ${authToken}`;

      const res = await problemsAPI.create(form, headers);
      setResult(res.data);
      setLastSubmission(res.data);
      setStep('done');
    } catch (e) {
      try {
        await queueReport({ edits, text: combinedText, analysis, assisted, lang });
        setOfflineNote(t('report.offlineSaved'));
        setResult({ queued: true });
        setStep('done');
      } catch {
        setError(t('common.error'));
      }
    } finally {
      setLoading(false);
    }
  };

  const listenSummary = () => {
    const say = [
      edits.problem_title,
      edits.summary,
      edits.location ? `Location: ${edits.location}` : '',
    ].filter(Boolean).join('. ');
    speakText(say, speechCode);
  };

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="font-display text-3xl font-bold text-sangam-ink">{t('report.title')}</h1>
      <p className="mt-2 text-slate-600">{t('report.subtitle')}</p>

      {step === 'collect' && (
        <div className="mt-8 space-y-6">
          <div className="grid grid-cols-3 gap-2" role="tablist" aria-label="Report mode">
            {[
              { id: 'speak', label: t('report.speak') },
              { id: 'show', label: t('report.show') },
              { id: 'type', label: t('report.type') },
            ].map((m) => (
              <button
                key={m.id}
                type="button"
                role="tab"
                aria-selected={mode === m.id}
                className={`min-h-[48px] rounded-xl font-semibold border ${
                  mode === m.id
                    ? 'bg-sangam-uni text-white border-sangam-uni'
                    : 'bg-white border-slate-200 text-slate-700'
                }`}
                onClick={() => setMode(m.id)}
              >
                {m.label}
              </button>
            ))}
          </div>

          {(mode === 'speak' || mode === 'type') && (
            <div className="panel p-5">
              {mode === 'speak' && (
                <div className="flex flex-col items-center gap-4 mb-6">
                  {!voice.supported && (
                    <p className="text-sm text-amber-800 text-center">{t('report.speechUnsupported')}</p>
                  )}
                  <button
                    type="button"
                    onClick={voice.toggle}
                    disabled={!voice.supported}
                    className={`w-28 h-28 rounded-full text-white text-3xl font-bold shadow-panel focus-visible:ring-4 focus-visible:ring-teal-300 ${
                      voice.listening ? 'bg-rose-600 animate-pulse' : 'bg-sangam-uni'
                    }`}
                    aria-pressed={voice.listening}
                    aria-label={voice.listening ? t('report.listening') : t('report.tapToSpeak')}
                  >
                    🎙️
                  </button>
                  <p className="text-sm text-slate-600">
                    {voice.listening ? t('report.listening') : t('report.tapToSpeak')}
                  </p>
                </div>
              )}
              <label className="label" htmlFor="report-text">{t('report.transcript')}</label>
              <textarea
                id="report-text"
                className="input min-h-[140px]"
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder={t('report.descriptionPlaceholder')}
              />
              {voice.interim && (
                <p className="text-sm text-slate-400 mt-2 italic">{voice.interim}</p>
              )}
            </div>
          )}

          {(mode === 'show' || photo) && (
            <div className="panel p-5">
              <label className="label" htmlFor="report-photo">{t('report.photo')}</label>
              <p className="text-xs text-slate-500 mb-2">{t('report.photoHint')}</p>
              <input
                id="report-photo"
                type="file"
                accept="image/*,video/*"
                className="input"
                onChange={(e) => onPhoto(e.target.files?.[0])}
              />
              {photoPreview && photo?.type?.startsWith('image') && (
                <img src={photoPreview} alt="Evidence preview" className="mt-3 rounded-lg max-h-48 object-cover" />
              )}
            </div>
          )}

          <div className="panel p-5 space-y-4">
            <div>
              <label className="label" htmlFor="loc">{t('report.location')}</label>
              <p className="text-xs text-slate-500 mb-2">{t('report.locationHint')}</p>
              <div className="flex gap-2">
                <input
                  id="loc"
                  className="input"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                />
                <button type="button" className="btn-secondary shrink-0" onClick={useGps}>
                  {t('report.useGps')}
                </button>
              </div>
            </div>
            <div>
              <label className="label" htmlFor="people">{t('report.peopleAffected')}</label>
              <input
                id="people"
                className="input"
                inputMode="numeric"
                value={people}
                onChange={(e) => setPeople(e.target.value)}
              />
            </div>
            <label className="flex items-start gap-3 text-sm">
              <input
                type="checkbox"
                className="mt-1 w-5 h-5"
                checked={assisted}
                onChange={(e) => setAssisted(e.target.checked)}
              />
              <span>{t('report.assisted')}</span>
            </label>
            {assisted && (
              <label className="flex items-start gap-3 text-sm">
                <input
                  type="checkbox"
                  className="mt-1 w-5 h-5"
                  checked={consent}
                  onChange={(e) => setConsent(e.target.checked)}
                />
                <span>{t('report.consent')}</span>
              </label>
            )}
          </div>

          {error && <p className="text-rose-700 text-sm" role="alert">{error}</p>}

          <button
            type="button"
            className="btn-primary w-full min-h-[52px] text-base"
            onClick={goAnalyze}
            disabled={loading}
          >
            {loading ? t('report.understanding') : t('report.continue')}
          </button>
        </div>
      )}

      {step === 'followup' && (
        <div className="mt-8 panel p-6 space-y-5">
          {followUps.includes('location') && (
            <div>
              <label className="label" htmlFor="fu-loc">{t('report.followUpLocation')}</label>
              <input id="fu-loc" className="input" value={location} onChange={(e) => setLocation(e.target.value)} />
            </div>
          )}
          {followUps.includes('people') && (
            <div>
              <label className="label" htmlFor="fu-people">{t('report.followUpPeople')}</label>
              <input id="fu-people" className="input" value={people} onChange={(e) => setPeople(e.target.value)} />
            </div>
          )}
          <div className="flex gap-3">
            <button type="button" className="btn-secondary" onClick={() => { setFollowUps([]); setStep('collect'); }}>
              {t('report.back')}
            </button>
            <button type="button" className="btn-primary flex-1" onClick={onFollowupContinue} disabled={loading}>
              {loading ? t('report.understanding') : t('report.continue')}
            </button>
          </div>
        </div>
      )}

      {step === 'confirm' && analysis && (
        <div className="mt-8 space-y-5">
          <h2 className="font-display text-2xl font-bold">{t('report.understood')}</h2>
          {analysis.ai_unavailable && (
            <p className="text-amber-900 bg-amber-50 border border-amber-200 rounded-lg px-4 py-3 text-sm">
              {analysis.message || t('report.aiUnavailable')}
            </p>
          )}

          <div className="panel p-5 space-y-4">
            <Field label={t('report.problem')} value={edits.problem_title} onChange={(v) => setEdits({ ...edits, problem_title: v })} />
            <Field label={t('report.understood')} value={edits.summary} onChange={(v) => setEdits({ ...edits, summary: v })} multiline />
            <Field label={t('report.location')} value={edits.location} onChange={(v) => setEdits({ ...edits, location: v })} />
            <Field label={t('report.impact')} value={edits.social_impact} onChange={(v) => setEdits({ ...edits, social_impact: v })} multiline />
            <Field label={t('report.category')} value={edits.category} onChange={(v) => setEdits({ ...edits, category: v })} />
          </div>

          {analysis.required_expertise?.length > 0 && (
            <div>
              <p className="text-sm font-semibold mb-2">{t('report.expertise')}</p>
              <div className="flex flex-wrap gap-2">
                {analysis.required_expertise.map((e) => (
                  <span key={e} className="badge bg-teal-50 text-teal-900 border border-teal-100">{e}</span>
                ))}
              </div>
            </div>
          )}

          {analysis.missing_information?.length > 0 && (
            <div className="text-sm text-slate-600">
              <p className="font-semibold">{t('report.missing')}</p>
              <ul className="list-disc ml-5 mt-1">
                {analysis.missing_information.map((m) => <li key={m}>{m}</li>)}
              </ul>
            </div>
          )}

          <div className="flex flex-wrap gap-3">
            <button type="button" className="btn-secondary" onClick={listenSummary}>{t('report.listen')}</button>
            <button type="button" className="btn-secondary" onClick={() => setStep('collect')}>{t('report.correct')}</button>
            <button type="button" className="btn-primary flex-1 min-h-[48px]" onClick={submitConfirmed} disabled={loading}>
              {loading ? t('common.loading') : t('report.confirm')}
            </button>
          </div>
          {error && <p className="text-rose-700 text-sm">{error}</p>}
        </div>
      )}

      {step === 'done' && (
        <div className="mt-8 panel p-6 space-y-4">
          <h2 className="font-display text-2xl font-bold text-teal-900">{t('report.success')}</h2>
          {offlineNote && (
            <p className="text-amber-900 bg-amber-50 border border-amber-200 rounded-lg px-4 py-3 text-sm">
              {offlineNote} · {t('report.pendingSync')}
            </p>
          )}
          {assisted ? (
            <p className="text-sm font-medium">{t('report.submittedWithAssistance')}</p>
          ) : (
            <p className="text-sm font-medium">{t('report.reportedByCitizen')}</p>
          )}

          {result?.similar?.length > 0 && (
            <div>
              <h3 className="font-semibold mb-2">{t('report.related')}</h3>
              <ul className="space-y-2 text-sm">
                {result.similar.map((s) => (
                  <li key={s.id} className="border border-slate-200 rounded-lg p-3">
                    {s.title} · {s.relation || s.recommended_action} ({s.similarity}%)
                  </li>
                ))}
              </ul>
            </div>
          )}

          {result?.matches?.length > 0 && (
            <div>
              <h3 className="font-semibold mb-2">{t('report.collaborators')}</h3>
              <ul className="space-y-2">
                {result.matches.map((m) => (
                  <li key={m.university_id} className="border border-slate-200 rounded-lg p-3 text-sm">
                    <div className="flex gap-2 items-center">
                      <span className="font-semibold">{m.university_name}</span>
                      {m.is_demo && <DemoBadge label={t('common.demoData')} tone="amber" />}
                    </div>
                    <p className="text-slate-600 mt-1">{t('report.whyMatch')} {m.explanation}</p>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="flex flex-wrap gap-3 pt-2">
            {result?.challenge?.id || result?.id ? (
              <Link
                to={`/explore/${result.challenge?.id || result.id}`}
                className="btn-primary"
              >
                {t('explore.viewDetails')}
              </Link>
            ) : null}
            <button type="button" className="btn-secondary" onClick={() => navigate('/')}>
              {t('nav.home')}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function Field({ label, value, onChange, multiline }) {
  const Comp = multiline ? 'textarea' : 'input';
  return (
    <div>
      <label className="label">{label}</label>
      <Comp
        className={`input ${multiline ? 'min-h-[100px]' : ''}`}
        value={value || ''}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
}
