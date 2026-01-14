// TourBuddy AI – Simple Web UI (vanilla)

// Recording state
let recStream = null;
let recChunks = [];
let recMedia = null;
let recBlob = null;
let recWavBlob = null;
let recCtx = null;

function getAPI() {
  const input = document.getElementById('apiBase');
  return (input?.value || '').replace(/\/$/, '');
}

function setText(id, text, isError = false) {
  const el = document.getElementById(id);
  if (el) {
    el.textContent = typeof text === 'string' ? text : JSON.stringify(text, null, 2);
    el.classList.toggle('error', !!isError);
  }
}

function showToast(message, ok = true) {
  const cont = document.getElementById('toast');
  if (!cont) return;
  const div = document.createElement('div');
  div.className = 'toast ' + (ok ? 'ok' : 'err');
  div.textContent = message;
  cont.appendChild(div);
  setTimeout(() => { div.remove(); }, 3500);
}

function setAudio(id, url) {
  const audio = document.getElementById(id);
  if (!audio) return;
  if (url) {
    audio.src = url;
    audio.classList.remove('hidden');
  } else {
    audio.removeAttribute('src');
    audio.classList.add('hidden');
  }
}

function addOperationStatus(tabId, type, message) {
  // Remove existing status
  const existing = document.querySelector(`[data-panel="${tabId}"] .operation-status`);
  if (existing) existing.remove();
  
  // Add new status
  const panel = document.querySelector(`[data-panel="${tabId}"]`);
  if (panel) {
    const status = document.createElement('div');
    status.className = `operation-status ${type}`;
    status.textContent = message;
    const output = panel.querySelector('.output');
    if (output) {
      output.parentNode.insertBefore(status, output);
    }
  }
}

function getLanguageName(code) {
  const names = {
    'en': 'English',
    'hi': 'Hindi', 
    'te': 'Telugu',
    'kn': 'Kannada'
  };
  return names[code] || code;
}

function spinner(busy) {
  const sp = document.getElementById('spinner');
  if (!sp) return;
  sp.classList.toggle('hidden', !busy);
}

async function fetchJSON(url, data) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  const text = await res.text();
  try {
    const json = JSON.parse(text);
    if (!res.ok) throw json;
    return json;
  } catch (e) {
    throw text || e;
  }
}

async function fetchForm(url, formData) {
  const res = await fetch(url, { method: 'POST', body: formData });
  const text = await res.text();
  try {
    const json = JSON.parse(text);
    if (!res.ok) throw json;
    return json;
  } catch (e) {
    throw text || e;
  }
}

function on(id, ev, fn) {
  const el = document.getElementById(id);
  if (el) el.addEventListener(ev, fn);
}

function wireDropzone(zoneId, fileInputId) {
  const zone = document.getElementById(zoneId);
  const input = document.getElementById(fileInputId);
  if (!zone || !input) return;
  ['dragenter','dragover'].forEach(ev => zone.addEventListener(ev, e => { e.preventDefault(); zone.classList.add('drag'); }));
  ;['dragleave','drop'].forEach(ev => zone.addEventListener(ev, e => { e.preventDefault(); zone.classList.remove('drag'); }));
  zone.addEventListener('drop', e => {
    const f = e.dataTransfer?.files?.[0];
    if (f) input.files = e.dataTransfer.files;
  });
}

function switchTab(tab) {
  document.querySelectorAll('.tab').forEach(b => b.classList.toggle('active', b.dataset.tab === tab));
  document.querySelectorAll('[data-panel]').forEach(p => p.classList.toggle('hidden', p.dataset.panel !== tab));
}

function setHealth(ok) {
  const dot = document.getElementById('healthDot');
  const text = document.getElementById('healthStatus');
  if (dot) { dot.classList.toggle('dot--ok', !!ok); dot.classList.toggle('dot--bad', !ok); }
  if (text) { text.textContent = ok ? 'OK' : 'Unavailable'; }
}

async function checkHealth() {
  const base = getAPI();
  try {
    const res = await fetch(base + '/health');
    await res.json().catch(()=>({}));
    setHealth(true);
    showToast('Backend healthy', true);
  } catch (e) {
    setHealth(false);
    showToast('Backend unavailable', false);
  }
}

