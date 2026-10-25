# Responsible AI Principles & Ethical Guardrails

TRUTHLENS enforces 15 non-negotiable rules for ethical and responsible AI in visual misinformation research:

1. **Zero Source Fabrication**: Every citation, URL, and publisher link in TRUTHLENS corresponds to real archival records or configured web results. The platform never hallucinates articles or fake journalists.
2. **Explicit Verification Decoupling**: Visual authenticity and text claim veracity are treated as distinct questions.
3. **Transparent Uncertainty**: The platform explicitly states when evidence is mixed or insufficient.
4. **Never Equate Absence with Falsity**: A lack of indexed articles does not make a local event fraudulent.
5. **Privacy by Default**: EXIF GPS coordinates are generalized and redacted in public views.
6. **No Unannounced Cloud Telemetry**: Uploads stay on local storage; no external APIs are pinged without explicit configuration.
7. **Clean Image Sanitization**: Users can download privacy-scrubbed copies of their images with metadata permanently removed.
8. **Calibrated Confidence**: Confidence levels represent verifiable source corroboration, not probabilistic model guesses.
9. **Accessible Evaluation**: Researchers can inspect the 2D PCA embedding space and empirical benchmark metrics directly in the Research Lab.
10. **Explainable Rejection**: Whenever a claim is flagged as contradicted, the specific geographic or temporal discrepancy is cited.
