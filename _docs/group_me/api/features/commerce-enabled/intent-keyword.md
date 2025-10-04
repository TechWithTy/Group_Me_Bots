Goals & Role in Pipeline

Purpose: Before invoking the LLM, filter messages to find ones with high intent (e.g. commerce, support, FAQ) so you don’t waste compute or cause spam-like noise.

Responsibilities:

Keyword / pattern matching layer (fast, rule-based)

Lightweight classifier / model for intent categories

Combined scoring → decide whether to forward to LLM

Optionally, extract slots / entities (e.g. “product name”, “price”, “how many”) for downstream action

Integration point (in pipeline):

Incoming GroupMe message → Preprocessor → Intent / Keyword Detector → (if high-intent) → LLM / Bot Response


If not high intent, message is handled by legacy logic (moderation, command handlers, or ignored).

Intent / Keyword Detection Architecture
Components

Preprocessing / Normalization

Clean up text (lowercase, punctuation removal, normalization of spacing)

Tokenization

Possibly lemmatization / stemming

Remove or mask user mentions, URLs (or replace with placeholder)

Keyword / Pattern Matching Layer (Rule-based)

Maintain a dictionary or ruleset of high-interest keywords / phrases (e.g. “buy”, “order”, “price”, “ship to”, “how much”, “do you sell”, “where can I get”)

Use regex or pattern lists for variants (e.g. /how much.*\?/, \b(buy|order|get)\b)

If a keyword matches, assign a base score and potential intent tag(s)

Intent Classifier / Model

A model that classifies message text (with optional context features) into one of several intent labels, with a confidence score

Intent labels (example): buy_request, product_info, faq, support_request, chitchat, other

Optionally, include a “no_intent / none” label

Slot / Entity Extractor (optional / future)

Once intent is detected (e.g. buy_request), run an entity extractor to parse product name, variant, quantity, location, etc.

This helps the LLM or commerce module skip asking trivial clarifying questions

Scoring & Decision Logic

Combine rule/keyword score and classifier confidence (e.g. weighted sum)

Possibly factor in metadata: user role, history, threshold per group

If combined score ≥ threshold → mark message as high-intent and forward

Feedback / Learning Loop

Log decisions: whether forwarded, how the LLM responded, whether user accepted reply

For false positives / negatives, feed data back into training set

Periodic retraining or online learning

Model Design & Training
Intent Classifier Model
Input features

Text embedding (e.g. via pretrained model: BERT, DistilBERT, etc.)

Possibly features: presence of numbers, currency symbols, punctuation ?, keyword matches

(Optionally) context / previous messages embeddings

Architecture ideas

A small transformer (e.g. DistilBERT) + classification head

Or lighter-weight model: CNN / LSTM / feed-forward on embeddings

You can adopt joint models where intent + slot extraction are learned together (e.g. joint intent detection & slot filling models) 
arXiv

Or use Siamese / lightweight models like LIDSNet for edge / faster inference 
arXiv

Output

Intent category (e.g. buy_request)

Confidence score (0.0 to 1.0)

(Optionally) slot extractions

Training

Label dataset with messages and correct intents

Split into train / validation / test

Use cross-entropy, track metrics (accuracy, precision, recall, F1)

Monitor confusion (e.g. misclassifying faq vs support)

Retrain periodically as usage evolves

Keyword / Pattern Layer

Maintain lists of keyword → intent mappings

Optionally, patterns weighted by strength

Fast lookup (trie, prefix trees, regex)

Scoring & Thresholds

Let KeywordScore be the strength from rule layer (e.g. 0 to 1)

Let ModelConf be confidence from classifier

CombinedScore = w1 * KeywordScore + w2 * ModelConf

Choose weights w1, w2 (e.g. 0.5 / 0.5) or tune per group

Each group / room may have its own threshold (to be more or less aggressive)

If CombinedScore ≥ threshold → forward to LLM

You can calibrate threshold so false positives / noise are low.

Example Workflow with Intent Detector

Let’s walk a sample:

Incoming message: "Hey Gort, can you tell me the price of your plugin?"

Preprocess → normalized text

Keyword layer sees “price”, “tell me” → KeywordScore = 0.7, intents candidate = product_info / buy_request

Classifier ingests the text → outputs buy_request with confidence 0.85

CombinedScore = 0.5×0.7 + 0.5×0.85 = 0.775

Threshold for group = 0.7 → this crosses → mark as high-intent

Extract slot: “plugin”

Forward to LLM / commerce module with intent + slot

LLM uses prompt (with context & product catalog) to respond with price info or “Buy it here” link

If another message: "Cool weather today" → keyword match low, classifier chitchat with confidence 0.4, combined score low → skip LLM.

Metrics, Monitoring & Feedback Loop

Track and monitor:

False positives: messages sent to LLM that shouldn’t have

False negatives: real user purchase / request messages not forwarded

Precision / recall for each intent label

How many LLM calls per group / per day (for cost control)

User acceptance rate: fraction of auto replies that the user engages with

Retraining frequency, drift in language usage

Allow group admins to override, turn off auto-intent detection, or adjust sensitivity / threshold.