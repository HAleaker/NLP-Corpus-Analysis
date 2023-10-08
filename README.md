# NLP Corpus Analysis (alpha stage)

This docker image is based on tools like spaCy, Textacy, pyLDAvis & others to analyse a text corpus, such as the collection of all published documents or any other CSV file with a text column.

It provides a range of Machine Learning and Natural Language Processing algorithms that can be executed over a corpus or its subset.

The project aims to provide these methods over a REST API when feasible.

## Current features

### Compose a text transformation pipeline to prepare a corpus

Upload a CSV file, then click "Create a corpus" to access the pipeline composition page.

### Create and visualise topic models via pyLDAvis.

[Topic Modeling](https://en.wikipedia.org/wiki/Topic_model) technique is use