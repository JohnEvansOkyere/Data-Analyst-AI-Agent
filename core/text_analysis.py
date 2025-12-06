"""
Text Analysis and NLP Module
Provides comprehensive text analysis and natural language processing capabilities.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
import re
from collections import Counter
import warnings
warnings.filterwarnings('ignore')


class TextAnalyzer:
    """
    Comprehensive text analysis and NLP toolkit.
    """

    def __init__(self):
        self.stop_words = None
        self.vectorizer = None
        self.sentiment_analyzer = None

    def basic_text_statistics(
        self,
        df: pd.DataFrame,
        text_column: str
    ) -> Dict[str, Any]:
        """
        Calculate basic text statistics.

        Args:
            df: Input DataFrame
            text_column: Name of text column

        Returns:
            Text statistics
        """
        texts = df[text_column].astype(str).fillna('')

        # Calculate statistics
        word_counts = texts.apply(lambda x: len(x.split()))
        char_counts = texts.apply(len)
        sentence_counts = texts.apply(lambda x: len(re.split(r'[.!?]+', x)))

        stats = {
            'total_documents': len(texts),
            'total_words': int(word_counts.sum()),
            'total_characters': int(char_counts.sum()),
            'avg_words_per_doc': float(word_counts.mean()),
            'avg_chars_per_doc': float(char_counts.mean()),
            'avg_sentences_per_doc': float(sentence_counts.mean()),
            'min_words': int(word_counts.min()),
            'max_words': int(word_counts.max()),
            'word_count_distribution': {
                'mean': float(word_counts.mean()),
                'std': float(word_counts.std()),
                'median': float(word_counts.median()),
                'q25': float(word_counts.quantile(0.25)),
                'q75': float(word_counts.quantile(0.75))
            }
        }

        # Empty documents
        empty_docs = (word_counts == 0).sum()
        stats['empty_documents'] = int(empty_docs)
        stats['empty_pct'] = float(empty_docs / len(texts) * 100)

        return stats

    def word_frequency_analysis(
        self,
        df: pd.DataFrame,
        text_column: str,
        top_n: int = 20,
        remove_stopwords: bool = True,
        min_word_length: int = 2
    ) -> Dict[str, Any]:
        """
        Analyze word frequencies.

        Args:
            df: Input DataFrame
            text_column: Name of text column
            top_n: Number of top words to return
            remove_stopwords: Whether to remove stop words
            min_word_length: Minimum word length

        Returns:
            Word frequency analysis
        """
        texts = df[text_column].astype(str).fillna('')

        # Load stop words if needed
        if remove_stopwords:
            try:
                import nltk
                try:
                    from nltk.corpus import stopwords
                    self.stop_words = set(stopwords.words('english'))
                except:
                    nltk.download('stopwords', quiet=True)
                    from nltk.corpus import stopwords
                    self.stop_words = set(stopwords.words('english'))
            except:
                # Fallback to basic stopwords
                self.stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                                   'of', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
                                   'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
                                   'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he',
                                   'she', 'it', 'we', 'they', 'what', 'which', 'who', 'when', 'where',
                                   'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most',
                                   'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
                                   'so', 'than', 'too', 'very', 'just'}

        # Extract all words
        all_words = []
        for text in texts:
            words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
            words = [w for w in words if len(w) >= min_word_length]
            if remove_stopwords and self.stop_words:
                words = [w for w in words if w not in self.stop_words]
            all_words.extend(words)

        # Count frequencies
        word_freq = Counter(all_words)
        top_words = word_freq.most_common(top_n)

        return {
            'total_unique_words': len(word_freq),
            'total_word_occurrences': len(all_words),
            'top_words': [{'word': word, 'count': count, 'frequency': count/len(all_words)}
                         for word, count in top_words],
            'vocabulary_richness': len(word_freq) / len(all_words) if len(all_words) > 0 else 0
        }

    def sentiment_analysis(
        self,
        df: pd.DataFrame,
        text_column: str,
        method: str = 'vader'
    ) -> Dict[str, Any]:
        """
        Perform sentiment analysis.

        Args:
            df: Input DataFrame
            text_column: Name of text column
            method: 'vader' or 'textblob'

        Returns:
            Sentiment analysis results
        """
        texts = df[text_column].astype(str).fillna('')

        if method == 'vader':
            try:
                from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
                analyzer = SentimentIntensityAnalyzer()

                sentiments = []
                for text in texts:
                    scores = analyzer.polarity_scores(text)
                    sentiments.append({
                        'compound': scores['compound'],
                        'positive': scores['pos'],
                        'negative': scores['neg'],
                        'neutral': scores['neu'],
                        'label': 'positive' if scores['compound'] > 0.05 else ('negative' if scores['compound'] < -0.05 else 'neutral')
                    })

                # Create results DataFrame
                sentiment_df = pd.DataFrame(sentiments)

                # Calculate distribution
                label_counts = sentiment_df['label'].value_counts().to_dict()

                return {
                    'method': 'VADER',
                    'sentiments': sentiments,
                    'distribution': label_counts,
                    'avg_compound': float(sentiment_df['compound'].mean()),
                    'avg_positive': float(sentiment_df['positive'].mean()),
                    'avg_negative': float(sentiment_df['negative'].mean()),
                    'avg_neutral': float(sentiment_df['neutral'].mean())
                }

            except ImportError:
                return {
                    'error': 'vaderSentiment not installed. Install with: pip install vaderSentiment',
                    'install_command': 'pip install vaderSentiment'
                }

        elif method == 'textblob':
            try:
                from textblob import TextBlob

                sentiments = []
                for text in texts:
                    blob = TextBlob(text)
                    polarity = blob.sentiment.polarity
                    subjectivity = blob.sentiment.subjectivity

                    sentiments.append({
                        'polarity': polarity,
                        'subjectivity': subjectivity,
                        'label': 'positive' if polarity > 0.1 else ('negative' if polarity < -0.1 else 'neutral')
                    })

                # Create results DataFrame
                sentiment_df = pd.DataFrame(sentiments)

                # Calculate distribution
                label_counts = sentiment_df['label'].value_counts().to_dict()

                return {
                    'method': 'TextBlob',
                    'sentiments': sentiments,
                    'distribution': label_counts,
                    'avg_polarity': float(sentiment_df['polarity'].mean()),
                    'avg_subjectivity': float(sentiment_df['subjectivity'].mean())
                }

            except ImportError:
                return {
                    'error': 'textblob not installed. Install with: pip install textblob',
                    'install_command': 'pip install textblob'
                }

        else:
            return {'error': f'Unknown sentiment analysis method: {method}'}

    def tokenization(
        self,
        df: pd.DataFrame,
        text_column: str,
        method: str = 'word'
    ) -> Dict[str, Any]:
        """
        Tokenize text.

        Args:
            df: Input DataFrame
            text_column: Name of text column
            method: 'word' or 'sentence'

        Returns:
            Tokenization results
        """
        texts = df[text_column].astype(str).fillna('')

        try:
            import nltk
            try:
                if method == 'word':
                    from nltk.tokenize import word_tokenize
                    tokens = [word_tokenize(text) for text in texts]
                else:
                    from nltk.tokenize import sent_tokenize
                    tokens = [sent_tokenize(text) for text in texts]
            except:
                nltk.download('punkt', quiet=True)
                if method == 'word':
                    from nltk.tokenize import word_tokenize
                    tokens = [word_tokenize(text) for text in texts]
                else:
                    from nltk.tokenize import sent_tokenize
                    tokens = [sent_tokenize(text) for text in texts]

            # Calculate statistics
            token_counts = [len(t) for t in tokens]

            return {
                'method': method,
                'total_documents': len(tokens),
                'total_tokens': sum(token_counts),
                'avg_tokens_per_doc': np.mean(token_counts),
                'min_tokens': min(token_counts),
                'max_tokens': max(token_counts),
                'tokens': tokens[:100]  # Return first 100 for preview
            }

        except ImportError:
            return {
                'error': 'nltk not installed. Install with: pip install nltk',
                'install_command': 'pip install nltk'
            }

    def ngram_analysis(
        self,
        df: pd.DataFrame,
        text_column: str,
        n: int = 2,
        top_n: int = 20,
        remove_stopwords: bool = True
    ) -> Dict[str, Any]:
        """
        Extract and analyze n-grams.

        Args:
            df: Input DataFrame
            text_column: Name of text column
            n: N-gram size (2 for bigrams, 3 for trigrams, etc.)
            top_n: Number of top n-grams to return
            remove_stopwords: Whether to remove stop words

        Returns:
            N-gram analysis
        """
        texts = df[text_column].astype(str).fillna('')

        # Load stop words if needed
        if remove_stopwords and self.stop_words is None:
            try:
                from nltk.corpus import stopwords
                self.stop_words = set(stopwords.words('english'))
            except:
                self.stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at'}

        # Extract n-grams
        all_ngrams = []
        for text in texts:
            words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
            if remove_stopwords and self.stop_words:
                words = [w for w in words if w not in self.stop_words]

            # Create n-grams
            ngrams = [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]
            all_ngrams.extend(ngrams)

        # Count frequencies
        ngram_freq = Counter(all_ngrams)
        top_ngrams = ngram_freq.most_common(top_n)

        ngram_name = {1: 'unigram', 2: 'bigram', 3: 'trigram', 4: 'quadgram', 5: 'pentagram'}.get(n, f'{n}-gram')

        return {
            'n': n,
            'ngram_type': ngram_name,
            'total_unique_ngrams': len(ngram_freq),
            'total_ngram_occurrences': len(all_ngrams),
            f'top_{ngram_name}s': [{'ngram': ngram, 'count': count, 'frequency': count/len(all_ngrams)}
                                   for ngram, count in top_ngrams]
        }

    def tfidf_analysis(
        self,
        df: pd.DataFrame,
        text_column: str,
        max_features: int = 100,
        ngram_range: Tuple[int, int] = (1, 1)
    ) -> Dict[str, Any]:
        """
        TF-IDF (Term Frequency-Inverse Document Frequency) analysis.

        Args:
            df: Input DataFrame
            text_column: Name of text column
            max_features: Maximum number of features
            ngram_range: N-gram range (e.g., (1, 2) for unigrams and bigrams)

        Returns:
            TF-IDF analysis results
        """
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer

            texts = df[text_column].astype(str).fillna('')

            # Create TF-IDF vectorizer
            vectorizer = TfidfVectorizer(
                max_features=max_features,
                ngram_range=ngram_range,
                stop_words='english'
            )

            # Fit and transform
            tfidf_matrix = vectorizer.fit_transform(texts)
            self.vectorizer = vectorizer

            # Get feature names
            feature_names = vectorizer.get_feature_names_out()

            # Calculate average TF-IDF scores
            avg_tfidf = tfidf_matrix.mean(axis=0).A1
            feature_scores = sorted(zip(feature_names, avg_tfidf), key=lambda x: x[1], reverse=True)

            # Create document-term matrix
            tfidf_df = pd.DataFrame(
                tfidf_matrix.toarray(),
                columns=feature_names
            )

            return {
                'n_documents': len(texts),
                'n_features': len(feature_names),
                'ngram_range': ngram_range,
                'top_features': [{'feature': feat, 'avg_tfidf': float(score)}
                                for feat, score in feature_scores[:20]],
                'tfidf_matrix': tfidf_df,
                'vocabulary_size': len(vectorizer.vocabulary_)
            }

        except ImportError:
            return {
                'error': 'scikit-learn not installed (should be available)',
                'install_command': 'pip install scikit-learn'
            }

    def named_entity_recognition(
        self,
        df: pd.DataFrame,
        text_column: str,
        top_n: int = 20
    ) -> Dict[str, Any]:
        """
        Named Entity Recognition (NER).
        Note: Requires spacy.

        Args:
            df: Input DataFrame
            text_column: Name of text column
            top_n: Number of top entities to return per type

        Returns:
            NER results
        """
        try:
            import spacy

            # Load model
            try:
                nlp = spacy.load('en_core_web_sm')
            except:
                return {
                    'error': 'spaCy model not found. Install with: python -m spacy download en_core_web_sm',
                    'install_command': 'python -m spacy download en_core_web_sm'
                }

            texts = df[text_column].astype(str).fillna('')

            # Extract entities
            all_entities = []
            entity_counts = {}

            for text in texts[:1000]:  # Limit to first 1000 for performance
                doc = nlp(text)
                for ent in doc.ents:
                    all_entities.append({
                        'text': ent.text,
                        'label': ent.label_,
                        'start': ent.start_char,
                        'end': ent.end_char
                    })

                    # Count entities by type
                    if ent.label_ not in entity_counts:
                        entity_counts[ent.label_] = Counter()
                    entity_counts[ent.label_][ent.text] += 1

            # Get top entities per type
            top_entities_by_type = {}
            for entity_type, counter in entity_counts.items():
                top_entities_by_type[entity_type] = [
                    {'entity': entity, 'count': count}
                    for entity, count in counter.most_common(top_n)
                ]

            return {
                'total_entities': len(all_entities),
                'entity_types': list(entity_counts.keys()),
                'entities_by_type': {k: len(v) for k, v in entity_counts.items()},
                'top_entities_by_type': top_entities_by_type,
                'sample_entities': all_entities[:100]
            }

        except ImportError:
            return {
                'error': 'spaCy not installed. Install with: pip install spacy',
                'install_command': 'pip install spacy && python -m spacy download en_core_web_sm'
            }

    def text_similarity(
        self,
        text1: str,
        text2: str,
        method: str = 'cosine'
    ) -> Dict[str, Any]:
        """
        Calculate text similarity.

        Args:
            text1: First text
            text2: Second text
            method: 'cosine', 'jaccard', or 'levenshtein'

        Returns:
            Similarity score
        """
        if method == 'cosine':
            try:
                from sklearn.feature_extraction.text import TfidfVectorizer
                from sklearn.metrics.pairwise import cosine_similarity

                vectorizer = TfidfVectorizer()
                tfidf = vectorizer.fit_transform([text1, text2])
                similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]

                return {
                    'method': 'cosine',
                    'similarity': float(similarity),
                    'interpretation': 'Identical' if similarity > 0.9 else ('Very similar' if similarity > 0.7 else ('Similar' if similarity > 0.5 else 'Different'))
                }
            except:
                return {'error': 'Could not calculate cosine similarity'}

        elif method == 'jaccard':
            # Jaccard similarity
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())

            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))

            similarity = intersection / union if union > 0 else 0

            return {
                'method': 'jaccard',
                'similarity': float(similarity),
                'interpretation': 'Identical' if similarity > 0.9 else ('Very similar' if similarity > 0.7 else ('Similar' if similarity > 0.5 else 'Different'))
            }

        elif method == 'levenshtein':
            try:
                from Levenshtein import distance

                dist = distance(text1, text2)
                max_len = max(len(text1), len(text2))
                similarity = 1 - (dist / max_len) if max_len > 0 else 0

                return {
                    'method': 'levenshtein',
                    'distance': dist,
                    'similarity': float(similarity),
                    'interpretation': 'Identical' if similarity > 0.9 else ('Very similar' if similarity > 0.7 else ('Similar' if similarity > 0.5 else 'Different'))
                }
            except ImportError:
                return {
                    'error': 'python-Levenshtein not installed. Install with: pip install python-Levenshtein',
                    'install_command': 'pip install python-Levenshtein'
                }

        return {'error': f'Unknown similarity method: {method}'}

    def text_classification_features(
        self,
        df: pd.DataFrame,
        text_column: str,
        max_features: int = 500
    ) -> pd.DataFrame:
        """
        Extract features for text classification.

        Args:
            df: Input DataFrame
            text_column: Name of text column
            max_features: Maximum number of features

        Returns:
            DataFrame with text features
        """
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer

            texts = df[text_column].astype(str).fillna('')

            # TF-IDF features
            vectorizer = TfidfVectorizer(max_features=max_features, stop_words='english')
            tfidf_features = vectorizer.fit_transform(texts).toarray()

            # Create feature DataFrame
            feature_names = [f'tfidf_{i}' for i in range(tfidf_features.shape[1])]
            features_df = pd.DataFrame(tfidf_features, columns=feature_names, index=df.index)

            # Add basic text statistics
            features_df['word_count'] = texts.apply(lambda x: len(x.split()))
            features_df['char_count'] = texts.apply(len)
            features_df['avg_word_length'] = texts.apply(lambda x: np.mean([len(w) for w in x.split()]) if len(x.split()) > 0 else 0)
            features_df['sentence_count'] = texts.apply(lambda x: len(re.split(r'[.!?]+', x)))

            self.vectorizer = vectorizer

            return features_df

        except Exception as e:
            return pd.DataFrame({'error': [str(e)]})