function withBusy(el, busy = true) {
  if (!el) return;
  el.disabled = !!busy;
}

function encodeWavPCM16(audioBuffer, targetSampleRate = 16000) {
  // Resample to mono 16k using OfflineAudioContext
  const channels = 1;
  const duration = audioBuffer.duration;
  const length = Math.floor(targetSampleRate * duration);
  const offline = new (window.OfflineAudioContext || window.webkitOfflineAudioContext)(channels, length, targetSampleRate);
  // Mixdown: connect bufferSource to offline destination (automatic channel mix)
  const bufferSource = offline.createBufferSource();
  bufferSource.buffer = audioBuffer;
  bufferSource.connect(offline.destination);
  bufferSource.start(0);
  return offline.startRendering().then(rendered => {
    const chData = rendered.getChannelData(0);
    // PCM16 encoding
    const wavBuffer = new ArrayBuffer(44 + chData.length * 2);
    const view = new DataView(wavBuffer);
    // RIFF header
    function writeString(off, s){ for (let i=0;i<s.length;i++) view.setUint8(off+i, s.charCodeAt(i)); }
    writeString(0, 'RIFF');
    view.setUint32(4, 36 + chData.length * 2, true);
    writeString(8, 'WAVE');
    writeString(12, 'fmt ');
    view.setUint32(16, 16, true); // PCM chunk size
    view.setUint16(20, 1, true);  // audio format PCM
    view.setUint16(22, 1, true);  // channels
    view.setUint32(24, targetSampleRate, true);
    view.setUint32(28, targetSampleRate * 2, true); // byte rate
    view.setUint16(32, 2, true);  // block align
    view.setUint16(34, 16, true); // bits per sample
    writeString(36, 'data');
    view.setUint32(40, chData.length * 2, true);
    let offset = 44;
    for (let i=0;i<chData.length;i++) {
      let s = Math.max(-1, Math.min(1, chData[i]));
      view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
      offset += 2;
    }
    return new Blob([view], { type: 'audio/wav' });
  });
}

async function startRecording() {
  try {
    recStream = await navigator.mediaDevices.getUserMedia({ audio: true });
  } catch (e) {
    showToast('Mic permission denied', false);
    return;
  }
  recChunks = [];
  recMedia = new MediaRecorder(recStream, { mimeType: 'audio/webm' });
  recMedia.ondataavailable = e => { if (e.data && e.data.size) recChunks.push(e.data) };
  recMedia.onstop = async () => {
    recBlob = new Blob(recChunks, { type: 'audio/webm' });
    try {
      const arrayBuf = await recBlob.arrayBuffer();
      recCtx = recCtx || new (window.AudioContext || window.webkitAudioContext)();
      const audioBuffer = await recCtx.decodeAudioData(arrayBuf.slice(0));
      recWavBlob = await encodeWavPCM16(audioBuffer, 16000);
      // preview
      const url = URL.createObjectURL(recWavBlob);
      const prev = document.getElementById('recPreview');
      if (prev) { prev.src = url; prev.classList.remove('hidden'); }
      // enable Use
      document.getElementById('recUse')?.removeAttribute('disabled');
      document.getElementById('recStatus').textContent = 'Recorded';
    } catch (e) {
      showToast('Failed to process audio', false);
      document.getElementById('recStatus').textContent = 'Error';
    }
    // stop tracks
    recStream.getTracks().forEach(t => t.stop());
    recStream = null;
  };
  recMedia.start(50);
  document.getElementById('recStart')?.setAttribute('disabled','true');
  document.getElementById('recStop')?.removeAttribute('disabled');
  document.getElementById('recStatus').textContent = 'Recording...';
}

function stopRecording() {
  try { recMedia && recMedia.state !== 'inactive' && recMedia.stop(); } catch {}
  document.getElementById('recStop')?.setAttribute('disabled','true');
  document.getElementById('recStart')?.removeAttribute('disabled');
  document.getElementById('recStatus').textContent = 'Processing...';
}

function useRecording() {
  if (!recWavBlob) { showToast('No recording', false); return }
  const file = new File([recWavBlob], 'recording.wav', { type: 'audio/wav' });
  // place into file input
  const dt = new DataTransfer();
  dt.items.add(file);
  const input = document.getElementById('asr_file');
  if (input) input.files = dt.files;
  showToast('Recording loaded');
}

