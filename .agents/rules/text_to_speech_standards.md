# Text-to-Speech (TTS) & Acoustic Engineering Standards

This standard governs all text-to-speech voice synthesis, phonetic transliteration (G2P), multilingual Indic speech processing, and audio mastering executed by agents in this repository. All voice synthesis operations must run locally at **$0 cloud token costs**.

---

## 1. Acoustic Engineering & Mastering Specifications

- **Sample Rate Standards**:
  - **24,000 Hz (24 kHz)**: Primary native sample rate for Kokoro-82M neural synthesis and conversational speech.
  - **48,000 Hz (48 kHz)**: Broadcast and NLE video conform (resampled via high-quality polyphase Sinc filter for Final Cut Pro and DaVinci Resolve).
- **Bit Depth & Channels**:
  - Format: 16-bit linear PCM uncompressed WAV (`audio/wav`) or broadcast MP3 (192–320 kbps CBR).
  - Channel Layout: Single-channel **Mono** for speech. Speech tracks must never be authored in stereo with artificial phase differences, which causes comb filtering when summed to mono on mobile devices.
- **Loudness Normalization Standards**:
  - **Speech / Podcasts / Outbound Audio**: Integrated loudness target **-16.0 LUFS** (tolerance $\pm 1.0\text{ LUFS}$).
  - **Video Voiceover / Narration Sync**: Integrated loudness target **-14.0 LUFS** (matching YouTube/Vimeo streaming standards).
  - **True Peak**: Maximum **-1.0 dBFS** to prevent inter-sample clipping during lossy compression.

---

## 2. Phonetic Normalization & G2P (Phonon) Standards

- **Pre-Synthesis Text Normalization**: Raw text must pass through normalization before vocoder input:
  - *Currencies*: `₹5,000` $\to$ `"five thousand rupees"`, `$150` $\to$ `"one hundred and fifty dollars"`.
  - *Technical Acronyms*: `API` $\to$ `"A-P-I"`, `JWT` $\to$ `"J-W-T"`, `OAuth` $\to$ `"O-Auth"`, `SQL` $\to$ `"S-Q-L" or "Sequel"`.
  - *Numbers & Quantities*: `250ms` $\to$ `"two hundred and fifty milliseconds"`, `3.5x` $\to$ `"three point five times"`.
- **IPA Transcription & Stress Markers**:
  - Use International Phonetic Alphabet (IPA) strings to guide neural duration and pitch models.
  - Insert primary stress (`ˈ`) and secondary stress (`ˌ`) to ensure natural rhythm and prevent robotic flat cadence.
  - Disambiguate heteronyms based on part-of-speech context (e.g., *project* noun /ˈprɒdʒɛkt/ vs verb /prəˈdʒɛkt/).

---

## 3. AI4Bharat Indic Language Phonetic Standards

- **Akshara Syllable Segmentation**:
  - Indic scripts (Devanagari, Tamil, Telugu, Kannada, Malayalam, Bengali, Gujarati, Gurmukhi) must be parsed into akshara units (V, CV, CCV) preserving conjunct consonants (*samyuktaksharas*).
- **Indo-Aryan Schwa Deletion Rule**:
  - For Hindi (`hi`), Marathi (`mr`), and Punjabi (`pa`), the inherent schwa vowel /ə/ must be deleted in:
    1. Word-final position: e.g., Hindi राम is /raːm/, not /raːmə/.
    2. Medial syllables when preceded by a long syllable or followed by a suffix (e.g., समझना is /səmədʒʱnaː/, not /səmədʒʱənaː/).
- **Dravidian Acoustic Fidelity**:
  - Preserve retroflex consonants (*ṭ*, *ḍ*, *ṇ*, *ḷ*) and the retroflex approximant (*zh* /ɻ/ in Tamil and Malayalam).
  - Enforce geminate consonant length (e.g., Tamil *pattu* vs *patu*).

---

## 4. Zero Cloud Token & Local Hardware Invariant

- **Prohibition of Cloud Voice Subscriptions**: Hardcoding or invoking paid external cloud voice APIs (ElevenLabs, OpenAI Speech API, Google Cloud TTS, Azure Speech) is strictly prohibited. All voice generation must execute locally on CPU or Apple Silicon Metal.
- **Model Efficiency & Footprint**:
  - Primary general voice model: **Kokoro-82M** (82 million parameters, <350MB memory footprint).
  - Indic multilingual voice model: **AI4Bharat IndicTTS** (FastPitch / VITS ONNX weights).
  - Synthesis speed must exceed $5\times$ real-time on Apple Silicon (M1/M2/M3/M4) and $2\times$ on modern x86_64 CPUs.
