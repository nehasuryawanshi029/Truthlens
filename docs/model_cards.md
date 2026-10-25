# TRUTHLENS Model Cards

### Model 1: Perceptual Visual Embedder
- **Algorithm**: Difference Hash (dHash) & Spatial RGB Distribution Vectors
- **Target Task**: Image near-duplicate and historical reuse detection
- **Input**: RGB / Grayscale Image (Any dimension)
- **Output**: 64-bit hexadecimal descriptor + 3-channel tone centroid
- **Latency**: ~12ms (Intel Core / AMD Ryzen CPU)
- **Strengths**: Robust against JPEG compression, small crops, slight color shifts, and social platform downscaling.
- **Limitations**: Cannot determine conceptual semantic similarity between two distinct photographs of the same physical monument.

---

### Model 2: Hybrid Lexical-Semantic Retriever
- **Algorithm**: TF-IDF (1-2 N-grams) with Named Entity Co-occurrence Overlap
- **Target Task**: Grounded fact-check passage matching
- **Input**: Tokenized claim assertion + Corpus documents
- **Output**: Ranked list of evidence items with relevance cosine scores
- **Latency**: ~18ms
- **Strengths**: Deterministic, 100% auditable, zero hallucination.
- **Limitations**: Requires lexical overlap; sensitive to synonyms unless augmented with dense vectors.

---

### Model 3: Deconstructive Epistemic Verifier
- **Algorithm**: Multi-Signal Logic Synthesizer
- **Target Task**: Epistemic state assignment (`supported`, `contradicted`, `insufficient_evidence`, `conflicting`)
- **Inputs**: Temporal delta, location match, evidence relationships, authenticity signals.
- **Latency**: ~5ms
- **Strengths**: Strictly separates image provenance from caption assertions; enforces explicit abstention.