// Voice Translate recording functions
let voiceRecStream = null;
let voiceRecChunks = [];
let voiceRecMedia = null;
let voiceRecBlob = null;
let voiceRecWavBlob = null;

async function startVoiceRecording() {
  try {
    voiceRecStream = await navigator.mediaDevices.getUserMedia({ audio: true });
  } catch (e) {
    showToast('Mic permission denied', false);
    return;
  }
  voiceRecChunks = [];
  voiceRecMedia = new MediaRecorder(voiceRecStream, { mimeType: 'audio/webm' });
  voiceRecMedia.ondataavailable = e => { if (e.data && e.data.size) voiceRecChunks.push(e.data) };
  voiceRecMedia.onstop = async () => {
    voiceRecBlob = new Blob(voiceRecChunks, { type: 'audio/webm' });
    try {
      const arrayBuf = await voiceRecBlob.arrayBuffer();
      const audioCtx = recCtx || new (window.AudioContext || window.webkitAudioContext)();
      const audioBuffer = await audioCtx.decodeAudioData(arrayBuf.slice(0));
      voiceRecWavBlob = await encodeWavPCM16(audioBuffer, 16000);
      // preview
      const url = URL.createObjectURL(voiceRecWavBlob);
      const prev = document.getElementById('voiceRecPreview');
      if (prev) { prev.src = url; prev.classList.remove('hidden'); }
      // enable Use
      document.getElementById('voiceRecUse')?.removeAttribute('disabled');
      document.getElementById('voiceRecStatus').textContent = 'Recorded';
    } catch (e) {
      showToast('Failed to process audio', false);
      document.getElementById('voiceRecStatus').textContent = 'Error';
    }
    // stop tracks
    voiceRecStream.getTracks().forEach(t => t.stop());
    voiceRecStream = null;
  };
  voiceRecMedia.start(50);
  document.getElementById('voiceRecStart')?.setAttribute('disabled','true');
  document.getElementById('voiceRecStop')?.removeAttribute('disabled');
  document.getElementById('voiceRecStatus').textContent = 'Recording...';
}

function stopVoiceRecording() {
  try { voiceRecMedia && voiceRecMedia.state !== 'inactive' && voiceRecMedia.stop(); } catch {}
  document.getElementById('voiceRecStop')?.setAttribute('disabled','true');
  document.getElementById('voiceRecStart')?.removeAttribute('disabled');
  document.getElementById('voiceRecStatus').textContent = 'Processing...';
}

function useVoiceRecording() {
  if (!voiceRecWavBlob) { showToast('No recording', false); return }
  const file = new File([voiceRecWavBlob], 'voice_recording.wav', { type: 'audio/wav' });
  // place into file input
  const dt = new DataTransfer();
  dt.items.add(file);
  const input = document.getElementById('voice_file');
  if (input) input.files = dt.files;
  showToast('Voice recording loaded');
}

