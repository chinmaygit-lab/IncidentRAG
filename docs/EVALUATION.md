# Evaluation

The included benchmark contains 60 synthetic queries: 40 answerable queries across ten services and 20 deliberate no-answer queries.

Metrics:

- Recall@K: fraction of relevant documents retrieved in the top K.
- MRR: reciprocal rank of the first relevant document.
- nDCG@K: rank-sensitive relevance quality.
- Hit@1: whether the first unique document is relevant.
- No-answer accuracy: fraction of no-answer queries rejected by the calibrated threshold.
- Answerable acceptance: fraction of answerable queries above the calibrated threshold.
- Balanced abstention accuracy: average of answerable acceptance and no-answer rejection.

The calibration routine maximizes balanced accuracy on labeled top scores. This is useful for regression testing, but a production threshold must be calibrated on a held-out representative set to avoid overfitting.

Never present perfect scores on this sample benchmark as evidence of real-world production quality. The sample data is intentionally compact, synthetic, and well-separated.