// Wire up events
window.addEventListener('DOMContentLoaded', () => {
  // Tabs
  document.querySelectorAll('.tab').forEach(btn => btn.addEventListener('click', () => switchTab(btn.dataset.tab)));
  switchTab('mt');

  document.querySelectorAll('[data-quick-tab]').forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.dataset.quickTab;
      if (!target) return;
      switchTab(target);
      const panel = document.querySelector(`[data-panel="${target}"]`);
      if (panel) panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });

  // Dropzones
  wireDropzone('asr_drop', 'asr_file');
  wireDropzone('voice_drop', 'voice_file');
  wireDropzone('image_voice_drop', 'image_voice_file');

  // Recorder controls
  const rs = document.getElementById('recStart'); if (rs) rs.addEventListener('click', startRecording);
  const rp = document.getElementById('recStop'); if (rp) rp.addEventListener('click', stopRecording);
  const ru = document.getElementById('recUse'); if (ru) ru.addEventListener('click', useRecording);
  
  // Voice Translate recorder controls
  const vrs = document.getElementById('voiceRecStart'); if (vrs) vrs.addEventListener('click', startVoiceRecording);
  const vrp = document.getElementById('voiceRecStop'); if (vrp) vrp.addEventListener('click', stopVoiceRecording);
  const vru = document.getElementById('voiceRecUse'); if (vru) vru.addEventListener('click', useVoiceRecording);
  wireDropzone('img_drop', 'ocr_file');
  wireDropzone('sum_drop', 'sumocr_file');

  // Health
  on('btnHealth', 'click', checkHealth);
  checkHealth();

  // Counters & file info
  const mtIn = document.getElementById('mt_input');
  if (mtIn) mtIn.addEventListener('input', ()=>{
    const words = (mtIn.value || '').trim().split(/\s+/).filter(Boolean).length;
    const el = document.getElementById('mt_count');
    if (el) el.textContent = String(words);
  });

  const ttsIn = document.getElementById('tts_input');
  if (ttsIn) ttsIn.addEventListener('input', ()=>{
    const words = (ttsIn.value || '').trim().split(/\s+/).filter(Boolean).length;
    const el = document.getElementById('tts_count');
    if (el) el.textContent = String(words);
  });

  const asrFile = document.getElementById('asr_file');
  if (asrFile) asrFile.addEventListener('change', ()=>{
    const f = asrFile.files?.[0];
    showToast(f ? `Selected: ${f.name}` : 'No file');
  });

  const ocrFile = document.getElementById('ocr_file');
  if (ocrFile) ocrFile.addEventListener('change', ()=>{
    const f = ocrFile.files?.[0];
    showToast(f ? `Selected: ${f.name}` : 'No file');
  });

  const sumFile = document.getElementById('sumocr_file');
  if (sumFile) sumFile.addEventListener('change', ()=>{
    const f = sumFile.files?.[0];
    showToast(f ? `Selected: ${f.name}` : 'No file');
  });

  // Voice Translate file input
  const voiceFile = document.getElementById('voice_file');
  if (voiceFile) voiceFile.addEventListener('change', ()=>{
    const f = voiceFile.files?.[0];
    showToast(f ? `Voice file selected: ${f.name}` : 'No voice file');
  });

  // Image to Voice file input
  const imageVoiceFile = document.getElementById('image_voice_file');
  if (imageVoiceFile) imageVoiceFile.addEventListener('change', ()=>{
    const f = imageVoiceFile.files?.[0];
    showToast(f ? `Image selected: ${f.name}` : 'No image file');
  });

  // Copy buttons for other outputs
  on('btnASRCopy', 'click', async ()=>{
    const t = document.getElementById('asr_output')?.textContent?.trim() || '';
    if (!t) return showToast('Nothing to copy', false);
    try { await navigator.clipboard.writeText(t); showToast('Copied') } catch { showToast('Copy failed', false) }
  });
  on('btnOCRCopy', 'click', async ()=>{
    const t = document.getElementById('ocr_output')?.textContent?.trim() || '';
    if (!t) return showToast('Nothing to copy', false);
    try { await navigator.clipboard.writeText(t); showToast('Copied') } catch { showToast('Copy failed', false) }
  });
  on('btnItiCopy', 'click', async ()=>{
    const t = document.getElementById('iti_output')?.textContent?.trim() || '';
    if (!t) return showToast('Nothing to copy', false);
    try { await navigator.clipboard.writeText(t); showToast('Copied') } catch { showToast('Copy failed', false) }
  });
  on('btnItiTranCopy', 'click', async ()=>{
    const txt = document.getElementById('iti_output')?.textContent || '';
    const idx = txt.indexOf('Translated:');
    const t = idx >= 0 ? txt.substring(idx + 'Translated:'.length).trim() : '';
    if (!t) return showToast('Nothing to copy', false);
    try { await navigator.clipboard.writeText(t); showToast('Copied') } catch { showToast('Copy failed', false) }
  });
  on('btnChatCopy', 'click', async ()=>{
    const t = document.getElementById('chat_output')?.textContent?.trim() || '';
    if (!t) return showToast('Nothing to copy', false);
    try { await navigator.clipboard.writeText(t); showToast('Copied') } catch { showToast('Copy failed', false) }
  });
  on('btnSumCopy', 'click', async ()=>{
    const t = document.getElementById('sum_output')?.textContent?.trim() || '';
    if (!t) return showToast('Nothing to copy', false);
    try { await navigator.clipboard.writeText(t); showToast('Copied') } catch { showToast('Copy failed', false) }
  });
  on('btnSumOCRCopy', 'click', async ()=>{
    const t = document.getElementById('sumocr_output')?.textContent?.trim() || '';
    if (!t) return showToast('Nothing to copy', false);
    try { await navigator.clipboard.writeText(t); showToast('Copied') } catch { showToast('Copy failed', false) }
  });

  on('btnMT', 'click', async (e) => {
    const btn = e.currentTarget; withBusy(btn, true); spinner(true);
    setText('mt_output', ''); addOperationStatus('mt', 'processing', 'Translating...');
    try {
      const text = document.getElementById('mt_input').value.trim();
      const sourceLang = document.getElementById('mt_source_lang').value;
      const targetLang = document.getElementById('mt_target_lang').value;
      
      if (!text) throw 'Please enter some text to translate.';
      
      const json = await fetchJSON(getAPI() + '/unified/text', {
        text: text,
        source_language: sourceLang,
        target_language: targetLang,
        output_type: 'text'
      });
      
      const el = document.getElementById('mt_output');
      if (el) { el.textContent = json.final_output || 'No translation received' }
      
      addOperationStatus('mt', 'success', json.message || 'Translation completed');
      showToast('Translated successfully');
    } catch (err) {
      setText('mt_output', err, true); 
      addOperationStatus('mt', 'error', 'Translation failed');
      showToast('Translation failed', false);
    } finally { withBusy(btn, false); spinner(false); }
  });

  on('btnMTCopy', 'click', async () => {
    const el = document.getElementById('mt_output');
    const text = el?.textContent?.trim() || '';
    if (!text) { showToast('Nothing to copy', false); return }
    try { await navigator.clipboard.writeText(text); showToast('Copied') } catch { showToast('Copy failed', false) }
  });

  on('btnTTS', 'click', async (e) => {
    const btn = e.currentTarget; withBusy(btn, true); spinner(true);
    setAudio('tts_audio', null);
    try {
      const text = document.getElementById('tts_input').value.trim();
      if (!text) throw 'Please enter some text to convert to speech.';
      
      const sourceLanguage = document.getElementById('tts_source_lang').value;
      const targetLanguage = document.getElementById('tts_target_lang').value;
      const gender = document.getElementById('tts_voice_gender').value;
      
      const json = await fetchJSON(getAPI() + '/unified/text', {
        text: text,
        source_language: sourceLanguage,
        target_language: targetLanguage,
        output_type: 'audio',
        gender: gender
      });
      
      let statusMessage = '';
      if (sourceLanguage === targetLanguage) {
        statusMessage = `Text-to-speech in ${getLanguageName(sourceLanguage)}`;
      } else {
        statusMessage = `Translation (${getLanguageName(sourceLanguage)} → ${getLanguageName(targetLanguage)}) + Text-to-speech`;
      }
      addOperationStatus('tts', 'success', statusMessage);
      
      if (json.final_output) {
        setAudio('tts_audio', json.final_output);
        showToast('Speech generated successfully');
      } else {
        throw 'No audio URL received';
      }
    } catch (err) {
      addOperationStatus('tts', 'error', 'Text-to-speech failed');
      showToast('TTS failed: ' + err, false);
    } finally { withBusy(btn, false); spinner(false); }
  });

  on('btnTTSDownload', 'click', async () => {
    const audio = document.getElementById('tts_audio');
    if (!audio.src) {
      showToast('No audio to download', false);
      return;
    }
    try {
      const a = document.createElement('a');
      a.href = audio.src;
      a.download = 'tts_audio.wav';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      showToast('Download started');
    } catch {
      showToast('Download failed', false);
    }
  });

  on('btnASR', 'click', async (e) => {
    const btn = e.currentTarget; withBusy(btn, true); spinner(true);
    setText('asr_output', '');
    try {
      const f = document.getElementById('asr_file').files?.[0];
      if (!f) throw 'Please select a WAV file.';
      
      const sourceLanguage = document.getElementById('asr_source_lang').value;
      const targetLanguage = document.getElementById('asr_target_lang').value;
      
      const fd = new FormData();
      fd.append('audio_file', f);
      fd.append('source_language', sourceLanguage);
      fd.append('target_language', targetLanguage);
      fd.append('output_type', 'text');
      
      const result = await fetchForm(getAPI() + '/unified/audio', fd);
      
      let statusMessage = '';
      if (sourceLanguage === targetLanguage) {
        statusMessage = `Speech-to-text in ${getLanguageName(sourceLanguage)}`;
      } else {
        statusMessage = `Speech-to-text (${getLanguageName(sourceLanguage)}) + Translation to ${getLanguageName(targetLanguage)}`;
      }
      
      setText('asr_output', result.final_output);
      addOperationStatus('speech', 'success', statusMessage);
      showToast('Speech converted to text successfully');
    } catch (err) {
      addOperationStatus('speech', 'error', 'Speech processing failed');
      setText('asr_output', err, true);
      showToast('Speech processing failed', false);
    }
    finally { withBusy(btn, false); spinner(false); }
  });

  // Voice Translate functionality
  on('btnVoiceTranslate', 'click', async (e) => {
    const btn = e.currentTarget; withBusy(btn, true); spinner(true);
    setText('voice_output', ''); setAudio('voice_audio', null);
    try {
      const f = document.getElementById('voice_file').files?.[0];
      if (!f) throw 'Please select a WAV file.';
      
      const sourceLanguage = document.getElementById('voice_source_lang').value;
      const targetLanguage = document.getElementById('voice_target_lang').value;
      const gender = document.getElementById('voice_gender').value;
      
      // Step 1: Get text (ASR + optional translation)
      const fd = new FormData();
      fd.append('audio_file', f);
      fd.append('source_language', sourceLanguage);
      fd.append('target_language', targetLanguage);
      fd.append('output_type', 'text');
      
      const textResult = await fetchForm(getAPI() + '/unified/audio', fd);
      const finalText = textResult.final_output;
      
      // Step 2: Convert text to speech in target language
      const languageMap = { 'en': 'english', 'hi': 'hindi', 'te': 'telugu', 'kn': 'kannada' };
      const ttsLanguage = languageMap[targetLanguage] || 'english';
      const ttsResult = await fetchJSON(getAPI() + `/tts/${ttsLanguage}`, {
        text: finalText,
        gender: gender
      });
      
      let statusMessage = '';
      if (sourceLanguage === targetLanguage) {
        statusMessage = `Speech-to-speech in ${getLanguageName(sourceLanguage)}`;
      } else {
        statusMessage = `Voice translation: ${getLanguageName(sourceLanguage)} → ${getLanguageName(targetLanguage)}`;
      }
      
      setText('voice_output', finalText + '\n\n[Audio generated in ' + getLanguageName(targetLanguage) + ']');
      setAudio('voice_audio', ttsResult.audio_url);
      addOperationStatus('voice-translate', 'success', statusMessage);
      showToast('Voice translation completed successfully');
    } catch (err) {
      addOperationStatus('voice-translate', 'error', 'Voice translation failed');
      setText('voice_output', err, true);
      showToast('Voice translation failed', false);
    }
    finally { withBusy(btn, false); spinner(false); }
  });

  // Voice copy and download
  on('btnVoiceCopy', 'click', async () => {
    const text = document.getElementById('voice_output')?.textContent?.replace(/\n\n\[Audio generated.*\]/, '').trim() || '';
    if (!text) { showToast('Nothing to copy', false); return }
    try { await navigator.clipboard.writeText(text); showToast('Copied') } catch { showToast('Copy failed', false) }
  });

  on('btnVoiceDownload', 'click', async () => {
    const audio = document.getElementById('voice_audio');
    if (!audio.src) {
      showToast('No audio to download', false);
      return;
    }
    try {
      const a = document.createElement('a');
      a.href = audio.src;
      a.download = 'voice_translation.wav';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      showToast('Download started');
    } catch {
      showToast('Download failed', false);
    }
  });


  on('btnOCR', 'click', async (e) => {
    const btn = e.currentTarget; withBusy(btn, true); spinner(true);
    setText('ocr_output', '');
    try {
      const f = document.getElementById('ocr_file').files?.[0];
      if (!f) throw 'Please select an image file (jpg/png).';
      
      const sourceLanguage = document.getElementById('ocr_source_lang').value;
      const targetLanguage = document.getElementById('ocr_target_lang').value;
      
      const fd = new FormData();
      fd.append('image_file', f);
      fd.append('source_language', sourceLanguage);
      fd.append('target_language', targetLanguage);
      fd.append('output_type', 'text');
      
      const result = await fetchForm(getAPI() + '/unified/image', fd);
      
      let statusMessage = '';
      if (sourceLanguage === targetLanguage) {
        statusMessage = `OCR in ${getLanguageName(sourceLanguage)}`;
      } else {
        statusMessage = `OCR (${getLanguageName(sourceLanguage)}) + Translation to ${getLanguageName(targetLanguage)}`;
      }
      
      setText('ocr_output', result.final_output);
      addOperationStatus('image', 'success', statusMessage);
      showToast('Text extracted from image successfully');
    } catch (err) {
      addOperationStatus('image', 'error', 'OCR failed');
      setText('ocr_output', err, true);
      showToast('OCR failed', false);
    }
    finally { withBusy(btn, false); spinner(false); }
  });

  // Image to Voice functionality
  on('btnImageVoice', 'click', async (e) => {
    const btn = e.currentTarget; withBusy(btn, true); spinner(true);
    setText('image_voice_output', ''); setAudio('image_voice_audio', null);
    try {
      const f = document.getElementById('image_voice_file').files?.[0];
      if (!f) throw 'Please select an image file (jpg/png).';
      
      const sourceLanguage = document.getElementById('image_voice_source_lang').value;
      const targetLanguage = document.getElementById('image_voice_target_lang').value;
      const gender = document.getElementById('image_voice_gender').value;
      
      // Step 1: Get text (OCR + optional translation)
      const fd = new FormData();
      fd.append('image_file', f);
      fd.append('source_language', sourceLanguage);
      fd.append('target_language', targetLanguage);
      fd.append('output_type', 'text');
      
      const textResult = await fetchForm(getAPI() + '/unified/image', fd);
      const finalText = textResult.final_output;
      
      // Step 2: Convert text to speech in target language
      const languageMap = { 'en': 'english', 'hi': 'hindi', 'te': 'telugu', 'kn': 'kannada' };
      const ttsLanguage = languageMap[targetLanguage] || 'english';
      const ttsResult = await fetchJSON(getAPI() + `/tts/${ttsLanguage}`, {
        text: finalText,
        gender: gender
      });
      
      let statusMessage = '';
      if (sourceLanguage === targetLanguage) {
        statusMessage = `OCR + Text-to-speech in ${getLanguageName(sourceLanguage)}`;
      } else {
        statusMessage = `Image text extraction (${getLanguageName(sourceLanguage)}) + Translation + TTS (${getLanguageName(targetLanguage)})`;
      }
      
      setText('image_voice_output', finalText + '\n\n[Audio generated in ' + getLanguageName(targetLanguage) + ']');
      setAudio('image_voice_audio', ttsResult.audio_url);
      addOperationStatus('image-voice', 'success', statusMessage);
      showToast('Image converted to voice successfully');
    } catch (err) {
      addOperationStatus('image-voice', 'error', 'Image to voice conversion failed');
      setText('image_voice_output', err, true);
      showToast('Image to voice conversion failed', false);
    }
    finally { withBusy(btn, false); spinner(false); }
  });

  // Image Voice copy and download
  on('btnImageVoiceCopy', 'click', async () => {
    const text = document.getElementById('image_voice_output')?.textContent?.replace(/\n\n\[Audio generated.*\]/, '').trim() || '';
    if (!text) { showToast('Nothing to copy', false); return }
    try { await navigator.clipboard.writeText(text); showToast('Copied') } catch { showToast('Copy failed', false) }
  });

  on('btnImageVoiceDownload', 'click', async () => {
    const audio = document.getElementById('image_voice_audio');
    if (!audio.src) {
      showToast('No audio to download', false);
      return;
    }
    try {
      const a = document.createElement('a');
      a.href = audio.src;
      a.download = 'image_to_voice.wav';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      showToast('Download started');
    } catch {
      showToast('Download failed', false);
    }
  });


  on('btnIti', 'click', async (e) => {
    const btn = e.currentTarget; withBusy(btn, true); spinner(true);
    setText('iti_output', ''); setAudio('iti_audio', null);
    try {
      const destination = document.getElementById('iti_destination').value.trim();
      const days = parseInt(document.getElementById('iti_days').value || '1', 10);
      const interests = document.getElementById('iti_interests').value.trim().split(',').map(s => s.trim()).filter(Boolean);
      const target_lang = document.getElementById('iti_target_lang').value.trim() || 'en';
      const speak = document.getElementById('iti_speak').checked;
      const json = await fetchJSON(getAPI() + '/itinerary/generate', { destination, days, interests, target_lang, speak });
      const combined = [
        json.itinerary ? json.itinerary : null,
        json.translated ? `\nTranslated:\n${json.translated}` : null
      ].filter(Boolean).join('\n') || JSON.stringify(json, null, 2)
      setText('iti_output', combined);
      if (json.tts_url) setAudio('iti_audio', json.tts_url);
      showToast('Itinerary ready');
    } catch (err) { setText('iti_output', err, true); showToast('Itinerary failed', false); }
    finally { withBusy(btn, false); spinner(false); }
  });

  on('btnChat', 'click', async (e) => {
    const btn = e.currentTarget; withBusy(btn, true); spinner(true);
    setText('chat_output', ''); setAudio('chat_audio', null);
    try {
      const content = document.getElementById('chat_text').value.trim();
      const target_lang = document.getElementById('chat_target_lang').value.trim() || 'en';
      const speak = document.getElementById('chat_speak').checked;
      const json = await fetchJSON(getAPI() + '/chat', { messages: [{ role: 'user', content }], target_lang, speak });
      const out = (json && json.reply) ? json.reply : JSON.stringify(json, null, 2)
      setText('chat_output', out);
      if (json.tts_url) setAudio('chat_audio', json.tts_url);
      showToast('Reply received');
    } catch (err) { setText('chat_output', err, true); showToast('Chat failed', false); }
    finally { withBusy(btn, false); spinner(false); }
  });

  on('btnSum', 'click', async (e) => {
    const btn = e.currentTarget; withBusy(btn, true); spinner(true);
    setText('sum_output', ''); setAudio('sum_audio', null);
    try {
      const text = document.getElementById('sum_text').value.trim();
      const target_lang = document.getElementById('sum_target_lang').value.trim() || 'en';
      const speak = document.getElementById('sum_speak').checked;
      const json = await fetchJSON(getAPI() + '/summarize/text', { text, target_lang, speak });
      const out = (json && (json.summary || json.translated)) ? (json.translated || json.summary) : JSON.stringify(json, null, 2)
      setText('sum_output', out);
      if (json.tts_url) setAudio('sum_audio', json.tts_url);
      showToast('Summary ready');
    } catch (err) { setText('sum_output', err, true); showToast('Summarize failed', false); }
    finally { withBusy(btn, false); spinner(false); }
  });

  on('btnSumOCR', 'click', async (e) => {
    const btn = e.currentTarget; withBusy(btn, true); spinner(true);
    setText('sumocr_output', ''); setAudio('sumocr_audio', null);
    try {
      const f = document.getElementById('sumocr_file').files?.[0];
      if (!f) throw 'Please select an image file (jpg/png).';
      const target_lang = document.getElementById('sum_target_lang').value.trim() || 'en';
      const speak = document.getElementById('sum_speak').checked;
      const fd = new FormData(); fd.append('file', f);
      const url = `${getAPI()}/summarize/ocr?target_lang=${encodeURIComponent(target_lang)}&speak=${speak}`;
      const json = await fetchForm(url, fd);
      const out = (json && (json.summary || json.translated)) ? (json.translated || json.summary) : JSON.stringify(json, null, 2)
      setText('sumocr_output', out);
      if (json.tts_url) setAudio('sumocr_audio', json.tts_url);
      showToast('OCR summary ready');
    } catch (err) { setText('sumocr_output', err, true); showToast('OCR summarize failed', false); }
    finally { withBusy(btn, false); spinner(false); }
  });
});
